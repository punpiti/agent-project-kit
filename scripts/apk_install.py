#!/usr/bin/env python3
"""Install or update Agent Project Kit in a project (the single installer core).

scripts/install-to-project.sh and scripts/install-to-project.ps1 are thin
wrappers around this file. Behavior contract:

- Project-local `.ai/` state is never overwritten; missing templates are added.
- The package snapshot is staged, SHA-256 verified, then swapped in; the old
  snapshot becomes `.ai/agent-project-kit.previous`. Any failure restores the
  previous snapshot and every control file (version metadata, SESSION_LOG.md,
  AGENTS.md, CLAUDE.md, ANTIGRAVITY.md).
- Existing paths that do not look like kit content stop the install before
  anything is written.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import socket
import stat
import sys
import tempfile
import time
from pathlib import Path

ITEMS = (
    "manifest.json", "PACKAGE_CONTENTS.md", "CHANGELOG.md", "README.md", "README.th.md",
    "UPDATE_EXISTING_PROJECT.md", "INSTALL_IN_PROJECT.md", "index.md", "GIT_DISTRIBUTION.md",
    "OPEN_WITH_AGENT.md", "MARKDOWN_OVER_ARCHIVE_RECOVERY.md", "START_HERE.md",
    "SPEC_EVAL_LOOP_INSTRUCTION.md", "AGENTS.md", "CLAUDE.md", "ANTIGRAVITY.md", "AI_CLIENTS.md",
    "MACHINE_PROFILES.md", "TOKEN_DISCIPLINE.md", "DOCUMENT_PRODUCTION_POLICY.md",
    "MARKDOWN_ORGANIZATION_POLICY.md", "SECURITY_EXCLUSIONS.md", "MIGRATION_FROM_OLD.md",
    "ENVIRONMENT_POLICY.md", "GLOBAL_START_PROMPT.md", "STARTUP.md", "SHARED_RUNTIME_EXPERIMENT.md",
    "bootstrap_ai_project.py", "prompts", "templates", "checklists", "config", "environments", "scripts",
)
TEMPLATES = (
    "PROJECT_STATE.md", "PROJECT_HIERARCHY.md", "MACHINE_PROFILE.md", "LOCAL_RESOURCES.md",
    "MACHINE_COMPATIBILITY.md", "RUNBOOK.md", "TOKEN_BUDGET.md", "SESSION_LOG.md",
    "ENVIRONMENT_VARIABLES.md", "DOCUMENT_PIPELINE.md", "DOCUMENT_STYLE.md", "DOCUMENT_QA.md",
    "MARKDOWN_INVENTORY.md", "project.json", "state.json", "local-resources.json",
)
BEGIN = "<!-- BEGIN COMPUTING-ENVIRONMENT -->"
END = "<!-- END COMPUTING-ENVIRONMENT -->"
ADAPTER = "<!-- BEGIN AGENT-PROJECT-KIT-ADAPTER -->"
INSTALL_LOG_MARKER = "Agent Project Kit installation first recorded"
KIT_NAME = re.compile(r'"name"\s*:\s*"(agent-project-kit|computing-environment)"')
KIT_METADATA = re.compile(r"Agent Project Kit|agent-project-kit|computing-environment|"
                          r"Computing environment source|Agent Project Kit source", re.IGNORECASE)
# Windows reparse tags that are real links. OneDrive online-only files are
# reparse points too (cloud tags) and must still be packaged.
LINK_REPARSE_TAGS = {0xA000000C, 0xA0000003}  # IO_REPARSE_TAG_SYMLINK, IO_REPARSE_TAG_MOUNT_POINT

AGENTS_BLOCK = f"""{BEGIN}
This project uses Agent Project Kit. On each request:

1. Read `.ai/PROJECT_STATE.md` and `.ai/agent-project-kit/STARTUP.md`.
2. Classify the task and load only the routed prompt/state files.
3. If the task is clear, proceed; ask one outcome question only when materially ambiguous.

