#!/usr/bin/env python3
"""Install computing-environment rules into a project.

Works from WSL2, Linux, macOS, or Windows Python.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import platform
import shutil
import socket
from pathlib import Path

ITEMS = [
    "manifest.json",
    "PACKAGE_CONTENTS.md",
    "README.md",
    "INSTALL_IN_PROJECT.md",
    "GIT_DISTRIBUTION.md",
    "OPEN_WITH_AGENT.md",
    "MARKDOWN_OVER_ARCHIVE_RECOVERY.md",
    "START_HERE.md",
    "SPEC_EVAL_LOOP_INSTRUCTION.md",
    "AGENTS.md",
    "CLAUDE.md",
    "ANTIGRAVITY.md",
    "AI_CLIENTS.md",
    "MACHINE_PROFILES.md",
    "TOKEN_DISCIPLINE.md",
    "DOCUMENT_PRODUCTION_POLICY.md",
    "MARKDOWN_ORGANIZATION_POLICY.md",
    "SECURITY_EXCLUSIONS.md",
    "MIGRATION_FROM_OLD.md",
    "ENVIRONMENT_POLICY.md",
    "GLOBAL_START_PROMPT.md",
    "bootstrap_ai_project.py",
    "prompts",
    "templates",
    "checklists",
    "scripts",
]

PROJECT_TEMPLATES = [
    "PROJECT_STATE.md",
    "PROJECT_HIERARCHY.md",
    "MACHINE_PROFILE.md",
    "COMPUTING_ENVIRONMENT_VERSION.md",
    "LOCAL_RESOURCES.md",
    "MACHINE_COMPATIBILITY.md",
    "RUNBOOK.md",
    "TOKEN_BUDGET.md",
    "SESSION_LOG.md",
    "ENVIRONMENT_VARIABLES.md",
    "DOCUMENT_PIPELINE.md",
    "DOCUMENT_STYLE.md",
    "DOCUMENT_QA.md",
    "MARKDOWN_INVENTORY.md",
]


def is_wsl() -> bool:
    try:
        text = Path("/proc/version").read_text(encoding="utf-8", errors="ignore").lower()
        return "microsoft" in text or "wsl" in text
    except Exception:
        return False


def source_candidates(script_path: Path) -> list[Path]:
    candidates: list[Path] = []
    candidates.append(script_path.parent.parent)

    home = Path.home()
    candidates.extend([
        home / "OneDrive" / "agent-project-kit",
        home / "OneDrive - Kasetsart University" / "agent-project-kit",
        home / "OneDrive" / "computing-environment",
        home / "OneDrive - Kasetsart University" / "computing-environment",
    ])

    for env_name in ["OneDrive", "OneDriveCommercial", "OneDriveConsumer"]:
        val = os.environ.get(env_name)
        if val:
            candidates.append(Path(val) / "computing-environment")

    # WSL2 Windows mounts
    for mount in [Path("/mnt/c/Users"), Path("/mnt/d/Users")]:
        if mount.exists():
            for user_dir in mount.iterdir():
                if not user_dir.is_dir():
                    continue
                for one in user_dir.glob("OneDrive*"):
                    candidates.append(one / "agent-project-kit")
                    candidates.append(one / "computing-environment")

    # De-duplicate preserving order
    out: list[Path] = []
    seen = set()
    for p in candidates:
        key = str(p)
        if key not in seen:
            seen.add(key)
            out.append(p)
    return out


def find_source(explicit: str | None, script_path: Path) -> Path:
    if explicit:
        p = Path(explicit).expanduser().resolve()
        if (p / "START_HERE.md").exists():
            return p
        raise FileNotFoundError(f"Source path does not look like Agent Project Kit: {p}")
    for p in source_candidates(script_path):
        try:
            if (p / "START_HERE.md").exists():
                return p.resolve()
        except OSError:
            pass
    raise FileNotFoundError("Could not auto-detect Agent Project Kit. Pass --source-path.")


def copy_item(src: Path, dst: Path) -> None:
    if not src.exists():
        print(f"Warning: missing item {src}")
        return
    if dst.exists():
        if dst.is_dir():
            shutil.rmtree(dst)
        else:
            dst.unlink()
    if src.is_dir():
        shutil.copytree(src, dst)
    else:
        shutil.copy2(src, dst)


def copy_template_if_missing(source: Path, ai_dir: Path, name: str) -> None:
    dst = ai_dir / name
    if dst.exists():
        return
    src = source / "templates" / name
    if src.exists():
        shutil.copy2(src, dst)
    else:
        dst.write_text("", encoding="utf-8")


def read_manifest(source: Path) -> dict[str, str]:
    manifest = source / "manifest.json"
    if not manifest.exists():
        return {}
    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
    except Exception:
        return {}
    out: dict[str, str] = {}
    for key, value in data.items():
        if isinstance(value, (str, int, float)):
            out[key] = str(value)
        elif isinstance(value, list):
            out[key] = ", ".join(str(item) for item in value)
    return out


def read_version_line(path: Path, label: str) -> str:
    if not path.exists():
        return "none"
    prefix = f"- {label}:"
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if line.startswith(prefix):
            return line[len(prefix):].strip() or "none"
    return "none"


def update_agents(project: Path) -> None:
    agents = project / "AGENTS.md"
    marker = "<!-- BEGIN COMPUTING-ENVIRONMENT -->"
    block = """<!-- BEGIN COMPUTING-ENVIRONMENT -->
