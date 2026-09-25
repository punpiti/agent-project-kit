#!/usr/bin/env python3
"""Migrate a legacy .ai/state.json into the authoritative .ai/PROJECT_STATE.md.

Contract (config/STATE_MIGRATION.md): dry run by default; --write appends one
marked section to PROJECT_STATE.md and renames state.json to a dated
state.json.migrated-* backup. Nothing is deleted, existing Markdown is never
rewritten, and a second run is a no-op.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BEGIN = "<!-- BEGIN MIGRATED LEGACY STATE sha256={digest} -->"
END = "<!-- END MIGRATED LEGACY STATE -->"
FIELDS = (
    ("active_task", "Active task"),
    ("last_completed", "Last completed"),
    ("blockers", "Blockers"),
    ("next_actions", "Next actions"),
    ("open_decisions", "Open decisions"),
    ("updated", "Legacy updated"),
)
# Carried as structure, not narrative.
SKIPPED = {"schema_version", "status"}


def schema_errors(data: object) -> list[str]:
    spec = importlib.util.spec_from_file_location("apk_validate_schemas", ROOT / "scripts" / "validate_schemas.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.validate(data, "legacy-state")


def render_value(value: object) -> list[str]:
    if isinstance(value, list):
        return [f"  - {item if isinstance(item, str) else json.dumps(item, ensure_ascii=False)}" for item in value] or ["  - (none)"]
    if isinstance(value, str):
        return [f"  {value}"]
    return [f"  {json.dumps(value, ensure_ascii=False)}"]


def render(data: dict, digest: str, today: str) -> str:
    lines = [
        BEGIN.format(digest=digest),
        f"## Migrated legacy state (from `.ai/state.json`, {today})",
        "",
        "Copied verbatim for human review. It may be older than the sections above;",
        "move anything still current into them, then delete this section if wanted.",
        "",
    ]
    known = {key for key, _ in FIELDS}
    for key, label in FIELDS:
        if key in data and data[key] not in (None, "", []):
            lines.append(f"- {label}:")
            lines.extend(render_value(data[key]))
    for key in sorted(set(data) - known - SKIPPED):
        lines.append(f"- `{key}`:")
        lines.extend(render_value(data[key]))
    lines.append(END)
    return "\n".join(lines) + "\n"


def plan(project: Path) -> tuple[str, dict | None]:
    """Return (status, details). Status is one of: none, placeholder, invalid, migrated, ready."""
    ai = project / ".ai"
    legacy = ai / "state.json"
    if not legacy.exists():
        return "none", None
    if legacy.is_symlink() or not legacy.is_file():
        return "invalid", {"error": "state.json is not a regular file"}
    raw = legacy.read_bytes()
    try:
        data = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        return "invalid", {"error": f"state.json is not valid UTF-8 JSON ({error})"}
    errors = schema_errors(data)
    if errors:
        return "invalid", {"error": "; ".join(errors[:3])}
    digest = hashlib.sha256(raw).hexdigest()
    state_md = ai / "PROJECT_STATE.md"
    existing = state_md.read_text(encoding="utf-8") if state_md.is_file() else ""
    if BEGIN.format(digest=digest) in existing:
        return "migrated", {"legacy": legacy, "digest": digest}
    if data.get("status") == "placeholder":
        return "placeholder", {"legacy": legacy, "digest": digest}
    today = dt.date.today().isoformat()
    return "ready", {"legacy": legacy, "digest": digest, "state_md": state_md,
                     "existing": existing, "section": render(data, digest, today),
                     "backup": ai / f"state.json.migrated-{today.replace('-', '')}"}


def main() -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("--project", type=Path, default=Path("."))
    parser.add_argument("--write", action="store_true", help="apply the migration (default: dry run)")
    parser.add_argument("--retire-placeholder", action="store_true",
                        help="with --write, also rename an empty placeholder state.json")
    args = parser.parse_args()
    project = args.project.resolve()
    status, details = plan(project)
    if status == "none":
        print("state migration: nothing to do (no .ai/state.json)"); return 0
    if status == "invalid":
        print(f"state migration: REFUSED: {details['error']}"); return 1
    if status == "migrated":
        print("state migration: already migrated (PROJECT_STATE.md holds this state.json)"); return 0
    backup = details["legacy"].with_name(details["legacy"].name + ".migrated-" + dt.date.today().strftime("%Y%m%d"))
    if status == "placeholder":
        if args.write and args.retire_placeholder:
            if backup.exists():
                print(f"state migration: REFUSED: backup already exists: {backup.name}"); return 1
            details["legacy"].rename(backup)
            print(f"state migration: retired placeholder state.json -> {backup.name}")
        else:
            print("state migration: placeholder state.json holds no project state; "
                  "use --write --retire-placeholder to retire it")
        return 0
    if not args.write:
        print("state migration: DRY RUN. With --write this section is appended to .ai/PROJECT_STATE.md")
        print(f"and state.json is renamed to {details['backup'].name}:\n")
        print(details["section"], end="")
        return 0
    if details["backup"].exists():
        print(f"state migration: REFUSED: backup already exists: {details['backup'].name}"); return 1
    existing = details["existing"]
    if not existing:
        existing = "# PROJECT_STATE\n"
    separator = "" if existing.endswith("\n\n") else ("\n" if existing.endswith("\n") else "\n\n")
    state_md: Path = details["state_md"]
    temp = state_md.with_name(f".{state_md.name}.migrate.tmp")
    temp.write_bytes((existing + separator + details["section"]).encode("utf-8"))
    temp.replace(state_md)
    details["legacy"].rename(details["backup"])
    print(f"state migration: appended legacy state to {state_md.relative_to(project)}; "
          f"state.json -> {details['backup'].name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