Do not scan the managed snapshot or rerun onboarding, machine discovery, update
checks, or repository scans merely because a new session started. Follow the
cadence and `run-once.py` guidance in `STARTUP.md`. Keep L1 execution distinct
from L2 human judgment and L3 external evidence.
{END}
"""


class InstallError(Exception):
    pass


def ignored(relative: Path) -> bool:
    return ("__pycache__" in relative.parts or relative.suffix in {".pyc", ".pyo"}
            or relative.name in {".DS_Store", "Thumbs.db"})


def is_link(path: Path) -> bool:
    if path.is_symlink():
        return True
    tag = getattr(os.lstat(path), "st_reparse_tag", 0)
    return tag in LINK_REPARSE_TAGS


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_managed_snapshot(path: Path) -> bool:
    if not os.path.lexists(path):
        return True
    manifest = path / "manifest.json"
    if path.is_dir() and manifest.is_file():
        try:
            return bool(KIT_NAME.search(manifest.read_text(encoding="utf-8", errors="replace")))
        except OSError:
            return False
    return False


def is_kit_metadata(path: Path) -> bool:
    if not os.path.lexists(path):
        return True
    try:
        return bool(KIT_METADATA.search(path.read_text(encoding="utf-8", errors="replace")))
    except OSError:
        return False


def find_source(given: str | None, script_source: Path) -> Path:
    if given and Path(given).is_dir():
        return Path(given).resolve()
    home = Path.home()
    candidates = [script_source, home / "OneDrive/agent-project-kit",
                  home / "OneDrive - Kasetsart University/agent-project-kit",
                  home / "OneDrive/computing-environment",
                  home / "OneDrive - Kasetsart University/computing-environment"]
    for env in ("OneDrive", "OneDriveCommercial", "OneDriveConsumer"):
        if os.environ.get(env):
            candidates += [Path(os.environ[env]) / "agent-project-kit", Path(os.environ[env]) / "computing-environment"]
    profile = os.environ.get("USERPROFILE")
    if profile and Path(profile).is_dir():
        for folder in sorted(Path(profile).glob("OneDrive*")):
            candidates += [folder / "agent-project-kit", folder / "computing-environment"]
    for drive in ("c", "d"):
        for name in ("agent-project-kit", "computing-environment"):
            candidates += sorted(Path(f"/mnt/{drive}/Users").glob(f"*/OneDrive/{name}"))
            candidates += sorted(Path(f"/mnt/{drive}/Users").glob(f"*/OneDrive - */{name}"))
    for candidate in candidates:
        if (candidate / "START_HERE.md").is_file():
            return candidate.resolve()
    raise InstallError("SourcePath not found. Pass it explicitly:\n"
                       "  bash install-to-project.sh /path/to/project /path/to/agent-project-kit")


def validate_managed_block(path: Path) -> None:
    if os.path.lexists(path) and not path.is_file():
        raise InstallError(f"Refusing to edit non-file AGENTS.md path: {path}")
    if not path.is_file():
        return
    lines = [line.rstrip("\r") for line in path.read_text(encoding="utf-8", errors="surrogateescape").split("\n")]
    begins, ends = lines.count(BEGIN), lines.count(END)
    if begins != ends or begins > 1:
        raise InstallError(f"Refusing to edit malformed Agent Project Kit managed block: {path}")


def environment_manager() -> str:
    for name in ("micromamba", "mamba", "conda"):
        found = shutil.which(name)
        if found:
            return f"{name} ({found})"
    return "none (deferred; install user-local micromamba only when an environment is needed)"


def wsl_status() -> str:
    if os.name == "nt":
        return "no / Windows"
    try:
        text = Path("/proc/version").read_text(encoding="utf-8", errors="ignore").lower()
    except OSError:
        return "unknown/no"
    return "yes" if "microsoft" in text or "wsl" in text else "unknown/no"


def version_line(path: Path, label: str) -> str:
    if not path.is_file():
        return "none"
    prefix = f"- {label}:"
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith(prefix):
            return line[len(prefix):].strip() or "none"
    return "none"


def replace(src: Path, dst: Path) -> None:
    """os.replace that retries Windows sharing violations.

    Defender and the search indexer briefly hold handles on a directory that
    was just renamed, so an immediate rename back can fail with WinError 5/32.
    """
    delay = 0.1
    for attempt in range(8):
        try:
            os.replace(src, dst)
            return
        except PermissionError:
            if os.name != "nt" or attempt == 7:
                raise
            time.sleep(delay)
            delay = min(delay * 2, 3.0)


def _clear_readonly(function, path, _info) -> None:
    os.chmod(path, stat.S_IWRITE)
    function(path)


def rmtree(path: Path) -> None:
    """shutil.rmtree that also removes read-only files (Windows, synced folders)."""
    if sys.version_info >= (3, 12):
        shutil.rmtree(path, onexc=_clear_readonly)
    else:
        shutil.rmtree(path, onerror=_clear_readonly)


def current_umask() -> int:
    mask = os.umask(0)
    os.umask(mask)
    return mask


def apply_umask(path: Path) -> None:
    """Match cp: copied modes are the source modes filtered by the umask."""
    if os.name == "nt":
        return
    mask = current_umask()
    for node in [path, *(path.rglob("*") if path.is_dir() else [])]:
        os.chmod(node, stat.S_IMODE(node.stat().st_mode) & ~mask)


def write_text(path: Path, text: str) -> None:
    path.write_bytes(text.encode("utf-8", errors="surrogateescape"))


class Installer:
    def __init__(self, project: Path, source: Path, installer_name: str):
        self.project = project
        self.source = source
        self.installer_name = installer_name
        self.ai = project / ".ai"
        self.target = self.ai / "agent-project-kit"
        self.previous = self.ai / "agent-project-kit.previous"
        self.older_previous = self.ai / "agent-project-kit.previous.old"
        self.control_paths = [self.ai / "COMPUTING_ENVIRONMENT_VERSION.md", self.ai / "INSTALLATION_INFO.md",
                              self.ai / "SESSION_LOG.md", project / "AGENTS.md", project / "CLAUDE.md",
                              project / "ANTIGRAVITY.md"]
        self.stage: Path | None = None
        self.control_backup: Path | None = None
        self.agents_temp: Path | None = None
        self.snapshot_swapped = self.target_moved = self.had_target = self.previous_rotated = False
        self.keep_control_backup = False

    # -- transaction -----------------------------------------------------
    def rollback(self) -> None:
        """Undo every step; keep going when one step fails and report all failures."""
        problems: list[str] = []

        def step(description: str, action) -> None:
            try:
                action()
            except OSError as error:
                problems.append(f"{description}: {error}")

        if self.snapshot_swapped and os.path.lexists(self.target):
            step("remove the new snapshot", lambda: rmtree(self.target))
        if self.target_moved and self.had_target and os.path.lexists(self.previous):
            step("restore the active snapshot", lambda: replace(self.previous, self.target))
        if self.snapshot_swapped or self.target_moved:
            print("Install failed; restored the previous Agent Project Kit snapshot." if not problems else
                  "Install failed; the previous snapshot could not be fully restored.", file=sys.stderr)
        # Only touch the previous slot once the active snapshot is back in
        # place; until then .previous may hold the only good copy.
        active_restored = os.path.lexists(self.target) or not self.had_target
        if self.previous_rotated and os.path.lexists(self.older_previous) and active_restored:
            if os.path.lexists(self.previous):
                step("clear the previous-snapshot slot", lambda: rmtree(self.previous))
            step("restore the previous snapshot", lambda: replace(self.older_previous, self.previous))
        if self.control_backup and self.control_backup.is_dir():
            for index, path in enumerate(self.control_paths):
                def restore(path: Path = path, saved: Path = self.control_backup / str(index)) -> None:
                    if path.is_dir() and not path.is_symlink():
                        rmtree(path)
                    elif os.path.lexists(path):
                        path.unlink()
                    if saved.exists():
                        path.parent.mkdir(parents=True, exist_ok=True)
                        (shutil.copytree if saved.is_dir() else shutil.copy2)(saved, path)
                step(f"restore {path.name}", restore)
        if problems:
            # Keep the control backup so nothing is lost; say how to finish by hand.
            self.keep_control_backup = True
            print("ROLLBACK INCOMPLETE. Nothing was deleted; finish by hand:", file=sys.stderr)
            for problem in problems:
                print(f"- {problem}", file=sys.stderr)
            print(f"- snapshots: rename {self.previous.name} back to {self.target.name} if it is missing; "
                  f"{self.older_previous.name} holds the older copy", file=sys.stderr)
            if self.control_backup:
                print(f"- control-file backup kept at: {self.control_backup}", file=sys.stderr)

    def cleanup(self, success: bool) -> None:
        if success and os.path.lexists(self.older_previous):
            try:
                rmtree(self.older_previous)
            except OSError:
                print(f"Warning: could not remove old snapshot rotation: {self.older_previous}", file=sys.stderr)
        for leftover in (self.stage, self.agents_temp):
            if leftover and os.path.lexists(leftover):
                rmtree(leftover) if leftover.is_dir() else leftover.unlink()
        if self.control_backup and self.control_backup.exists() and not self.keep_control_backup:
            try:
                rmtree(self.control_backup)
            except OSError:
                print(f"Warning: could not remove installer control backup: {self.control_backup}", file=sys.stderr)

    # -- steps -------------------------------------------------------------
    def preflight(self) -> None:
        validate_managed_block(self.project / "AGENTS.md")
        self.ai.mkdir(parents=True, exist_ok=True)
        if self.source.resolve() == self.target.resolve():
            raise InstallError(f"Source path equals install target: {self.target}\n"
                               "Clone Agent Project Kit into .ai/agent-project-kit-source or use a cache path, then rerun.")
        for path, purpose in ((self.target, ".ai/agent-project-kit snapshot"),
                              (self.previous, ".ai/agent-project-kit.previous snapshot")):
            if not is_managed_snapshot(path):
                raise InstallError(f"Refusing to overwrite existing {purpose}: {path}\n"
                                   "This path exists but does not look like an Agent Project Kit snapshot.\n"
                                   "Move or rename it first, then rerun the installer.")
        for path in self.control_paths[:2]:
            if not is_kit_metadata(path):
                raise InstallError(f"Refusing to overwrite existing user file: {path}\n"
                                   "This file name is needed for Agent Project Kit metadata, but the existing file "
                                   "does not look like kit metadata.\nMove or rename it first, then rerun the installer.")

    def backup_controls(self) -> None:
        self.control_backup = Path(tempfile.mkdtemp(prefix=".agent-project-kit.control-backup.", dir=self.ai))
        for index, path in enumerate(self.control_paths):
            if path.is_dir():
                shutil.copytree(path, self.control_backup / str(index), symlinks=True)
            elif os.path.lexists(path):
                shutil.copy2(path, self.control_backup / str(index), follow_symlinks=False)

    def stage_package(self) -> None:
        self.stage = Path(tempfile.mkdtemp(prefix=".agent-project-kit.stage.", dir=self.ai))
        for item in ITEMS:
            src = self.source / item
            if not os.path.lexists(src):
                raise InstallError(f"Missing required package item: {src}")
            nodes = [src] + (list(src.rglob("*")) if src.is_dir() and not is_link(src) else [])
            if any(is_link(node) for node in nodes):
                raise InstallError(f"Refusing to package symbolic link: {src}")
            dst = self.stage / item
            if src.is_dir():
                shutil.copytree(src, dst, copy_function=shutil.copy,
                                ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo", ".DS_Store", "Thumbs.db"))
                files = [p for p in src.rglob("*") if p.is_file() and not ignored(p.relative_to(src))]
            else:
                shutil.copy(src, dst)
                files = [src]
            apply_umask(dst)
            for source_file in files:
                relative = source_file.relative_to(self.source)
                staged = self.stage / relative
                if not staged.is_file():
                    raise InstallError(f"Staged file missing during SHA-256 verification: {relative.as_posix()}")
                if sha256(source_file) != sha256(staged):
                    raise InstallError(f"Staged SHA-256 mismatch: {relative.as_posix()}")
        if (not is_managed_snapshot(self.stage) or not (self.stage / "STARTUP.md").is_file()
                or not (self.stage / "scripts" / "context.py").is_file()):
            raise InstallError(f"Staged package validation failed: {self.stage}")

    def swap(self) -> None:
        if os.path.lexists(self.previous):
            if os.path.lexists(self.older_previous):
                rmtree(self.older_previous)
            replace(self.previous, self.older_previous)
            self.previous_rotated = True
        if os.path.lexists(self.target):
            self.had_target = True
            replace(self.target, self.previous)
            self.target_moved = True
        assert self.stage is not None
        # Test-only fault injection: fail exactly while activating the stage.
        if os.environ.get("APK_INSTALL_TEST_FAULT") == "activate":
            raise OSError("injected fault while activating the staged snapshot")
        replace(self.stage, self.target)
        self.stage = None
        self.snapshot_swapped = True

    def add_templates(self) -> None:
        # A migrated project keeps its state in PROJECT_STATE.md; do not
        # recreate the legacy file (see config/STATE_MIGRATION.md).
        migrated = any(self.ai.glob("state.json.migrated-*"))
        for name in TEMPLATES:
            target = self.ai / name
            if (name == "state.json" and migrated) or target.is_file():
                continue
            template = self.source / "templates" / name
            if template.is_file():
                shutil.copy(template, target)
                apply_umask(target)
            else:
                target.touch()

    def write_metadata(self, manifest: dict, first_install: bool, machine: str, wsl: str, manager: str) -> None:
        def value(key: str, default: str = "unknown") -> str:
            item = manifest.get(key, "")
            return str(item) if item not in ("", None) and not isinstance(item, (dict, list)) else default
        name, display = value("name", "agent-project-kit"), value("display_name", "Agent Project Kit")
        version, updated = value("version"), value("updated")
        state_schema, profile_schema = value("state_schema_version"), value("machine_profile_schema_version")
        version_path = self.ai / "COMPUTING_ENVIRONMENT_VERSION.md"
        previous_version = version_line(version_path, "Package version")
        previous_profile = version_line(version_path, "Machine profile schema version")
        now = dt.datetime.now().astimezone().isoformat(timespec="seconds")
        first = "yes" if first_install else "no"
        updater = "scripts/update-from-pages.ps1 -DryRun" if os.name == "nt" else "scripts/update-from-pages.sh --dry-run"
        apply = "scripts/update-from-pages.ps1" if os.name == "nt" else "scripts/update-from-pages.sh"
        write_text(version_path, f"""# COMPUTING_ENVIRONMENT_VERSION

