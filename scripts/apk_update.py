#!/usr/bin/env python3
"""Update Agent Project Kit from Git or from the published GitHub Pages manifest.

scripts/install-from-git.{sh,ps1} and scripts/update-from-pages.{sh,ps1} are
thin wrappers around the two subcommands here:

  apk_update.py from-git   [--dry-run] PROJECT REPO_URL [REF] [CLONE_DIR] [EXPECTED_VERSION]
  apk_update.py from-pages [--dry-run] PROJECT [MANIFEST_URL] [REPO_URL] [REF] [CLONE_DIR]

The checked-out package installs itself with its own installer, so a newer
release can change install behavior. Downgrades and version mismatches fail
closed; a dry run never writes project files.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

DEFAULT_MANIFEST = "https://punpiti.github.io/agent-project-kit/manifest.json"
DEFAULT_REPO = "https://github.com/punpiti/agent-project-kit.git"


class UpdateError(Exception):
    def __init__(self, message: str, code: int = 1):
        super().__init__(message)
        self.code = code


def git(*args: str, check: bool = True, quiet: bool = False) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(["git", *args], text=True,
                            stdout=subprocess.PIPE if quiet else None,
                            stderr=subprocess.PIPE if quiet else None)
    if check and result.returncode != 0:
        raise UpdateError(f"git {' '.join(args)} failed with exit code {result.returncode}")
    return result


def version_line(version_file: Path, label: str) -> str:
    if not version_file.is_file():
        return ""
    prefix = f"- {label}:"
    for line in version_file.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith(prefix):
            return line[len(prefix):].strip()
    return ""


def manifest_value(manifest: dict, key: str) -> str:
    value = manifest.get(key, "")
    return "" if isinstance(value, (dict, list)) or value is None else str(value)


def is_wsl2() -> bool:
    try:
        text = Path("/proc/version").read_text(encoding="utf-8", errors="ignore").lower()
    except OSError:
        return False
    return "microsoft" in text or "wsl" in text


def default_clone_dir(project: Path) -> Path:
    # A Git clone inside a Windows-synced folder is slow and fragile; WSL2
    # projects on /mnt/<drive> use a machine-local cache instead.
    if os.name != "nt" and is_wsl2() and re.match(r"^/mnt/[a-zA-Z]/", str(project)):
        return Path(os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache") / "agent-project-kit"
    return project / ".ai" / "agent-project-kit-source"


def run_clone_installer(clone: Path, project: Path) -> None:
    """Install with the checked-out package's own platform wrapper."""
    if os.name == "nt":
        shell = shutil.which("pwsh") or shutil.which("powershell") or "powershell"
        command = [shell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
                   str(clone / "scripts" / "install-to-project.ps1"), "-ProjectPath", str(project),
                   "-SourcePath", str(clone)]
    else:
        command = ["bash", str(clone / "scripts" / "install-to-project.sh"), str(project), str(clone)]
    result = subprocess.run(command)
    if result.returncode != 0:
        raise UpdateError("Install from the checked-out package failed.", result.returncode)


