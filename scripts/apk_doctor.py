#!/usr/bin/env python3
"""Read-only consistency checks for an Agent Project Kit installation."""
from __future__ import annotations
import argparse, importlib.util, json, platform, re, sys
from pathlib import Path
import datetime as dt

def field(text: str, name: str) -> str | None:
    # [ \t]* keeps an empty field from capturing the next line's value.
    m = re.search(rf"^- {re.escape(name)}:[ \t]*(\S.*)$", text, re.MULTILINE); return m.group(1).strip() if m else None

def select_kit_root(root: Path) -> tuple[Path | None, bool]:
    """Prefer the canonical source tree over an installed downstream snapshot."""
    if (root/"manifest.json").is_file() and (root/"START_HERE.md").is_file():
        return root, True
    snapshot = root/".ai"/"agent-project-kit"
    if (snapshot/"manifest.json").is_file():
        return snapshot, False
    return None, False

def schema_issues(kit: Path, root: Path) -> list[str]:
    """Check project binding/metadata with the kit's own schemas (newer kits only)."""
    script = kit/"scripts"/"validate_schemas.py"
    if not script.is_file(): return []
    sys.dont_write_bytecode = True  # never add caches to a verified runtime
    spec = importlib.util.spec_from_file_location("apk_validate_schemas", script)
    if not spec or not spec.loader: return []
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    issues = []
    for name, schema in module.PROJECT_FILES:
        path = root/name
        if path.is_file():
            issues.extend(f"{name} schema: {error}" for error in module.validate_file(path, schema)[:5])
    return issues

def main() -> int:
    p=argparse.ArgumentParser(description=__doc__); p.add_argument("project",nargs="?",default="."); p.add_argument("--quick",action="store_true"); a=p.parse_args()
    root=Path(a.project).resolve(); issues=[]
    for path in (root/"AGENTS.md",root/".ai"/"PROJECT_STATE.md"):
        if not path.is_file(): issues.append(f"missing required file: {path.relative_to(root)}")
    project_state=root/".ai"/"PROJECT_STATE.md"
    if project_state.is_file():
        state_text=project_state.read_text(encoding="utf-8",errors="ignore")
        placeholders=("- Project name:\n", "สรุปเป้าหมายปัจจุบัน 3–7 บรรทัด")
        if all(marker in state_text for marker in placeholders):
            issues.append("PROJECT_STATE status=placeholder: initialize it before relying on resume")
        updated=field(state_text,"Last updated")
        if updated:
            try:
                age=(dt.date.today()-dt.date.fromisoformat(updated[:10])).days
                if age > 90: issues.append(f"PROJECT_STATE status=stale: Last updated is {age} days old")
            except ValueError: issues.append("PROJECT_STATE has an invalid Last updated date")
    structured=[]
    for name in ("project.json","state.json","local-resources.json"):
        path=root/".ai"/name
        if path.exists():
            try:
                data=json.loads(path.read_text(encoding="utf-8")); structured.append(data.get("status"))
                if data.get("schema_version") != 1: issues.append(f"{name} has unsupported schema_version")
            except (OSError,json.JSONDecodeError) as exc: issues.append(f"invalid {name}: {exc}")
    legacy=root/".ai"/"state.json"
    if legacy.is_file() and project_state.is_file():
        try: legacy_status=json.loads(legacy.read_text(encoding="utf-8")).get("status")
        except (OSError,json.JSONDecodeError): legacy_status=None
        if legacy_status not in (None,"placeholder"):
            issues.append("legacy .ai/state.json holds state that PROJECT_STATE.md overrides; review with scripts/migrate_state.py --project .")
    if structured and structured[:2] == ["placeholder","placeholder"]:
        print("Agent Project Kit doctor: structured state is placeholder; Markdown compatibility state remains active")
    kit, canonical = select_kit_root(root)
    if kit is None: issues.append("cannot find Agent Project Kit manifest")
    else:
        try: manifest=json.loads((kit/"manifest.json").read_text(encoding="utf-8"))
        except (OSError,json.JSONDecodeError) as exc: issues.append(f"invalid manifest: {exc}"); manifest={}
        issues.extend(schema_issues(kit, root))
        vf=root/".ai"/"COMPUTING_ENVIRONMENT_VERSION.md"
        if canonical:
            pass  # Source checkout is authoritative; installed-version metadata is downstream-only.
        elif not vf.is_file(): issues.append("missing .ai/COMPUTING_ENVIRONMENT_VERSION.md")
        else:
            text=vf.read_text(encoding="utf-8"); installed=field(text,"Package version"); machine=field(text,"Machine")
            if installed and manifest.get("version") and installed != manifest["version"]: issues.append(f"version drift: metadata={installed}, snapshot={manifest['version']}")
            if machine and machine.lower()!=platform.node().lower(): issues.append(f"install metadata machine is {machine}; current machine is {platform.node()}")
    ledger=root/".ai"/"AGENT_PROJECT_KIT_STATE.json"
    if ledger.exists():
        try:
            if not isinstance(json.loads(ledger.read_text(encoding="utf-8")).get("checks"),dict): issues.append("state ledger has no checks object")
        except (OSError,json.JSONDecodeError) as exc: issues.append(f"invalid state ledger: {exc}")
    print("Agent Project Kit doctor: "+("WARN" if issues else "OK"))
    for issue in issues: print(f"- {issue}")
    return 1 if issues else 0
if __name__ == "__main__": raise SystemExit(main())
