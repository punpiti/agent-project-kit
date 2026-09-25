#!/usr/bin/env python3
"""Generate or verify compatibility views from the v2 workflow registry."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGISTRY_PATH = ROOT / "config" / "workflow-registry.json"


def dump(data: object) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"


def projections(registry: dict) -> dict[Path, dict]:
    routes: dict[str, dict] = {}
    deliverables = {
        "code": "working software or code change",
        "analysis": "analysis or evidence-backed finding",
        "paper": "academic manuscript or reviewer response",
        "book": "book or textbook manuscript",
        "policy": "policy, governance decision, or institutional proposal",
        "presentation": "slides, talk, briefing, or pitch",
        "course-material": "lesson, syllabus, exercise, assessment, or teaching asset",
        "document": "formal document, correspondence, dossier, or report",
        "decision": "recommendation or decision brief",
    }
    methods = {
        "content-analysis": "systematic coding or interpretation of a corpus",
        "data-analytics": "data validation, metrics, statistics, or visualization",
        "web-development": "browser, frontend, backend web API, accessibility, or web performance",
        "research-synthesis": "literature, external evidence, or source synthesis",
        "strategy-advisory": "option comparison, advising, or direction setting",
    }
    for pipeline_id, item in registry["primary_pipelines"].items():
        projected = {k: item[k] for k in ("label", "prompt", "instruction")}
        projected["pipeline_id"] = pipeline_id
        for key in item["compatibility_keys"]:
            routes[key] = projected
    workflows = {}
    for kind, items in registry["modules"].items():
        for module_id, item in items.items():
            workflows[module_id] = {**item, "kind": kind.replace("_", "-")}
    inventory = []
    for item in registry["prompt_inventory"]:
        entry = {"path": item["path"], "type": item["legacy_type"], "role": item["role"]}
        if "route" in item:
            entry["route"] = item["route"]
        entry.update({"cadence": item["cadence"], "trigger": item["trigger"]})
        inventory.append(entry)
    catalog = {
        "schema_version": 2,
        "generated_from": "config/workflow-registry.json",
        "composition": registry["composition"],
        "prompts": inventory,
    }
    route_view = {
        "schema_version": 2,
        "generated_from": "config/workflow-registry.json",
        "routes": routes,
        "deliverables": deliverables,
        "methods": methods,
        "lifecycles": ["bootstrap", "resume", "create", "implement", "review", "publish", "monitor"],
    }
    workflow_view = {
        "schema_version": 2,
        "generated_from": "config/workflow-registry.json",
        "workflows": workflows,
        "one_time": [
            item["prompt"] for item in registry["modules"]["state_actions"].values()
            if item["prompt"] and item["cadence"].startswith("once")
        ],
    }
    policy_view = {
        "schema_version": 2,
        "generated_from": "config/workflow-registry.json",
        "policies": registry["policies"],
        "always": registry["always_policies"],
    }
    return {
        ROOT / "prompts" / "catalog.json": catalog,
        ROOT / "config" / "routes.json": route_view,
        ROOT / "config" / "workflows.json": workflow_view,
        ROOT / "config" / "policies.json": policy_view,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="rewrite generated compatibility files")
    args = parser.parse_args()
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    errors = []
    for path, data in projections(registry).items():
        expected = dump(data)
        if args.write:
            path.write_text(expected, encoding="utf-8", newline="\n")
        elif not path.exists() or path.read_text(encoding="utf-8") != expected:
            errors.append(path.relative_to(ROOT).as_posix())
    if errors:
        print("workflow registry projections: FAIL")
        for path in errors:
            print(f"- stale generated file: {path}")
        return 1
    print("workflow registry projections: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