def from_git(project_arg: str, repo_url: str, ref: str = "", clone_arg: str = "",
             expected_version: str = "", dry_run: bool = False) -> int:
    if not repo_url:
        raise UpdateError("Usage:\n  bash install-from-git.sh [--dry-run] /path/to/project <repo-url> [ref] [clone-dir]\n\n"
                          "Example:\n  bash install-from-git.sh . https://github.com/punpiti/agent-project-kit.git v6.16.0", 2)
    if not shutil.which("git"):
        raise UpdateError("git not found. Install Git first.")
    project = Path(project_arg).resolve()
    ai = project / ".ai"
    ref = ref or "main"
    clone = Path(clone_arg) if clone_arg else default_clone_dir(project)
    dry_root: Path | None = None
    try:
        if dry_run:
            dry_root = Path(tempfile.mkdtemp())
            clone = dry_root / "repository"
        else:
            ai.mkdir(parents=True, exist_ok=True)
        if (clone / ".git").is_dir():
            git("-C", str(clone), "remote", "set-url", "origin", repo_url)
            git("-C", str(clone), "fetch", "--tags", "--prune", "origin")
        else:
            if os.path.lexists(clone):
                raise UpdateError(f"Refusing to overwrite existing non-git clone path: {clone}\n"
                                  "Move or rename it first, or pass a different clone-dir argument.")
            git("clone", repo_url, str(clone))
            git("-C", str(clone), "fetch", "--tags", "--prune", "origin")
        if git("-C", str(clone), "rev-parse", "-q", "--verify", f"refs/tags/{ref}", check=False, quiet=True).returncode == 0:
            git("-C", str(clone), "checkout", "-q", f"tags/{ref}")
        else:
            git("-C", str(clone), "checkout", "-q", ref)
            if git("-C", str(clone), "pull", "--ff-only", "origin", ref, check=False).returncode != 0:
                raise UpdateError(f"Could not fast-forward ref {ref} from origin; refusing a stale or divergent checkout.")
        commit = git("-C", str(clone), "rev-parse", "--short=12", "HEAD", quiet=True).stdout.strip()
        manifest_path = clone / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.is_file() else {}
        checked_out = manifest_value(manifest, "version")
        if expected_version and checked_out != expected_version:
            raise UpdateError(f"Refusing package version mismatch: manifest advertised {expected_version} "
                              f"but ref {ref} contains {checked_out or 'unknown'}.")
        version_file = ai / "COMPUTING_ENVIRONMENT_VERSION.md"
        if dry_run:
            print("Agent Project Kit update dry run")
            print(f"Project: {project}")
            print(f"Repository: {repo_url}")
            print(f"Ref: {ref}")
            print(f"Commit: {commit}")
            print(f"Clone path: {clone}")
            print(f"Snapshot path that would be refreshed: {ai / 'agent-project-kit'}")
            print(f"Current package version: {version_line(version_file, 'Package version') or 'none'}")
            print(f"Target package version: {checked_out or 'unknown'}")
            print(f"Current state schema: {version_line(version_file, 'State schema version') or 'none'}")
            print(f"Target state schema: {manifest_value(manifest, 'state_schema_version') or 'unknown'}")
            print(f"Current machine profile schema: {version_line(version_file, 'Machine profile schema version') or 'none'}")
            print(f"Target machine profile schema: {manifest_value(manifest, 'machine_profile_schema_version') or 'unknown'}")
            print("Project-local state files would be preserved.")
            print("No project files were updated.")
            return 0
        sys.stdout.flush()
        run_clone_installer(clone, project)
        if version_file.is_file():
            with version_file.open("ab") as handle:
                handle.write(f"""
## Git Source

- Source type: git
- Repository: {repo_url}
- Ref: {ref}
- Commit: {commit}
- Clone path: {clone}
""".encode("utf-8"))
        print(f"Agent Project Kit cloned at: {clone}")
        print(f"Installed into project: {project}")
        print(f"Ref: {ref}")
        print(f"Commit: {commit}")
        return 0
    finally:
        if dry_root and dry_root.exists():
            shutil.rmtree(dry_root, ignore_errors=True)


def version_key(raw: str) -> tuple[int, int, int]:
    main = re.sub(r"[^0-9.].*$", "", re.sub(r"^[vV]", "", raw))
    parts = (main.split(".") + ["", "", ""])[:3]
    return tuple(int(part) if part.isdigit() else 0 for part in parts)  # type: ignore[return-value]


def is_newer(current: str, latest: str, current_updated: str, latest_updated: str) -> bool:
    if not latest or current == latest:
        return False
    current_key, latest_key = version_key(current), version_key(latest)
    if latest_key > current_key:
        return True
    if latest_key < current_key:
        return False  # a numerically older version is a downgrade even when its label differs
    # Same numeric version with a different label is accepted only when both
    # timestamps prove that the manifest is newer. Ambiguous cases fail closed.
    return bool(latest_updated and current_updated and latest_updated > current_updated)


