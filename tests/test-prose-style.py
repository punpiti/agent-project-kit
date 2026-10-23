#!/usr/bin/env python3
"""Regression tests for scripts/check_prose_style.py."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "scripts" / "check_prose_style.py"
PROSE_PROMPT = ROOT / "prompts" / "24_PROSE_STYLE.md"
GENRES = ROOT / "prompts" / "prose-genres"
BOOK_PROMPT = ROOT / "prompts" / "22_BOOK_WRITING.md"
BOOK_PROFILE = ROOT / "templates" / "BOOK_WRITING_PROFILE.md"
BOOK_GUIDE = ROOT / "templates" / "NEW_BOOK_START_GUIDE.md"


def run_checker(text: str, *args: str) -> subprocess.CompletedProcess[str]:
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".md", encoding="utf-8", delete=False
    ) as handle:
        handle.write(text)
        path = Path(handle.name)
    try:
        return subprocess.run(
            [sys.executable, str(CHECKER), str(path), *args],
            encoding="utf-8",
            capture_output=True,
            check=False,
            timeout=5,
        )
    finally:
        path.unlink()


def expect_exit(expected: int, text: str, *args: str) -> str:
    result = run_checker(text, *args)
    assert result.returncode == expected, result.stdout + result.stderr
    return result.stdout


expect_exit(0, "The measurements support the stated conclusion.\n")
expect_exit(1, "This is not a defect, but a feature.\n")

# The prose gate must retain the reader-readiness contract even though the
# executable checker only measures sentence-level style signals.
for path in (PROSE_PROMPT, BOOK_PROMPT, BOOK_PROFILE, BOOK_GUIDE):
    content = path.read_text(encoding="utf-8")
    assert "prerequisite" in content, path
    assert "คำแนะนำก่อนอ่าน" in content, path
prose_contract = PROSE_PROMPT.read_text(encoding="utf-8")
checker_contract = CHECKER.read_text(encoding="utf-8")
assert "does not determine whether AI generated any text" in checker_contract
for status in ("confirmed", "uncertain", "missing"):
    assert status in prose_contract, status
# The academic gate moved to its genre overlay; the core must still route to it.
academic_contract = (GENRES / "academic.md").read_text(encoding="utf-8")
for scientific_contract in (
    "Scientific-reporting and trust gate",
    "provenance เป็น justification",
    "แยก reproducibility ออกจาก validity",
    "แยก AI disclosure จาก Methods",
    "ตรวจ lineage ก่อนเกลาภาษา",
):
    assert scientific_contract in academic_contract, scientific_contract
    assert scientific_contract not in prose_contract, scientific_contract
for genre in ("academic", "social", "exam", "web"):
    overlay = f"prompts/prose-genres/{genre}.md"
    assert overlay in prose_contract, overlay
    assert f"--profile {genre}" in (ROOT / overlay).read_text(encoding="utf-8"), overlay
# Personal taste stays out of the public overlays.
assert "APK_VOICE_PROFILE_DIR" in prose_contract
social_contract = (GENRES / "social.md").read_text(encoding="utf-8")
for gate in ("ไม่ชี้ตัวบุคคลในทางลบ", "แยกข้อเท็จจริงกับความเห็น", "ระวังทัวร์ลง"):
    assert gate in social_contract, gate
book_contract = BOOK_PROMPT.read_text(encoding="utf-8")
for column in ("สำคัญเพราะอะไร", "ใช้ในบท/แนวคิดใด", "วิธีตรวจความพร้อม", "ทางปรับพื้นหรือ pre-reading"):
    assert column in book_contract, column

# Contrast framing that the first release missed (found in real reader copy).
for framing in (
    "AI เปิดตรวจสไลด์ที่ได้จริง ไม่ใช่แค่บอกว่าทำเสร็จแล้ว\n",
    "งานนี้ไม่ใช่เพียงเอกสารฉบับหนึ่ง\n",
    "This is not just a checker.\n",
    "It works, not merely compiles.\n",
):
    expect_exit(1, framing)
# Plain negation is not framing and must pass.
for plain in (
    "ไฟล์นี้ไม่ใช่ UTF-8 จึงต้องแปลงก่อน\n",
    "The value is not zero.\n",
    "The file is ready: it is in the folder.\n",
    "It is not available; see the runbook.\n",
):
    out = expect_exit(0, plain)
    assert "[FIX]" not in out, out
# "is not X; it is Y" is a review signal, never an automatic failure on its own.
reframe = expect_exit(0, "It is not about speed; it is about trust.\n")
assert '[chk] "is not X; it is Y": 1' in reframe, reframe

bold_output = expect_exit(1, "This is **the key finding** in the paper.\n")
assert "[FIX] bold inside running text: 1" in bold_output, bold_output

# Markdown headings, label-style bold, and fenced code are outside running prose.
expect_exit(
    0,
    "# **Results**\n\n**Term:** definition\n\n```text\nnot noise, but signal?\n```\n",
)

# Markdown table separators and horizontal rules are markup, not em dashes.
expect_exit(
    0,
    "| Measure | Result |\n|---|---:|\n| Accuracy | 95% |\n\n---\n***\n___\n- - -\n",
    "--strict",
)

# A prose triple dash must remain visible, and a long malformed separator must
# complete within the subprocess timeout instead of triggering regex blow-up.
expect_exit(1, "Words --- more words.\n", "--strict")
expect_exit(0, "|" + "-" * 100_000 + "x\n")

dense_semicolons = "One clause; another clause; a third clause.\n"
expect_exit(0, dense_semicolons)
expect_exit(1, dense_semicolons, "--strict")

# Internal process language is a semantic-review signal, not an AI verdict and
# not an automatic failure, even in strict mode.
process_output = expect_exit(
    0,
    "The archived workflow produced values in the analysis cache. "
    "Its caption summarizes the sequence.\n",
    "--strict",
)
assert "[review] internal artifact named instead of research object: 2" in process_output
assert "[review] method deferred to notebook or caption: 1" in process_output

# Labels in callouts and list items, and image alt text, are not running prose
# (false positives found on a real textbook chapter).
expect_exit(0, "> **โจทย์:** จงหาน้ำหนักบนดวงจันทร์\n\n- **Given:** mass 454 kg\n")
expect_exit(0, "![Lecture — Slide 3](slides/Slide3.JPG)\n" * 5, "--strict")
expect_exit(1, "> The result is **the key finding** here.\n")
title_out = expect_exit(0, "**Couette Flow — velocity gradient and shear stress**\n")
assert "[review] whole bold line (title or emphasized sentence?): 1" in title_out, title_out
# A Thai bold sentence has no period, so it is surfaced for review, never
# passed silently; a bold FAQ question is a title (review findings).
thai_out = expect_exit(0, "**ผลการทดลองยืนยันว่าการรักษาช่วยเพิ่มอัตรารอดชีวิต**\n", "--profile", "academic")
assert "[review] whole bold line" in thai_out, thai_out
faq_out = expect_exit(0, "**What Is Fluid Mechanics?**\n", "--profile", "web")
assert "[review] whole bold line" not in faq_out, faq_out
# A bold sentence is emphasis even when it fills the line (review finding).
expect_exit(1, "**The treatment significantly improves survival.**\n")

# Genre profiles relax only what the genre needs.
question = "เคยสงสัยไหมว่าทำไมน้ำถึงไหล?\n"
expect_exit(1, question)
expect_exit(1, question, "--profile", "academic")
for profile in ("social", "exam", "web"):
    expect_exit(0, question, "--profile", profile)
negated_stem = "Which of the following is **not** a property of fluids?\n"
expect_exit(0, negated_stem, "--profile", "exam")
expect_exit(0, "ข้อใด**ไม่**ใช่สมบัติของของไหล\n", "--profile", "exam")
expect_exit(1, negated_stem, "--profile", "social")
# Exam allows bold only on the negation, not on any word (review finding).
expect_exit(1, "Which result is **correct**?\n", "--profile", "exam")
# A wholly bold stem is not a FAQ title in an exam (review finding).
expect_exit(1, "**Which result is correct?**\n", "--profile", "exam")
expect_exit(0, "**Which result is correct?**\n", "--profile", "web")
# Formulaic framing stays a failure in every genre.
for profile in ("general", "academic", "social", "exam", "web"):
    expect_exit(1, "This is not just a post.\n", "--profile", profile)
# Scientific review phrases are reported only where they apply.
artifact = "The archived workflow produced values in the analysis cache.\n"
assert "[review]" in expect_exit(0, artifact, "--profile", "academic")
assert "[review]" not in expect_exit(0, artifact, "--profile", "social")
# Rate thresholds follow the profile in strict mode.
dashes = "Water flows — fast — when the slope — rises steeply here — in spring.\n" * 3
expect_exit(1, dashes, "--strict")
web_labels = "Price: free entry. Hours: nine to five. Venue: main hall.\n"
expect_exit(1, web_labels, "--strict")
expect_exit(0, web_labels, "--strict", "--profile", "web")

print("prose style checker tests: PASS")