Before working on this project, read the project-local AI working rules:

If this project is the Agent Project Kit source repository itself, including the
legacy `computing-environment` folder, use the root-level governance files as
canonical and treat `.ai/computing-environment/` as a packaged downstream
snapshot. Do not recurse into another Agent Project Kit / `computing-environment`
layer unless explicitly requested.

- `.ai/computing-environment/START_HERE.md`
- `.ai/computing-environment/SPEC_EVAL_LOOP_INSTRUCTION.md`
- `.ai/computing-environment/AGENTS.md`
- `.ai/computing-environment/MACHINE_PROFILES.md`
- `.ai/computing-environment/TOKEN_DISCIPLINE.md`
- `.ai/computing-environment/DOCUMENT_PRODUCTION_POLICY.md`
- `.ai/computing-environment/MARKDOWN_ORGANIZATION_POLICY.md`
- `.ai/computing-environment/ENVIRONMENT_POLICY.md`

Then read project state:

- `.ai/PROJECT_STATE.md`
- `.ai/PROJECT_HIERARCHY.md`
- `.ai/MACHINE_PROFILE.md`
- `.ai/LOCAL_RESOURCES.md`
- `.ai/MACHINE_COMPATIBILITY.md`
- `.ai/RUNBOOK.md`
- `.ai/TOKEN_BUDGET.md`
- `.ai/SESSION_LOG.md`
- `.ai/DOCUMENT_PIPELINE.md`
- `.ai/DOCUMENT_STYLE.md`
- `.ai/DOCUMENT_QA.md`
- `.ai/MARKDOWN_INVENTORY.md`
- `.ai/COMPUTING_ENVIRONMENT_VERSION.md`

Use Spec–Eval–Loop Workflow.
Record machine identity/storage assumptions in `.ai/MACHINE_PROFILE.md`.
Do not pretend L2 or L3 has been resolved by L1 alone.
Do not pretend files outside the project/shared source tree exist on every machine.
For document work, start with Markdown, use project style sheets, and run final PDF QA before calling a document final.
Do not create loose Markdown scratch files; put AI working notes in `.ai/` and register document sources in `.ai/DOCUMENT_PIPELINE.md`.
<!-- END COMPUTING-ENVIRONMENT -->
"""
    if not agents.exists():
        agents.write_text(f"# AGENTS.md\n\n{block}", encoding="utf-8")
        return
    text = agents.read_text(encoding="utf-8", errors="ignore")
    if marker not in text:
        agents.write_text(text.rstrip() + "\n\n" + block, encoding="utf-8")


def update_adapter(project: Path, filename: str) -> None:
    path = project / filename
    marker = "<!-- BEGIN AGENT-PROJECT-KIT-ADAPTER -->"
    block = f"""# {filename}

{marker}
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
"""
    if not path.exists():
        path.write_text(block, encoding="utf-8")
        return
    text = path.read_text(encoding="utf-8", errors="ignore")
    if marker not in text:
        appendix = """<!-- BEGIN AGENT-PROJECT-KIT-ADAPTER -->
Agent Project Kit adapter: read `AGENTS.md` and project-local `.ai/` state
before acting. Do not overwrite project-local `.ai/` state when updating the
kit.
<!-- END AGENT-PROJECT-KIT-ADAPTER -->
"""
        path.write_text(text.rstrip() + "\n\n" + appendix, encoding="utf-8")


def append_session_log(ai_dir: Path, source: Path, project: Path) -> None:
    log = ai_dir / "SESSION_LOG.md"
    if not log.exists():
        return
    machine = socket.gethostname().lower()
    today = _dt.date.today().isoformat()
    entry = f"""