def record_check(version_file: Path, latest: str, manifest_url: str) -> None:
    if not version_file.is_file():
        return
    now = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    text = version_file.read_bytes().decode("utf-8", errors="surrogateescape")
    for prefix, value in (("- Last update check:", now), ("- Latest known upstream version:", latest),
                          ("- Update check source:", manifest_url)):
        text = re.sub(rf"(?m)^{re.escape(prefix)}.*$", lambda _m, p=prefix, v=value: f"{p} {v}", text)
    temp = version_file.with_name(f".{version_file.name}.tmp")
    temp.write_bytes(text.encode("utf-8", errors="surrogateescape"))
    os.replace(temp, version_file)


def from_pages(project_arg: str = ".", manifest_url: str = "", repo_url: str = "", ref: str = "",
               clone_arg: str = "", dry_run: bool = False) -> int:
    manifest_url = manifest_url or DEFAULT_MANIFEST
    repo_url = repo_url or DEFAULT_REPO
    project = Path(project_arg).resolve()
    ai = project / ".ai"
    version_file = ai / "COMPUTING_ENVIRONMENT_VERSION.md"
    ai.mkdir(parents=True, exist_ok=True)
    try:
        with urllib.request.urlopen(manifest_url, timeout=60) as response:
            manifest = json.loads(response.read().decode("utf-8"))
    except (OSError, ValueError) as error:
        raise UpdateError(f"Could not read GitHub Pages manifest: {manifest_url}\n"
                          "Usage:\n  bash update-from-pages.sh [--dry-run] /path/to/project [pages-manifest-url] "
                          f"[repo-url] [ref] [clone-dir]\nReason: {error}")
    latest = manifest_value(manifest, "version") or "unknown"
    latest_updated = manifest_value(manifest, "updated")
    current = version_line(version_file, "Package version") or "none"
    current_updated = version_line(version_file, "Package updated")
    ref = ref or manifest_value(manifest, "git_ref") or f"v{latest}"
    print("Agent Project Kit GitHub Pages update check")
    print(f"Project: {project}")
    print(f"Manifest: {manifest_url}")
    print(f"Repository: {repo_url}")
    print(f"Ref: {ref}")
    print(f"Current package version: {current}")
    print(f"Latest package version: {latest}")
    print(f"Current package updated: {current_updated or 'unknown'}")
    print(f"Latest package updated: {latest_updated or 'unknown'}")
    print(f"Current state schema: {version_line(version_file, 'State schema version') or 'none'}")
    print(f"Latest state schema: {manifest_value(manifest, 'state_schema_version') or 'unknown'}")
    print(f"Current machine profile schema: {version_line(version_file, 'Machine profile schema version') or 'none'}")
    print(f"Latest machine profile schema: {manifest_value(manifest, 'machine_profile_schema_version') or 'unknown'}")
    if not is_newer(current, latest, current_updated, latest_updated):
        print("Result: no newer package version found.")
        if not dry_run:
            record_check(version_file, latest, manifest_url)
        return 0
    print("Result: newer or different package version found.")
    print("Project-local state files will be preserved by install-from-git.")
    sys.stdout.flush()
    code = from_git(str(project), repo_url, ref, clone_arg, latest, dry_run=dry_run)
    if not dry_run:
        record_check(version_file, latest, manifest_url)
    return code


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    sys.dont_write_bytecode = True
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    if not args or args[0] not in {"from-git", "from-pages"}:
        print(__doc__, file=sys.stderr)
        return 2
    command, rest = args[0], args[1:]
    dry_run = bool(rest) and rest[0] == "--dry-run"
    if dry_run:
        rest = rest[1:]
    try:
        if command == "from-git":
            positional = (rest + [""] * 5)[:5]
            return from_git(positional[0] or ".", *positional[1:], dry_run=dry_run)
        positional = (rest + [""] * 5)[:5]
        return from_pages(positional[0] or ".", *positional[1:], dry_run=dry_run)
    except UpdateError as error:
        print(error, file=sys.stderr)
        return error.code


if __name__ == "__main__":
    sys.exit(main())
