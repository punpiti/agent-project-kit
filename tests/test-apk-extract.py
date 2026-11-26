#!/usr/bin/env python3
"""apk extract cache contract, the extract-first hook, tool discovery and the
academic review signals added for the 2026-11-26 extract-first field note."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXTRACT = ROOT / "scripts" / "apk_extract.py"
HOOK = ROOT / "scripts" / "hooks" / "extract_first_hook.py"
DISCOVER = ROOT / "scripts" / "discover_tools.py"
CHECKER = ROOT / "scripts" / "check_prose_style.py"


def make_pdf(path: Path, pages: list[str]) -> None:
    """A minimal valid PDF with one Helvetica text line per page."""
    objects = ["<< /Type /Catalog /Pages 2 0 R >>", None,
               "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"]
    kids = []
    for text in pages:
        stream = f"BT /F1 18 Tf 72 720 Td ({text}) Tj ET"
        objects.append(f"<< /Length {len(stream)} >>\nstream\n{stream}\nendstream")
        content = len(objects)
        objects.append(f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
                       f"/Resources << /Font << /F1 3 0 R >> >> /Contents {content} 0 R >>")
        kids.append(f"{len(objects)} 0 R")
    objects[1] = f"<< /Type /Pages /Kids [{' '.join(kids)}] /Count {len(kids)} >>"
    out = bytearray(b"%PDF-1.4\n")
    offsets = []
    for number, body in enumerate(objects, 1):
        offsets.append(len(out))
        out += f"{number} 0 obj\n{body}\nendobj\n".encode("latin-1")
    xref = len(out)
    out += f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode()
    for offset in offsets:
        out += f"{offset:010d} 00000 n \n".encode()
    out += f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode()
    path.write_bytes(bytes(out))


def run(args, env, stdin=None):
    return subprocess.run([sys.executable, "-B", *map(str, args)], capture_output=True, text=True,
                          env=env, input=stdin)


def hook(event: dict, env) -> dict | None:
    out = run([HOOK], env, json.dumps(event)).stdout.strip()
    return json.loads(out) if out else None


def main() -> int:
    have_pymupdf = subprocess.run([sys.executable, "-c", "import pymupdf"], capture_output=True).returncode == 0
    if not (shutil.which("pdftotext") or have_pymupdf):
        print("SKIP test-apk-extract: neither poppler pdftotext nor PyMuPDF is available")
        return 0
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        env = {**os.environ, "APK_CACHE_ROOT": str(tmp / "cache")}
        env.pop("APK_EXTRACT_FIRST", None)
        pdf = tmp / "Long Source Name (2024).pdf"
        make_pdf(pdf, ["Alpha page one", "Bravo page two", "Charlie page three"])

        miss = run([EXTRACT, pdf, "--check"], env)
        assert miss.returncode == 3 and miss.stdout.strip() == "miss", miss

        made = json.loads(run([EXTRACT, pdf, "--pages", "1-2", "--json"], env).stdout)
        assert made["status"] == "created", made
        directory = Path(made["dir"])
        assert directory.parent == tmp / "cache" / "extract", directory
        assert directory.name.endswith("-" + made["sha256"][:12]), directory
        index = (directory / "INDEX.md").read_text(encoding="utf-8")
        for field in ("source:", "source_sha256: " + made["sha256"], "extractor:", "pages: 1-2", "page_count: 3"):
            assert field in index, field
        text = (directory / "text.md").read_text(encoding="utf-8")
        assert "<!-- page 1 -->" in text and "Bravo" in text and "Charlie" not in text, text

        partial = run([EXTRACT, pdf, "--pages", "3", "--check"], env)
        assert partial.returncode == 3 and partial.stdout.startswith("partial"), partial
        extended = json.loads(run([EXTRACT, pdf, "--pages", "3", "--json"], env).stdout)
        assert extended["status"] == "extended" and extended["dir"] == str(directory), extended
        assert "pages: 1-3" in (directory / "INDEX.md").read_text(encoding="utf-8")
        assert "Charlie" in (directory / "text.md").read_text(encoding="utf-8")

        moved = tmp / "renamed.pdf"
        shutil.copy(pdf, moved)
        hit = json.loads(run([EXTRACT, moved, "--json"], env).stdout)
        assert hit["status"] == "hit" and hit["dir"] == str(directory), hit
        bad = run([EXTRACT, pdf, "--pages", "9"], env)
        assert bad.returncode == 1 and "outside 1-3" in bad.stderr, bad
        via_apk = run([ROOT / "scripts" / "apk.py", "extract", pdf, "--check"], env)
        assert via_apk.returncode == 0 and str(directory) in via_apk.stdout, via_apk

        # Hook: cached text denies raw reads; rendering and kit tools pass; misses get a hint.
        denied = hook({"tool_name": "Read", "tool_input": {"file_path": str(pdf)}, "cwd": str(tmp)}, env)
        decision = denied["hookSpecificOutput"]
        assert decision["permissionDecision"] == "deny" and str(directory / "text.md") in decision["permissionDecisionReason"]
        bash = hook({"tool_name": "Bash", "tool_input": {"command": f"pdftotext -layout renamed.pdf - | grep x"},
                     "cwd": str(tmp)}, env)
        assert bash["hookSpecificOutput"]["permissionDecision"] == "deny", bash
        for allowed in (f"pdftoppm -png -f 1 -l 1 '{pdf}' out", f"python3 scripts/apk.py extract '{pdf}'",
                        "ls *.pdf", "cat notes.md"):
            assert hook({"tool_name": "Bash", "tool_input": {"command": allowed}, "cwd": str(tmp)}, env) is None, allowed
        other = tmp / "uncached.pdf"
        make_pdf(other, ["Delta"])
        hint = hook({"tool_name": "Read", "tool_input": {"file_path": str(other)}, "cwd": str(tmp)}, env)
        assert "permissionDecision" not in hint["hookSpecificOutput"], hint
        assert "apk.py extract" in hint["hookSpecificOutput"]["additionalContext"], hint
        assert hook({"tool_name": "Read", "tool_input": {"file_path": str(pdf)}, "cwd": str(tmp)},
                    {**env, "APK_EXTRACT_FIRST": "off"}) is None
        (tmp / ".ai").mkdir()
        (tmp / ".ai" / "extract-first-hook.off").write_text("", encoding="utf-8")
        assert hook({"tool_name": "Read", "tool_input": {"file_path": str(pdf)}, "cwd": str(tmp)}, env) is None
        broken = subprocess.run([sys.executable, "-B", str(HOOK)], input="not json", capture_output=True, text=True)
        assert broken.returncode == 0 and not broken.stdout, broken
        settings = json.loads((ROOT / "templates" / "claude" / "extract-first-hook.settings.json").read_text())
        assert "extract_first_hook.py" in settings["hooks"]["PreToolUse"][0]["hooks"][0]["command"]

        # Tool discovery: env-only tools are reported with their environment.
        fake_root = tmp / "conda"
        tool = fake_root / "envs" / "text" / "bin" / "fake-pandoc-apk"
        tool.parent.mkdir(parents=True)
        tool.write_text("#!/bin/sh\n", encoding="utf-8")
        tool.chmod(0o755)
        denv = {**env, "CONDA_ROOT": str(fake_root), "CONDA_PREFIX": "", "MAMBA_ROOT_PREFIX": ""}
        found = json.loads(run([DISCOVER, "fake-pandoc-apk", "--modules", "--json"], denv).stdout)
        assert found["tools"]["fake-pandoc-apk"] == [{"path": str(tool), "env": "text"}], found
        resources = tmp / "LOCAL_RESOURCES.md"
        resources.write_text("# LOCAL_RESOURCES\n\n- keep me\n", encoding="utf-8")
        for _ in range(2):  # idempotent block replacement
            run([DISCOVER, "fake-pandoc-apk", "--modules", "--write", resources], denv)
        body = resources.read_text(encoding="utf-8")
        assert "- keep me" in body and body.count("BEGIN apk:tool-locations") == 1, body
        assert f"`{tool}` | text" in body, body

        # Academic review signals: report, never fail; general profile unaffected.
        prose = tmp / "draft.md"
        prose.write_text("เราทดสอบเพียงสามสถานี\nข้อมูลเพียงพอสำหรับการวิเคราะห์\n"
                         "This is merely a baseline.\nResults for RQ2 follow.\n", encoding="utf-8")
        academic = run([CHECKER, prose, "--profile", "academic"], env).stdout
        assert "[review] self-diminishing wording" in academic and "lines [1, 3]" in academic, academic
        assert "[review] floating code label" in academic, academic
        assert "self-diminishing" not in run([CHECKER, prose], env).stdout

    for doc, needle in (("DATA_FLOW_POLICY.md", "## Extraction Cache Contract"),
                        ("AGENTS.md", "### Before Declaring a Tool Missing"),
                        ("AGENTS.md", "prompts/snippets/EXTRACT_FIRST_BRIEF.md"),
                        ("prompts/prose-genres/academic.md", "templates/citation-audit.md"),
                        ("templates/citation-audit.md", "CANNOT CHECK")):
        assert needle in (ROOT / doc).read_text(encoding="utf-8"), (doc, needle)
    print("apk extract tests: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