- Package name: {name}
- Package display name: {display}
- Legacy package names: computing-environment
- Package version: {version}
- Package updated: {updated}
- State schema version: {state_schema}
- Machine profile schema version: {profile_schema}
- Previous package version: {previous_version}
- Previous machine profile schema version: {previous_profile}
- Installed/updated: {now}
- Update check cadence: report installed version every startup; check GitHub Pages manifest when last check is missing, older than 14 days, before package-level/release work, or when explicitly asked
- Last update check: not checked by installer
- Latest known upstream version: unknown
- Update check source: {self.source}
- Source path: {self.source}
- Installer: {self.installer_name}
- Machine: {machine}
- WSL2 detected: {wsl}
- First install: {first}
- Conda-family manager: {manager}

## Update Rule

If package version changes but machine profile schema version is unchanged,
reuse `.ai/MACHINE_PROFILE.md`; do not rerun first-use discovery unless
hostname/platform/path style changed.

Project-local state files are preserved by the installer. Update package
snapshots and missing template files without overwriting project-specific state.
On first install, same-name paths that do not look like Agent Project Kit
content are left untouched and the installer stops before writing kit-owned files.

## Update Check Rule

Every startup should report the installed Agent Project Kit package name and
version from this file. Do not fetch/pull package updates every time. Check the
GitHub Pages manifest with `{updater}` when
`Last update check` is missing/stale, before package-level or release work, or
when explicitly asked. Apply updates through `{apply}` so
project-local state is preserved.
""")
        write_text(self.ai / "INSTALLATION_INFO.md", f"""# INSTALLATION_INFO

