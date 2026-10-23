#!/usr/bin/env python3
"""Related-Markdown lookup: finds earlier-session notes, ignores noise."""
from __future__ import annotations
import hashlib, json, os, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.dont_write_bytecode = True


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        os.environ["APK_CACHE_ROOT"] = str(tmp / "cache")
        os.environ.pop("APK_PDF_FIGURE_CACHE", None)
        import md_index

        project = tmp / "project"
        write(project / ".ai/PROJECT_STATE.md", "# PROJECT_STATE\nBernoulli\n")
        write(project / "references/reading-cache/PDF_READING_CACHE_white_ch3.md",
              "# Reading cache: White chapter 3\n## 3.1 กลศาสตร์ของไหล เบื้องต้น\n## 3.2 Bernoulli equation\n")
        write(project / "references/reading-cache/EVIDENCE_2.4.md",
              "# Evidence 2.4 ความหนืด\n## นิยามความหนืด\n")
        write(project / "notes/budget.md", "# รายได้ประจำปี\n## งบประมาณ\n")
        write(project / "notes/agenda.md", "# Meeting agenda\n## เอกสารประกอบ\n## ไฟล์แนบ\n")
        write(project / "notes/code.md", "# Notes\n```\n# Bernoulli inside code\n```\n")
        write(project / ".ai/agent-project-kit/AGENTS.md", "# Kit\n## Bernoulli\n")
        write(project / ".ai/archive/legacy-md/2026-01-01/plan.md", "# Old plan bernoulli\n")
        source = project / "white-2011.pdf"
        source.write_bytes(b"fake pdf bytes")
        sha12 = hashlib.sha256(source.read_bytes()).hexdigest()[:12]
        write(project / f"references/pdf-figures/white-2011-{sha12}/manifest.json", "{}")
        write(project / f"references/pdf-figures/white-2011-{sha12}/INDEX.md", "# PDF figures white\n")
        write(project / "references/pdf-figures/white-2011-000000000000/manifest.json", "{}")
        write(project / "references/pdf-figures/white-2011-000000000000/INDEX.md", "# PDF figures white old\n")

        def paths(request: str, files=None) -> list[str]:
            return [f["path"] for f in md_index.related(request, project, files)["files"]]

        # Must find: English heading, Thai fragment containing a stopword
        # ("ของ" in "ของไหล"), Thai title, and a Thai word ending in "ได้".
        assert paths("explain the Bernoulli equation")[:1] == [
            "references/reading-cache/PDF_READING_CACHE_white_ch3.md"]
        assert "references/reading-cache/PDF_READING_CACHE_white_ch3.md" in paths("เขียนหัวข้อกลศาสตร์ของไหลต่อ")
        assert paths("อธิบายความหนืดให้หน่อย")[:1] == ["references/reading-cache/EVIDENCE_2.4.md"]
        assert paths("สรุปรายได้") == ["notes/budget.md"]

        # Must not find: generic wording, unrelated requests, kit snapshot,
        # headings inside code blocks, PROJECT_STATE (already bundled). Archived
        # notes are penalized, not excluded: a one-word match drops below the
        # threshold, a request that names the old note still finds it.
        assert paths("ช่วยดูไฟล์เอกสารนี้ให้หน่อย") == []
        assert paths("fix the website login bug") == []
        found = paths("bernoulli")
        assert not any(p.startswith(".ai/") or p == "notes/code.md" for p in found), found
        archived = ".ai/archive/legacy-md/2026-01-01/plan.md"
        assert archived in paths("old plan bernoulli")
        ranked = {f["path"]: f["score"] for f in md_index.related("old plan bernoulli", project)["files"]}
        assert ranked[archived] == 7.0, ranked  # 3 title terms x 3, minus the archive penalty

        # Private areas from the release boundary are never indexed (review finding).
        write(project / "private/customers.private.md", "# Customer renewal confidential Alice\n")
        write(project / "internal/plan.md", "# Customer renewal internal\n")
        write(project / "notes/renewal.private.md", "# Customer renewal private\n")
        assert paths("customer renewal confidential") == []

        # A supplied source file finds its hash-keyed cache first; a same-name
        # cache with another hash is offered only as possibly stale.
        result = md_index.related("ดึงรูปจากไฟล์นี้", project, [source])["files"]
        assert result[0]["path"].endswith(f"white-2011-{sha12}/INDEX.md"), result
        assert "cache of supplied file" in result[0]["reasons"][0]
        assert "may be stale" in result[1]["reasons"][0]

        # A cache outside the project (the policy's hot tier) is found by the
        # supplied file's hash without indexing other projects' caches.
        outside = tmp / "cache" / "extract" / f"white-2011-{sha12}"
        write(outside / "INDEX.md", "# White 2011 text extract\n")
        hits = md_index.related("ดึงข้อความจากไฟล์นี้", project, [source])["files"]
        assert any(f["path"] == str(outside / "INDEX.md") for f in hits), hits

        # Reading is bounded per call (review findings): files whose path matches
        # or that are evidence/cache/.ai notes up to the budget, other files only
        # up to the small discovery allowance; the rest match by path until read.
        crowd = tmp / "crowd"
        write(crowd / ".ai/PROJECT_STATE.md", "# state\n")
        for i in range(30):
            write(crowd / f"notes/note{i:02d}.md", f"# Note {i}\n## Topic {i}\n")
        write(crowd / "notes/zz-bernoulli.md", "# Zeta\n## Bernoulli equation\n")
        os.environ["APK_MD_INDEX_DISCOVERY"] = "2"
        first = md_index.related("explain bernoulli", crowd)
        assert first["reparsed"] == 3 and first["unread_files"] == 28, first
        assert [f["path"] for f in first["files"]] == ["notes/zz-bernoulli.md"], first
        assert md_index.related("fix login bug", crowd)["reparsed"] == 2
        assert md_index.build(crowd, budget=-1)["unparsed"] == 0
        os.environ.pop("APK_MD_INDEX_DISCOVERY")

        # A cache folder's hash is known before its INDEX.md is read, and a cache
        # found both in the index and by direct lookup is listed once.
        late = tmp / "late"
        write(late / ".ai/PROJECT_STATE.md", "# state\n")
        write(late / f"references/pdf-figures/white-{sha12}/INDEX.md", "# figures\n")
        os.environ["APK_MD_INDEX_READ_BUDGET"] = "0"
        os.environ["APK_MD_INDEX_DISCOVERY"] = "0"
        renamed = tmp / "renamed.pdf"
        renamed.write_bytes(source.read_bytes())
        late_hits = md_index.related("ดึงรูปจากไฟล์นี้", late, [renamed])["files"]
        os.environ.pop("APK_MD_INDEX_READ_BUDGET"); os.environ.pop("APK_MD_INDEX_DISCOVERY")
        assert [f["path"] for f in late_hits][:1] == [f"references/pdf-figures/white-{sha12}/INDEX.md"], late_hits
        os.environ["APK_PDF_FIGURE_CACHE"] = str(outside.parent)
        both = [f["path"] for f in md_index.related("ดึงข้อความจากไฟล์นี้", project, [source])["files"]]
        os.environ.pop("APK_PDF_FIGURE_CACHE")
        target = (outside / "INDEX.md").resolve()
        assert sum(Path(x).is_absolute() and Path(x).resolve() == target for x in both) == 1, both

        # A symlink into a private area is judged by its target (review finding).
        alias = project / "notes/customer.md"
        try:
            alias.symlink_to(project / "private/customers.private.md")
        except OSError:
            alias = None
        if alias is not None:
            assert paths("customer renewal confidential") == []
            # A cache found by hash is held to the same rule (review finding).
            linked = tmp / "cache" / "extract" / f"linked-{sha12}"
            linked.mkdir(parents=True)
            (linked / "INDEX.md").symlink_to(project / "private/customers.private.md")
            hits = [f["path"] for f in md_index.related("ดึงข้อความจากไฟล์นี้", project, [source])["files"]]
            assert not any("linked-" in h for h in hits), hits

        # Incremental: unchanged files are not re-read; a changed file is.
        assert md_index.build(project)["reparsed"] == 0
        write(project / "notes/budget.md", "# รายได้ประจำปี\n## Viscosity table\n")
        assert md_index.build(project)["reparsed"] == 1
        assert md_index.index_path(project).is_relative_to(tmp / "cache")

        # The context bundle carries pointers, not content, within its budget.
        # context.py exits 2 when the request needs clarification; still valid.
        def context(*args: str) -> dict:
            run = subprocess.run([sys.executable, str(ROOT / "scripts/context.py"), *args,
                                  "--project", str(project)], capture_output=True, env=os.environ)
            assert run.returncode in (0, 2), run.stderr
            return json.loads(run.stdout)
        bundle = context("explain the Bernoulli equation", "--max-bytes", "12000")
        related = bundle["related_markdown"]
        assert related["files"][0]["path"].endswith("PDF_READING_CACHE_white_ch3.md")
        assert "Reading cache" not in json.dumps(bundle["project_context"])
        assert bundle["metrics"]["bytes"] <= 12000
        assert "related_markdown" not in context("explain Bernoulli", "--no-markdown-index")

        # A private reference map for the routed pipeline is listed by path,
        # never by content, and only for that pipeline.
        refs = tmp / "refs"
        write(refs / "book-writing.md", "# REFERENCE_MAP — book-writing\nsecret-path-detail\n")
        os.environ["APK_REFERENCE_DIR"] = str(refs)
        book_bundle = context("draft chapter 3 prose of the book")
        assert book_bundle["reference_maps"] == [str(refs / "book-writing.md")], book_bundle.get("reference_maps")
        assert "secret-path-detail" not in json.dumps(book_bundle, ensure_ascii=False)
        assert "reference_maps" not in context("fix the website login bug")
        write(refs / "common.md", "# common\n")
        assert len(context("draft chapter 3 prose of the book")["reference_maps"]) == 2
        os.environ.pop("APK_REFERENCE_DIR")
    print("markdown index tests: PASS")


if __name__ == "__main__":
    main()
