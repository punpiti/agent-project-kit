#!/usr/bin/env python3
"""Claude Code PreToolUse hook: read cached PDF text instead of the PDF.

Fires for the main agent and its subagents, so the extract-first rule holds
even when a subagent brief never mentioned it. Install with
templates/claude/extract-first-hook.settings.json (see DATA_FLOW_POLICY.md).

- Read of a `.pdf`, or a Bash command that extracts PDF text (pdftotext,
  pdfplumber, pypdf/PyPDF2, PyMuPDF get_text), is denied when the shared cache
  already covers that PDF, and the reason names the cached text file.
- On a cache miss the call is allowed and the agent is told the one-line
  `apk.py extract` command that creates the reusable cache.
- Rendering pages for figures/layout (pdftoppm, pdf_render_pages.py,
  pdf_figures.py) and the kit's own extractors are never blocked.

Opt out: APK_EXTRACT_FIRST=off, or create `.ai/extract-first-hook.off` in the
project. Any internal error allows the call (fail open).
"""
from __future__ import annotations

import json
import os
import re
import shlex
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
KIT_SCRIPTS = HERE.parent
TEXT_TOOLS = re.compile(r"\b(pdftotext|pdfplumber|PyPDF2|pypdf|get_text\s*\(|mutool\s+(?:convert|draw)\b[^|;&]*-F\s*(?:txt|text))", re.I)
KIT_TOOLS = re.compile(r"(apk_extract\.py|apk\.py\s+extract|pdf_text_extract\.py|pdf_render_pages\.py|pdf_figures\.py)")


def pdf_paths_in(command: str, cwd: Path) -> list[Path]:
    try:
        tokens = shlex.split(command, posix=True)
    except ValueError:
        tokens = re.findall(r"[^\s'\"|;&<>]+\.pdf", command, re.I)
    out = []
    for token in tokens:
        for piece in re.findall(r"[^\s'\"|;&<>=]+\.pdf\b", token, re.I) or []:
            path = Path(os.path.expanduser(piece))
            path = path if path.is_absolute() else cwd / path
            if path.is_file() and path not in out:
                out.append(path)
        if token.lower().endswith(".pdf"):
            path = Path(os.path.expanduser(token))
            path = path if path.is_absolute() else cwd / path
            if path.is_file() and path not in out:
                out.append(path)
    return out


def decide(event: dict) -> dict | None:
    tool = event.get("tool_name")
    data = event.get("tool_input") or {}
    cwd = Path(event.get("cwd") or os.getcwd())
    if tool == "Read":
        target = str(data.get("file_path") or "")
        if not target.lower().endswith(".pdf"):
            return None
        pdfs = [Path(target)] if Path(target).is_file() else []
    elif tool == "Bash":
        command = str(data.get("command") or "")
        if not TEXT_TOOLS.search(command) or KIT_TOOLS.search(command):
            return None
        pdfs = pdf_paths_in(command, cwd)
    else:
        return None
    if not pdfs:
        return None
    sys.path.insert(0, str(KIT_SCRIPTS))
    import apk_extract  # noqa: E402

    cached, missing = [], []
    for pdf in pdfs:
        hit = apk_extract.find_hit(apk_extract.sha256_file(pdf))
        text = apk_extract.text_file(hit) if hit else None
        (cached if text else missing).append((pdf, text))
    extract_cmd = f"python3 {KIT_SCRIPTS / 'apk.py'} extract"
    if cached:
        lines = [f"{pdf.name}: text already cached at {text} (grep it; do not re-extract)."
                 for pdf, text in cached]
        lines.append("Pages not in the cache: " + extract_cmd + " FILE.pdf --pages A-B extends it.")
        lines.append("For figures or layout, render pages with "
                     f"{KIT_SCRIPTS / 'reference_extract' / 'pdf_render_pages.py'} and Read the PNG.")
        lines.append("Override for this project only if the owner asks: create .ai/extract-first-hook.off.")
        return {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                       "permissionDecisionReason": "\n".join(lines)}}
    hint = ("Extract-first (DATA_FLOW_POLICY.md): no cached text for "
            + ", ".join(pdf.name for pdf, _ in missing)
            + f". Run `{extract_cmd} FILE.pdf [--pages A-B]` once; it prints the cache directory and "
              "later sessions and subagents reuse its text.md.")
    return {"hookSpecificOutput": {"hookEventName": "PreToolUse", "additionalContext": hint}}


def disabled(event: dict) -> bool:
    if os.environ.get("APK_EXTRACT_FIRST", "").lower() in {"0", "off", "false", "no"}:
        return True
    roots = {os.environ.get("CLAUDE_PROJECT_DIR"), event.get("cwd")}
    return any(root and (Path(root) / ".ai" / "extract-first-hook.off").exists() for root in roots)


def main() -> int:
    try:
        event = json.load(sys.stdin)
        if disabled(event):
            return 0
        result = decide(event)
    except Exception:  # fail open: a broken hook must never block work
        return 0
    if result:
        print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