- Package version: {version}
- State schema version: {state_schema}
- Machine profile schema version: {profile_schema}
- Installed/updated: {now}
- Project path: {self.project}
- Agent Project Kit source: {self.source}
- Machine detected: {machine}
- WSL2 detected: {wsl}
- First install: {first}
- Conda-family manager: {manager}

Minimal startup (read other files only when STARTUP.md triggers them):

1. AGENTS.md
2. .ai/PROJECT_STATE.md
3. .ai/agent-project-kit/STARTUP.md
""")

    def update_agents(self) -> None:
        path = self.project / "AGENTS.md"
        if path.is_file():
            raw = path.read_bytes().decode("utf-8", errors="surrogateescape")
            kept, skip = [], False
            lines = raw.split("\n")
            if lines and lines[-1] == "":
                lines.pop()
            for line in lines:
                bare = line.rstrip("\r")
                if bare == BEGIN:
                    skip = True; continue
                if bare == END:
                    skip = False; continue
                if not skip:
                    kept.append(line + "\n")
            text = "".join(kept) + AGENTS_BLOCK
        else:
            text = "# AGENTS.md\n\n" + AGENTS_BLOCK
        fd, temp = tempfile.mkstemp(prefix=".AGENTS.md.tmp.", dir=self.project)
        os.close(fd)
        self.agents_temp = Path(temp)
        write_text(self.agents_temp, text)
        if path.is_file():
            os.chmod(self.agents_temp, stat.S_IMODE(path.stat().st_mode))
        replace(self.agents_temp, path)
        self.agents_temp = None

    def update_adapter(self, name: str) -> None:
        path = self.project / name
        if not path.is_file():
            write_text(path, f"""# {name}

