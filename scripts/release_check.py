#!/usr/bin/env python3
"""Run every Agent Project Kit release gate from one read-only command.

The command never bumps versions, commits, tags, pushes, publishes, or refreshes
an installed/shared runtime. It only reports whether the current source is fit
to release and prints the content digest a shared-runtime install would pin.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Files whose "current release" line must name manifest.json's version.
VERSION_LINES = {
    "README.md": r"^Current release: `([^`]+)`",
    "README.th.md": r"^release ปัจจุบัน: `([^`]+)`",
    "index.md": r"^- Current package version: `([^`]+)`",
}

TEST_COMMANDS = (
    ("workflow-architecture", ("python3", "tests/test-workflow-architecture.py")),
    ("v7-context", ("python3", "tests/test-v7-context.py")),
    ("prose-style", ("python3", "tests/test-prose-style.py")),
    ("thai-docx-repair", ("python3", "tests/test-thai-docx-repair.py")),
    ("release-check", ("python3", "tests/test-release-check.py")),
    ("routing-rules", ("python3", "tests/test-routing-rules.py")),
    ("schemas", ("python3", "tests/test-schemas.py")),
    ("fast-start", ("bash", "tests/test-fast-start.sh")),
    ("transactional-update", ("bash", "tests/test-transactional-update.sh")),
    ("shared-runtime", ("bash", "tests/test-shared-runtime.sh")),
    ("shared-runtime-v2", ("bash", "tests/test-shared-runtime-v2.sh")),
    ("benchmark", ("bash", "tests/test-benchmark.sh")),
)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True)


def version_errors(root: Path) -> list[str]:
    """Return every place that disagrees with manifest.json's version."""
    errors: list[str] = []
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    version = manifest.get("version", "")
    if not version:
        return ["manifest.json has no version"]
    if manifest.get("git_ref") != f"v{version}":
        errors.append(f"manifest.json git_ref {manifest.get('git_ref')!r} != 'v{version}'")
    template = json.loads((root / "templates" / "apk.json").read_text(encoding="utf-8"))
    if template.get("version") != version:
        errors.append(f"templates/apk.json version {template.get('version')!r} != {version!r}")
    for name, pattern in VERSION_LINES.items():
        text = (root / name).read_text(encoding="utf-8")
        found = re.search(pattern, text, flags=re.MULTILINE)
        if not found:
            errors.append(f"{name}: current-release line not found")
        elif found.group(1) != version:
            errors.append(f"{name}: names {found.group(1)!r}, manifest is {version!r}")
    changelog = (root / "CHANGELOG.md").read_text(encoding="utf-8")
    if not re.search(rf"^## {re.escape(version)}\b", changelog, flags=re.MULTILINE):
        errors.append(f"CHANGELOG.md has no '## {version}' section")
    unreleased = re.search(r"^## Unreleased\n(.*?)(?=^## )", changelog, flags=re.MULTILINE | re.DOTALL)
    if unreleased and unreleased.group(1).strip():
        errors.append("CHANGELOG.md Unreleased section is not empty; move entries under the version")
    return errors


def tag_errors(root: Path, version: str) -> list[str]:
    """With --tagged: the release tag must exist, be annotated, and peel to HEAD."""
    tag = f"v{version}"
    head = git(root, "rev-parse", "HEAD").stdout.strip()
    kind = git(root, "cat-file", "-t", tag)
    if kind.returncode != 0:
        return [f"tag {tag} does not exist"]
    errors = []
    if kind.stdout.strip() != "tag":
        errors.append(f"tag {tag} is lightweight; release tags must be annotated")
    if git(root, "rev-parse", f"{tag}^{{commit}}").stdout.strip() != head:
        errors.append(f"tag {tag} does not point to HEAD")
    return errors


def run_command(name: str, command: tuple[str, ...]) -> tuple[str, int, str, float]:
    started = time.monotonic()
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    output = (result.stdout + result.stderr).strip()
    return name, result.returncode, output, time.monotonic() - started


