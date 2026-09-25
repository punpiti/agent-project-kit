#!/usr/bin/env python3
"""Validate the v2 registry, prompt inventory, and generated projections."""
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROMPTS = ROOT / "prompts"

def main() -> int:
    registry=json.loads((ROOT/"config"/"workflow-registry.json").read_text(encoding="utf-8"))
    data = json.loads((PROMPTS / "catalog.json").read_text(encoding="utf-8"))
    entries = data.get("prompts", []); errors=[]
    paths=[entry.get("path") for entry in entries]
    if len(paths) != len(set(paths)): errors.append("duplicate catalog path")
    actual={p.name for p in PROMPTS.glob("*.md")}; catalog=set(paths)
    for missing in sorted(actual-catalog): errors.append(f"uncataloged prompt: {missing}")
    for missing in sorted(catalog-actual): errors.append(f"missing prompt file: {missing}")
    allowed={"primary","secondary","one-time","reference"}
    roles={"primary-pipeline","method","lifecycle-stage","quality-gate","state-action","reference"}
    for entry in entries:
        path=entry.get("path","<unknown>")
        if entry.get("type") not in allowed: errors.append(f"invalid type: {path}")
        if entry.get("role") not in roles: errors.append(f"invalid v2 role: {path}")
        if not entry.get("cadence"): errors.append(f"missing cadence: {path}")
        if not entry.get("trigger"): errors.append(f"missing trigger: {path}")
        if entry.get("type") == "primary" and not entry.get("route"): errors.append(f"primary missing route: {path}")
    routes=[e.get("route") for e in entries if e.get("type")=="primary"]
    if len(routes)!=9 or len(routes)!=len(set(routes)): errors.append("catalog must define exactly nine unique primary routes")
    registered={item.get("prompt") for item in registry["primary_pipelines"].values() if item.get("prompt")}
    for group in registry["modules"].values():
        registered.update(item.get("prompt") for item in group.values() if item.get("prompt"))
    catalog_paths={f"prompts/{path}" for path in catalog}
    for path in sorted(registered-catalog_paths): errors.append(f"registered prompt absent from catalog: {path}")
    if data.get("composition") != registry.get("composition"): errors.append("catalog composition differs from registry")
    rules=subprocess.run(
      [sys.executable,"-B",str(ROOT/"scripts"/"route_task.py"),"--validate"],
      text=True,capture_output=True,check=False)
    if rules.returncode:
        errors.extend(line for line in rules.stdout.splitlines() if not line.endswith(("PASS","FAIL")))
    projection=subprocess.run(
      [sys.executable,str(ROOT/"scripts"/"sync_workflow_registry.py")],
      text=True,capture_output=True,check=False)
    if projection.returncode: errors.append("generated workflow projections are stale")
    if errors:
        print("prompt catalog: FAIL"); [print(f"- {e}") for e in errors]; return 1
    print(f"prompt catalog: PASS ({len(entries)} prompts, {len(routes)} primary routes)"); return 0
if __name__ == "__main__": raise SystemExit(main())
