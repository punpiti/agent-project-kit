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
            assert asked["workflow"]["stages"] == ["paper-review"], (path, asked)
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

    # Prose genres: registry entries must point at real overlays, router phrase
    # lists, and deliverables, and a deliverable belongs to one genre only.
    def registry_errors(mutate) -> list[str]:
        registry = copy.deepcopy(route_task.REGISTRY)
        mutate(registry["prose_genres"])
        return route_task.validate_rules(route_task.ROUTING, registry)

    for fragment, mutate in (
        ("does not exist", lambda g: g["social"].update(overlay="prompts/prose-genres/missing.md")),
        ("not a router phrase list", lambda g: g["exam"].update(phrases="genre_poetry")),
        ("routes_to needs a phrase list", lambda g: g["academic"].update(routes_to="paper")),
        ("unknown deliverable", lambda g: g["academic"]["deliverables"].append("poem")),
        ("in both", lambda g: g["general"]["deliverables"].append("paper")),
    ):
        errors = registry_errors(mutate)
        assert any(fragment in error for error in errors), (fragment, errors)

    # A named genre selects its overlay and the prose gate; ordinary requests that
    # merely mention the web, tests, or a document do not.
    genre_cases = (
        ("ช่วยเกลาโพสต์เฟซบุ๊กนี้ให้หน่อย", "social"),
        ("draft a facebook post about water safety", "social"),
        ("ออกข้อสอบปรนัยเรื่องความหนืด 10 ข้อ", "exam"),
        ("write 5 exam questions on Bernoulli", "exam"),
        ("write website copy for the lab homepage", "web"),
        ("เขียนเนื้อหาเว็บไซต์ของภาควิชา", "web"),
        ("draft chapter 3 prose of the book", None),
        ("เกลาร้อยแก้วบทที่ 2 ของตำรา", None),
        ("revise the paper introduction", "academic"),
        ("เขียนจดหมายถึงคณบดี", "general"),
        ("fix the website login bug", None),
        ("run the unit tests", None),
        ("test the login page", None),
        ("สรุปผลวิเคราะห์ข้อมูลยอดขาย", None),
    )
    for request, genre in genre_cases:
        routed = route_task.classify(request)
        assert routed["prose_genre"] == genre, (request, routed["prose_genre"], routed["workflow"]["gates"])
        assert ("prose-style" in routed["workflow"]["gates"]) == (genre is not None), (request, routed)

    # A named genre is the output, so it also decides the deliverable and the
    # pipeline. When another output is named too, the one named first is what
    # to produce and the later one is its topic (review findings, two rounds).
    for request, deliverable, pipeline, genre in (
        ("draft a facebook post about water safety", "social-post", "general", "social"),
        ("draft a facebook post promoting my textbook", "social-post", "general", "social"),
        ("write website copy for the lab homepage", "web-copy", "general", "web"),
        ("write website copy explaining our privacy policy", "web-copy", "general", "web"),
        # Round 3: the verb's object is the output, wherever the source sits.
        ("Using this research paper, create exam questions", "course-material", "course-material-development", "exam"),
        ("จากบทความวิจัยนี้ ช่วยออกข้อสอบ 5 ข้อ", "course-material", "course-material-development", "exam"),
        ("About our privacy policy, write website copy", "web-copy", "general", "web"),
        ("write website copy about a facebook post", "web-copy", "general", "web"),
        ("ช่วยออกข้อสอบสำหรับโพสต์เฟซบุ๊ก", "course-material", "course-material-development", "exam"),
        ("write website copy for the textbook", "web-copy", "general", "web"),
        ("เขียนบทที่ 3 เรื่องข้อสอบ", "book", "book-writing", None),
        ("เขียนบทที่ 3 เรื่องแบบทดสอบ", "book", "book-writing", None),
        ("ออกข้อสอบบทที่ 3", "course-material", "course-material-development", "exam"),
        ("create exam questions for a research paper", "course-material", "course-material-development", "exam"),
        ("เกลาตำราที่มีข้อสอบ", "book", "book-writing", None),
        ("write a textbook about website copy", "book", "book-writing", None),
        ("implement a quiz API", "code", "software-development-automation", None),
        ("fix the quiz scoring bug", "code", "software-development-automation", None),
        ("write a formal letter about exam questions", "document", "administrative-professional-operations", "general"),
    ):
        routed = route_task.classify(request)
        got = (routed["deliverable"], routed["primary_pipeline"], routed["prose_genre"], routed["needs_clarification"])
        assert got == (deliverable, pipeline, genre, False), (request, got)
        assert ("implementation" in routed["workflow"]["stages"]) == (deliverable == "code"), (request, routed)
    # Two verb-led outputs in one request are a real choice: ask.
    both = route_task.classify("write a textbook and create exam questions")
    assert both["needs_clarification"] and "both" in both["clarification_reasons"][-1], both
    assert route_task.classify("ออกข้อสอบปรนัยเรื่องความหนืด")["primary_pipeline"] == "course-material-development"

    # Textbooks belong to Book Writing, which owns its prose method; academic
    # articles get the prose gate with the academic overlay. Owner rules for
    # Thai: "หนังสือเรียน"/"ตำรา" is a textbook, "หนังสือ" alone is a document,
    # "บทที่" always means the textbook unless a paper, thesis, slides, or course
    # material is named, and any other book part with a bare "หนังสือ" asks.
    for request, pipeline, genre, ask in (
        ("เขียนหนังสือเรียนวิชากลศาสตร์ของไหล", "book-writing", None, False),
        ("เกลาร้อยแก้วบทที่ 2 ของตำรา", "book-writing", None, False),
        ("เขียนบทที่ 3 ของหนังสือกลศาสตร์ของไหล", "book-writing", None, False),
        ("เกลาบทที่ 2", "book-writing", None, False),
        ("polish the preface of my textbook", "book-writing", None, False),
        ("แก้ภาษาในบทนำของหนังสือ", "administrative-professional-operations", "general", True),
        ("เขียนคำนำหนังสือ", "administrative-professional-operations", "general", True),
        ("เขียนหนังสือถึงคณบดีขอใช้ห้อง", "administrative-professional-operations", "general", False),
        ("เขียนหนังสือราชการขอใช้ห้อง", "administrative-professional-operations", "general", False),
        ("ร่างหนังสือภายในถึงภาควิชา", "administrative-professional-operations", "general", False),
        ("ทำสไลด์บทที่ 4", "presentation", None, False),
        ("เขียนบทที่ 3 เรื่องนโยบาย", "book-writing", None, False),
        ("fix the bug in chapter 3 demo code", "software-development-automation", None, False),
        ("เขียนบทที่ 3 พร้อมโค้ด Python", "book-writing", None, False),
        ("แบบฝึกหัดบทที่ 2", "course-material-development", None, False),
        ("เขียนบทที่ 2 ของวิทยานิพนธ์", "research-activities", "academic", False),
        ("เขียนบทความวิชาการลงวารสาร", "research-activities", "academic", False),
        ("แก้ abstract ให้กระชับ", "research-activities", "academic", False),
        ("write the related work section", "research-activities", "academic", False),
        ("fix the abstract class in the parser", "software-development-automation", None, False),
    ):
        routed = route_task.classify(request)
        assert routed["needs_clarification"] == ask, (request, routed)
        assert (routed["primary_pipeline"], routed["prose_genre"]) == (pipeline, genre), (request, routed)

    # Inside the kit's own source, requests name kit files to change: they route
    # to software development, never to the policy, paper, book, or post they
    # mention. The same request in an ordinary project routes by its words.
    assert route_task.kit_source(ROOT)
    for request in ("update the data flow policy for cloud drive caching",
                    "review the paper review prompt", "เขียนบทที่ 3 ของหนังสือ",
                    "write a facebook post prompt overlay"):
        routed = route_task.classify(request, ROOT)
        assert routed["primary_pipeline"] == "software-development-automation", (request, routed)
        assert routed["workflow"]["gates"] == [] and routed["selection_trace"]["self_hosted_kit"], (request, routed)
    released = route_task.classify("release the package", ROOT)["workflow"]
    assert "package-release" in released["stages"] and "release-boundary" in released["gates"], released
    with tempfile.TemporaryDirectory() as tmp:
        downstream = Path(tmp)
        (downstream / "START_HERE.md").write_text("# project\n", encoding="utf-8")
        (downstream / "manifest.json").write_text('{"name": "my-thesis"}', encoding="utf-8")
        assert not route_task.kit_source(downstream)
        routed = route_task.classify("update the data flow policy for cloud drive caching", downstream)
        assert routed["primary_pipeline"] == "educational-policy-development", routed
        assert routed["selection_trace"]["self_hosted_kit"] is False

    # The evidence-scaffold method attaches only when evidence gaps are the task.
    assert "evidence-scaffold" in route_task.classify(
        "build an evidence map for the related work section")["workflow"]["methods"]
    assert "evidence-scaffold" in route_task.classify("หาช่องว่างหลักฐานก่อนสรุปข้อเสนอ")["methods"]
    assert "evidence-scaffold" not in route_task.classify("summarize this paper")["methods"]

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
