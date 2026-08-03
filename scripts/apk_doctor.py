#!/usr/bin/env python3
"""Read-only consistency checks for an Agent Project Kit installation."""
from __future__ import annotations
import argparse, json, platform, re
from pathlib import Path
import datetime as dt

def field(text: str, name: str) -> str | None:
    m = re.search(rf"^- {re.escape(name)}:\s*(.+)$", text, re.MULTILINE); return m.group(1).strip() if m else None

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
    if structured and structured[:2] == ["placeholder","placeholder"]:
        print("Agent Project Kit doctor: structured state is placeholder; Markdown compatibility state remains active")
    kit=next((x for x in (root/".ai"/"agent-project-kit",root) if (x/"manifest.json").is_file()),None)
    if kit is None: issues.append("cannot find Agent Project Kit manifest")
    else:
        try: manifest=json.loads((kit/"manifest.json").read_text(encoding="utf-8"))
        except (OSError,json.JSONDecodeError) as exc: issues.append(f"invalid manifest: {exc}"); manifest={}
        vf=root/".ai"/"COMPUTING_ENVIRONMENT_VERSION.md"
        if not vf.is_file(): issues.append("missing .ai/COMPUTING_ENVIRONMENT_VERSION.md")
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