{ADAPTER}
This project uses Agent Project Kit.

Read these first:

1. `AGENTS.md`
2. `.ai/PROJECT_STATE.md`
3. `.ai/PROJECT_HIERARCHY.md`
4. `.ai/COMPUTING_ENVIRONMENT_VERSION.md`
5. `.ai/MACHINE_PROFILE.md`
6. `.ai/LOCAL_RESOURCES.md`
7. `.ai/MACHINE_COMPATIBILITY.md`
8. `.ai/RUNBOOK.md`
9. `.ai/TOKEN_BUDGET.md`

Follow the Spec-Eval-Loop workflow in `AGENTS.md`.
Do not overwrite project-local `.ai/` state when updating Agent Project Kit.
<!-- END AGENT-PROJECT-KIT-ADAPTER -->
""")
        elif ADAPTER not in path.read_text(encoding="utf-8", errors="replace"):
            with path.open("ab") as handle:
                handle.write(f"""
{ADAPTER}
Agent Project Kit adapter: read `AGENTS.md` and project-local `.ai/` state
before acting. Do not overwrite project-local `.ai/` state when updating the
kit.
<!-- END AGENT-PROJECT-KIT-ADAPTER -->
""".encode("utf-8"))

    def record_session(self, machine: str) -> None:
        log = self.ai / "SESSION_LOG.md"
        if not log.is_file() or INSTALL_LOG_MARKER in log.read_text(encoding="utf-8", errors="replace"):
            return
        with log.open("ab") as handle:
            handle.write(f"""
