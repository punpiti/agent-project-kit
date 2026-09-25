#!/usr/bin/env python3
"""Fail closed when tracked or packaged content crosses the public boundary."""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = json.loads((ROOT / "config" / "release-boundary.json").read_text(encoding="utf-8"))


def public_candidate_files() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=ROOT, check=True, capture_output=True
    )
    return [part.decode("utf-8") for part in result.stdout.split(b"\0") if part]


def untracked_files(root: Path = ROOT) -> list[str]:
    """Return untracked, non-ignored files that a release could omit."""
    result = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard", "-z"],
        cwd=root, check=True, capture_output=True
    )
    return [part.decode("utf-8") for part in result.stdout.split(b"\0") if part]


def has_tracked_changes(root: Path = ROOT, *, staged: bool = False) -> bool:
    command = ["git", "diff", "--quiet"]
    if staged:
        command.insert(2, "--cached")
    return subprocess.run(command, cwd=root).returncode != 0


def runtime_items() -> tuple[str, ...]:
    sys.dont_write_bytecode = True  # importing a sibling must not add __pycache__ to the tree
    path = ROOT / "scripts" / "install-shared.py"
    spec = importlib.util.spec_from_file_location("apk_install_shared", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return tuple(module.INCLUDE)


def is_private_path(name: str) -> bool:
    path = Path(name)
    return (
        any(name.startswith(prefix) for prefix in CONFIG["private_prefixes"])
        or path.name in CONFIG.get("private_names", [])
        or any(path.name.startswith(prefix) for prefix in CONFIG.get("private_name_prefixes", []))
        or any(name.endswith(suffix) for suffix in CONFIG["private_suffixes"])
    )


def history_findings(patterns: list[tuple[str, re.Pattern[str]]]) -> list[str]:
    """Inspect reachable Git history without ever printing matching content."""
    findings: list[str] = []
    names = subprocess.run(
        ["git", "log", "--all", "--name-only", "--pretty=format:"],
        cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.splitlines()
    for name in {line for line in names if line}:
        if is_private_path(name):
            findings.append(f"historical private path: {name}")
    revisions = subprocess.run(
        ["git", "rev-list", "--all"], cwd=ROOT, check=True,
        capture_output=True, text=True
    ).stdout.splitlines()
    if revisions:
        command = ["git", "grep", "-I", "-l", "-P"]
        for _, pattern in patterns:
            command.extend(["-e", pattern.pattern])
        scan = subprocess.run(
            [*command, *revisions, "--"], cwd=ROOT, capture_output=True, text=True
        )
        if scan.returncode not in (0, 1):
            raise subprocess.CalledProcessError(
                scan.returncode, scan.args, output=scan.stdout, stderr=scan.stderr
            )
        for location in scan.stdout.splitlines():
            findings.append(f"historical secret-pattern: {location}")
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--history", action="store_true",
        help="also scan every reachable Git blob; report identifiers, never values",
    )
    parser.add_argument(
        "--release", action="store_true",
        help="also fail when non-ignored untracked files could be omitted from the release",
    )
    args = parser.parse_args()
    errors: list[str] = []
    files = public_candidate_files()
    if args.release:
        for name in untracked_files():
            errors.append(f"untracked release candidate: {name}")
        if has_tracked_changes():
            errors.append("tracked working-tree changes remain")
        if has_tracked_changes(staged=True):
            errors.append("staged but uncommitted changes remain")
    for name in files:
        if is_private_path(name):
            errors.append(f"blocked private path: {name}")
    ignore_rules = {
        line.strip() for line in (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }
    for rule in CONFIG["required_ignore_rules"]:
        if rule not in ignore_rules:
            errors.append(f"missing ignore rule: {rule}")
    actual_runtime = set(runtime_items())
    expected_runtime = set(CONFIG["shared_runtime_items"])
    if actual_runtime != expected_runtime:
        errors.append("shared runtime allowlist differs from config/release-boundary.json")
    secret_patterns = [
        (item["id"], re.compile(item["regex"])) for item in CONFIG["secret_patterns"]
    ]
    current_patterns = [
        ("secret-pattern", rule_id, pattern) for rule_id, pattern in secret_patterns
    ] + [
        ("blocked-content", item["id"], re.compile(item["regex"]))
        for item in CONFIG.get("public_content_patterns", [])
    ]
    for name in files:
        path = ROOT / name
        if not path.is_file():
            continue
        if path.stat().st_size > 2_000_000:
            if args.release:
                errors.append(f"unscanned large release candidate: {name}")
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            if args.release:
                errors.append(f"unscanned non-UTF-8 release candidate: {name}")
            continue
        for finding_type, rule_id, pattern in current_patterns:
            if pattern.search(text):
                errors.append(f"{finding_type} {rule_id}: {name}")
    if args.history:
        errors.extend(history_findings(secret_patterns))
    if errors:
        print("release boundary: FAIL")
        for error in sorted(set(errors)):
            print(f"- {error}")
        return 1
    scopes = []
    if args.release:
        scopes.append("release completeness checked")
    if args.history:
        scopes.append("Git history scanned")
    scope = f"; {'; '.join(scopes)}" if scopes else ""
    print(
        f"release boundary: PASS ({len(files)} public-candidate files{scope}; "
        "no secret values printed)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