## {today} — {machine} — Agent Project Kit installed/updated
- Objective: Install/update Agent Project Kit workflow files.
- Mode: T0 Quick
- Files touched: AGENTS.md, .ai/computing-environment/, .ai project templates if missing
- Commands/tests run: bootstrap_ai_project.py
- Result: Installed from {source}
- Local resources used: none
- Decisions made: none
- Open questions: Fill PROJECT_HIERARCHY.md to declare whether this directory is a project/subproject/plain subdir; fill MACHINE_PROFILE.md for new machines; if package version changed but machine profile schema did not, reuse the existing profile; fill LOCAL_RESOURCES.md and DOCUMENT_PIPELINE.md if project uses non-portable cache/data/build files; run organize-project-markdown.py if the project has scattered Markdown files
- Next action: Resume project via PROJECT_STATE.md
- Token note: Future sessions should read PROJECT_STATE.md before scanning broadly.
"""
    with log.open("a", encoding="utf-8") as f:
        f.write(entry)


def main() -> int:
    parser = argparse.ArgumentParser(description="Install Agent Project Kit into a project")
    parser.add_argument("project_path", nargs="?", default=".")
    parser.add_argument("--source-path", default=None)
    args = parser.parse_args()

    script_path = Path(__file__).resolve()
    source = find_source(args.source_path, script_path)
    project = Path(args.project_path).expanduser().resolve()
    if not project.exists():
        raise FileNotFoundError(project)

    ai_dir = project / ".ai"
    target = ai_dir / "computing-environment"
    target.mkdir(parents=True, exist_ok=True)

    for item in ITEMS:
        copy_item(source / item, target / item)

    ai_dir.mkdir(parents=True, exist_ok=True)
    for name in PROJECT_TEMPLATES:
        copy_template_if_missing(source, ai_dir, name)

    manifest = read_manifest(source)
    package_name = manifest.get("name", "agent-project-kit")
    package_display_name = manifest.get("display_name", "Agent Project Kit")
    legacy_names = manifest.get("legacy_names", "computing-environment")
    package_version = manifest.get("version", "unknown")
    package_updated = manifest.get("updated", "unknown")
    state_schema = manifest.get("state_schema_version", "unknown")
    profile_schema = manifest.get("machine_profile_schema_version", "unknown")
    version_path = ai_dir / "COMPUTING_ENVIRONMENT_VERSION.md"
    previous_package_version = read_version_line(version_path, "Package version")
    previous_profile_schema = read_version_line(version_path, "Machine profile schema version")

    version_info = f"""# COMPUTING_ENVIRONMENT_VERSION

- Package name: {package_name}
- Package display name: {package_display_name}
- Legacy package names: {legacy_names}
- Package version: {package_version}
- Package updated: {package_updated}
- State schema version: {state_schema}
- Machine profile schema version: {profile_schema}
- Previous package version: {previous_package_version}
- Previous machine profile schema version: {previous_profile_schema}
- Installed/updated: {_dt.datetime.now().isoformat(timespec='seconds')}
- Source path: {source}
- Installer: bootstrap_ai_project.py
- Machine: {socket.gethostname().lower()}
- Platform: {platform.platform()}
- WSL2 detected: {'yes' if is_wsl() else 'no/unknown'}

## Update Rule

If package version changes but machine profile schema version is unchanged,
reuse `.ai/MACHINE_PROFILE.md`; do not rerun first-use discovery unless
hostname/platform/path style changed.

Project-local state files are preserved by the installer. Update package
snapshots and missing template files without overwriting project-specific state.
"""
    (ai_dir / "COMPUTING_ENVIRONMENT_VERSION.md").write_text(version_info, encoding="utf-8")

    install_info = f"""# INSTALLATION_INFO

- Package version: {package_version}
- State schema version: {state_schema}
- Machine profile schema version: {profile_schema}
- Installed/updated: {_dt.datetime.now().isoformat(timespec='seconds')}
- Project path: {project}
- Computing environment source: {source}
- Machine detected: {socket.gethostname().lower()}
- Platform: {platform.platform()}
- WSL2 detected: {'yes' if is_wsl() else 'no/unknown'}

Read this project with:

1. AGENTS.md
2. .ai/computing-environment/START_HERE.md
3. .ai/PROJECT_STATE.md
4. .ai/PROJECT_HIERARCHY.md
5. .ai/MACHINE_PROFILE.md
6. .ai/LOCAL_RESOURCES.md
7. .ai/MACHINE_COMPATIBILITY.md
8. .ai/RUNBOOK.md
9. .ai/TOKEN_BUDGET.md
10. .ai/COMPUTING_ENVIRONMENT_VERSION.md
"""
    (ai_dir / "INSTALLATION_INFO.md").write_text(install_info, encoding="utf-8")

    update_agents(project)
    update_adapter(project, "CLAUDE.md")
    update_adapter(project, "ANTIGRAVITY.md")
    append_session_log(ai_dir, source, project)

    print(f"Installed Agent Project Kit into: {target}")
    print(f"Project AI state directory: {ai_dir}")
    print(f"Detected machine: {socket.gethostname().lower()}")
    print(f"WSL2 detected: {'yes' if is_wsl() else 'no/unknown'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
