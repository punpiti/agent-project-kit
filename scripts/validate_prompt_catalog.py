#!/usr/bin/env python3
"""Validate prompt catalog coverage, paths, roles, and composition metadata."""
from __future__ import annotations
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROMPTS = ROOT / "prompts"

def main() -> int:
    data = json.loads((PROMPTS / "catalog.json").read_text(encoding="utf-8"))
    entries = data.get("prompts", []); errors=[]
    paths=[entry.get("path") for entry in entries]
    if len(paths) != len(set(paths)): errors.append("duplicate catalog path")
    actual={p.name for p in PROMPTS.glob("*.md")}; catalog=set(paths)
    for missing in sorted(actual-catalog): errors.append(f"uncataloged prompt: {missing}")
    for missing in sorted(catalog-actual): errors.append(f"missing prompt file: {missing}")
    allowed={"primary","secondary","one-time","reference"}
    for entry in entries:
        path=entry.get("path","<unknown>")
        if entry.get("type") not in allowed: errors.append(f"invalid type: {path}")
        if not entry.get("cadence"): errors.append(f"missing cadence: {path}")
        if not entry.get("trigger"): errors.append(f"missing trigger: {path}")
        if entry.get("type") == "primary" and not entry.get("route"): errors.append(f"primary missing route: {path}")
    routes=[e.get("route") for e in entries if e.get("type")=="primary"]
    if len(routes)!=8 or len(routes)!=len(set(routes)): errors.append("catalog must define exactly eight unique primary routes")
    if data.get("composition",{}).get("secondary_max") != 2: errors.append("secondary_max must be 2")
    if errors:
        print("prompt catalog: FAIL"); [print(f"- {e}") for e in errors]; return 1
    print(f"prompt catalog: PASS ({len(entries)} prompts, {len(routes)} primary routes)"); return 0
if __name__ == "__main__": raise SystemExit(main())