## {dt.date.today().isoformat()} — {machine} — {INSTALL_LOG_MARKER}
- Objective: Install/update Agent Project Kit workflow files.
- Mode: T0 Quick
- Files touched: AGENTS.md, .ai/agent-project-kit/, .ai project templates if missing; existing user files with conflicting metadata/snapshot names are not overwritten
- Commands/tests run: {self.installer_name}
- Result: Installed from {self.source}
- Local resources used: none
- Decisions made: none
- Open questions: Fill PROJECT_HIERARCHY.md to declare whether this directory is a project/subproject/plain subdir; fill MACHINE_PROFILE.md for new machines; if package version changed but machine profile schema did not, reuse the existing profile; fill LOCAL_RESOURCES.md and DOCUMENT_PIPELINE.md if project uses non-portable cache/data/build files; run organize-project-markdown.py if scattered Markdown exists
- Next action: Resume project via PROJECT_STATE.md
- Token note: Future sessions should read PROJECT_STATE.md before scanning broadly.
""".encode("utf-8"))

    def run(self) -> None:
        first_install = not os.path.lexists(self.target)
        machine = (socket.gethostname() or "unknown").lower()
        wsl, manager = wsl_status(), environment_manager()
        if first_install:
            print(f"Environment-manager preflight: {manager}")
        self.preflight()
        self.backup_controls()
        manifest_path = self.source / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.is_file() else {}
        self.stage_package()
        self.swap()
        self.ai.mkdir(parents=True, exist_ok=True)
        self.add_templates()
        self.write_metadata(manifest, first_install, machine, wsl, manager)
        # Installing the kit into its own source tree must not edit the
        # canonical, distributed AGENTS.md/CLAUDE.md/ANTIGRAVITY.md.
        self_hosted = Path(os.path.realpath(self.source)) == Path(os.path.realpath(self.project))
        if not self_hosted:
            self.update_agents()
            self.update_adapter("CLAUDE.md")
            self.update_adapter("ANTIGRAVITY.md")
        self.record_session(machine)
        print(f"Installed Agent Project Kit into: {self.target}")
        if self_hosted:
            print("Self-hosted kit source: left canonical AGENTS.md and adapter files unchanged")
        else:
            print(f"Created/updated project AGENTS.md: {self.project / 'AGENTS.md'}")
        print(f"Project AI state directory: {self.ai}")
        print(f"Detected machine: {machine}")
        print(f"WSL2 detected: {wsl}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("project", nargs="?", default=".")
    parser.add_argument("source", nargs="?", default="")
    parser.add_argument("--installer-name", default="apk_install.py",
                        help="name recorded in version metadata (set by the wrappers)")
    args = parser.parse_args(argv)
    sys.dont_write_bytecode = True
    # Thai project paths must print on Windows consoles and pipes (cp1252 default).
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    try:
        source = find_source(args.source or None, Path(__file__).resolve().parent.parent)
        project = Path(args.project).resolve()
        if not project.is_dir():
            raise InstallError(f"Project path is not a directory: {project}")
    except InstallError as error:
        print(error, file=sys.stderr)
        return 1
    installer = Installer(project, source, args.installer_name)
    success = False
    try:
        installer.run()
        success = True
    except (InstallError, OSError) as error:
        installer.rollback()
        print(error, file=sys.stderr)
    except BaseException:  # KeyboardInterrupt and friends still roll back
        installer.rollback()
        raise
    finally:
        installer.cleanup(success)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