def main() -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("--allow-dirty", action="store_true",
                        help="run the gates on an uncommitted tree; the result is never release-ready")
    parser.add_argument("--tagged", action="store_true",
                        help="also require an annotated v<version> tag on HEAD")
    parser.add_argument("--skip-tests", action="store_true",
                        help="skip the acceptance suite (result is never release-ready)")
    parser.add_argument("--skip-history", action="store_true",
                        help="skip the Git-history secret scan (result is never release-ready)")
    parser.add_argument("--jobs", type=int, default=6, help="parallel test workers (default 6)")
    parser.add_argument("--artifact-out", type=Path,
                        help="write the shared-runtime content manifest JSON to this path")
    args = parser.parse_args()

    failures: list[str] = []
    skipped: list[str] = []

    def report(gate: str, errors: list[str]) -> None:
        print(f"[{'FAIL' if errors else 'PASS'}] {gate}")
        for error in errors:
            print(f"       - {error}")
        failures.extend(f"{gate}: {error}" for error in errors)

    version = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8")).get("version", "")
    head = git(ROOT, "rev-parse", "--short", "HEAD").stdout.strip()
    print(f"Agent Project Kit release check — {version} at {head}")

    report("version consistency", version_errors(ROOT))
    if args.tagged:
        report("release tag", tag_errors(ROOT, version))
    else:
        print("[INFO] release tag not checked; rerun with --tagged after tagging")

    for gate, command in (
        ("workflow registry projections", ("python3", "scripts/sync_workflow_registry.py")),
        ("prompt catalog", ("python3", "scripts/validate_prompt_catalog.py")),
    ):
        _, code, output, _ = run_command(gate, command)
        report(gate, [] if code == 0 else [line for line in output.splitlines() if line][-5:] or [f"exit {code}"])

    boundary = ["python3", "scripts/check_release_boundary.py"]
    if not args.allow_dirty:
        boundary.append("--release")
    else:
        skipped.append("clean-tree/untracked completeness (--allow-dirty)")
    if not args.skip_history:
        boundary.append("--history")
    else:
        skipped.append("Git-history secret scan (--skip-history)")
    _, code, output, _ = run_command("release boundary", tuple(boundary))
    report("release boundary", [] if code == 0 else [
        line.removeprefix("- ") for line in output.splitlines() if line.startswith("- ")
    ] or [f"exit {code}"])

    if args.skip_tests:
        skipped.append("acceptance suite (--skip-tests)")
    else:
        with ThreadPoolExecutor(max_workers=max(1, args.jobs)) as pool:
            results = list(pool.map(lambda item: run_command(*item), TEST_COMMANDS))
        for name, code, output, seconds in results:
            gate = f"test {name} ({seconds:.0f}s)"
            tail = [line for line in output.splitlines() if line][-8:]
            report(gate, [] if code == 0 else tail or [f"exit {code}"])

    installer = load_module("apk_install_shared", ROOT / "scripts" / "install-shared.py")
    artifact = installer.source_content_manifest(ROOT)
    artifact = {"package": "agent-project-kit", "version": version, "commit": head, **artifact}
    print(f"[INFO] shared-runtime artifact: {len(artifact['files'])} files, "
          f"content_sha256 {artifact['content_sha256']}")
    if args.artifact_out:
        args.artifact_out.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
        print(f"[INFO] artifact manifest written to {args.artifact_out}")

    print("[INFO] not covered here: native-Windows tests/test-shared-runtime-v2-windows.ps1, "
          "Pages build, GitHub Release, and post-publish updater dry-run")
    for item in skipped:
        print(f"[SKIP] {item}")
    if failures:
        print(f"release check: FAIL ({len(failures)} problem(s)); do not tag or publish")
        return 1
    if skipped:
        print("release check: PASS for the gates run; NOT release-ready because gates were skipped")
        return 0
    print("release check: PASS; ready to tag and publish")
    return 0


if __name__ == "__main__":
    sys.exit(main())
