#!/usr/bin/env python3
"""Routing vocabulary is data: validated structurally and editable without code."""
from __future__ import annotations

import copy
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location("apk_route_task", ROOT / "scripts" / "route_task.py")
assert spec and spec.loader
route_task = importlib.util.module_from_spec(spec)
spec.loader.exec_module(route_task)


def errors_after(mutate) -> list[str]:
    rules = copy.deepcopy(route_task.ROUTING)
    mutate(rules)
    return route_task.validate_rules(rules, route_task.REGISTRY)


def expect(fragment: str, mutate) -> None:
    errors = errors_after(mutate)
    assert any(fragment in error for error in errors), (fragment, errors)


def main() -> None:
    assert route_task.validate_rules() == [], route_task.validate_rules()

    expect("in both", lambda r: r["axes"]["domain"]["research"].append("website"))
    expect("duplicate phrase", lambda r: r["phrases"]["secret_check"].append("Secret"))
    expect("invalid phrase", lambda r: r["phrases"]["prose_writing"].append(" draft"))
    expect("must be a non-empty list", lambda r: r["phrases"].update(machine_needed=[]))
    expect("unknown domain", lambda r: r["strong_domains"].append({"id": "astrology", "phrases": ["x"]}))
    expect("unknown deliverable", lambda r: r["strong_outputs"][0].update(id="poem"))
    expect("not in axes", lambda r: r["preferred_deliverable"].update(software="poem"))
    expect("unregistered module", lambda r: r["method_modules"].update({"web-development": "webz"}))
    expect("no module for method", lambda r: r["method_modules"].pop("strategy-advisory"))
    expect("not used by route_task.py", lambda r: r["phrases"].update(unused_list=["x"]))
    expect("phrases.secret_check", lambda r: r["phrases"].pop("secret_check"))
    expect("source_file_pattern", lambda r: r.update(source_file_pattern="(unclosed"))
    expect("defaults.deliverable", lambda r: r["defaults"].update(deliverable="poem"))

    # Editing only the JSON changes routing: no Python edit is needed.
    with tempfile.TemporaryDirectory() as tmp:
        kit = Path(tmp)
        shutil.copytree(ROOT / "config", kit / "config")
        (kit / "scripts").mkdir()
        shutil.copy2(ROOT / "scripts" / "route_task.py", kit / "scripts" / "route_task.py")
        request = "tune the zzqx pipeline"

        def route() -> dict:
            out = subprocess.check_output(
                [sys.executable, "-B", str(kit / "scripts" / "route_task.py"), request], encoding="utf-8")
            return json.loads(out)

        assert route()["domain"] == "general"
        rules_path = kit / "config" / "routing-rules.json"
        rules = json.loads(rules_path.read_text(encoding="utf-8"))
        rules["axes"]["domain"]["software"].append("zzqx")
        rules_path.write_text(json.dumps(rules, ensure_ascii=False), encoding="utf-8")
        routed = route()
        assert (routed["domain"], routed["deliverable"], routed["primary_pipeline"]) == (
            "software", "code", "software-development-automation"), routed

    print("routing rules tests: PASS")


if __name__ == "__main__":
    main()
