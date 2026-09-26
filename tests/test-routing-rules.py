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


def write_document(directory: Path, name: str, body: str) -> Path:
    """A document on disk, so the detector is exercised the way callers use it."""
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / name
    path.write_text(body, encoding="utf-8")
    return path


SECTIONS = """# {title}
{header}
## Abstract
text
## Introduction
text
## Related Work
text
## Method
text
## Results
text
## References
text
"""


def check_documents() -> None:
    """Structure says what a file is; nothing on disk says what to do with it."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        published_header = "Proceedings of IEEE ICRA. DOI: 10.1109/x\nCopyright © 2024 IEEE."
        own = write_document(root / "01_working_text", "report.md",
                             SECTIONS.format(title="My Course Report", header=""))
        filed = write_document(root / "02_references", "smith.md",
                               SECTIONS.format(title="Someone Else", header=""))
        loose = write_document(root, "loose.md",
                               SECTIONS.format(title="Someone Else", header=published_header))
        notes = write_document(root, "notes.md", "# Notes\nResults show it is fast.\n")

        vague, ask = "ดูไฟล์นี้ให้หน่อย", "ตรวจไฟล์นี้ให้หน่อย"

        # No file selects the review by itself. The draft may be finished, the
        # paper already published, the work someone else's: the agent asks.
        for path in (own, filed, loose):
            route = route_task.classify(vague, None, [path])
            assert route["workflow"]["stages"] == [], (path, route)
            assert route["needs_clarification"], (path, route)
            assert route["clarification_reasons"], (path, route)
            # Naming the file as the thing to review is the deliberate ask.
            asked = route_task.classify(ask, None, [path])
            assert asked["workflow"]["stages"] == ["thesis-review"], (path, asked)
            assert asked["clarification_reasons"] == [], (path, asked)

        # A numbered folder is still that folder, and publication marks travel
        # with the file wherever it sits.
        assert route_task.classify(vague, None, [filed])["documents"][0]["in_reference_dir"]
        assert route_task.classify(vague, None, [loose])["documents"][0]["finished_or_external"]
        assert not route_task.classify(vague, None, [own])["documents"][0]["finished_or_external"]

        # Prose that merely starts with a section word is not a research report,
        # and must not raise a question of its own.
        quiet = route_task.classify(vague, None, [notes])
        assert not quiet["documents"][0]["research_document"], quiet
        assert quiet["clarification_reasons"] == [], quiet

        # An unreadable path is reported, not guessed at.
        missing = route_task.classify(vague, None, [root / "gone.md"])["documents"][0]
        assert missing["readable"] is False and missing["research_document"] is False, missing


def main() -> None:
    assert route_task.validate_rules() == [], route_task.validate_rules()
    check_documents()

    expect("in both", lambda r: r["axes"]["domain"]["research"].append("website"))
    expect("duplicate phrase", lambda r: r["phrases"]["secret_check"].append("Secret"))
    expect("invalid phrase", lambda r: r["phrases"]["prose_writing"].append(" draft"))
    expect("must be a non-empty list", lambda r: r["phrases"].update(machine_needed=[]))
    expect("unknown domain", lambda r: r["strong_domains"].append({"id": "astrology", "phrases": ["x"]}))
    expect("unknown deliverable", lambda r: r["strong_outputs"][0].update(id="poem"))
    expect("not in axes", lambda r: r["preferred_deliverable"].update(software="poem"))
    expect("document_signals.research_report.abstract",
           lambda r: r["document_signals"]["research_report"].update(abstract=[]))
    expect("document_signals.reference_paths",
           lambda r: r["document_signals"].update(reference_paths=["  "]))
    expect("minimum_sections", lambda r: r["document_signals"].update(minimum_sections=99))
    expect("published_marker_limit", lambda r: r["document_signals"].update(published_marker_limit=0))
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
