#!/usr/bin/env python3
"""Count prose patterns that read as formulaic or AI-generated.

See prompts/24_PROSE_STYLE.md. The counts are review signals, not verdicts:
every flagged line must be read in context before it is changed.

Usage:
    check_prose_style.py FILE [FILE ...] [--strict]

Exit status is 1 when a zero-tolerance pattern is found, or, with --strict,
when any rate exceeds its review threshold. Otherwise 0.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# pattern name -> (regex, flags)
ZERO = {
    'formulaic "not X, but Y"': (r"\bnot\b[^.!?;:\n]{0,120}\bbut\b", re.I),
    '"more than just"': (r"\bmore than (just|merely|simply)\b", re.I),
    '"ไม่ใช่ … แต่เป็น"': (r"ไม่ใช่[^.\n]{0,80}แต่(เป็น)?", 0),
    '"มากกว่าแค่"': (r"มากกว่าแค่", 0),
    "question mark in running text": (r"[A-Za-zก-๙)]\?(\s|$)", 0),
}
# pattern name -> (regex, flags, review threshold per 1,000 words)
RATES = {
    '"rather than" / "instead of"': (r"\b(rather than|instead of)\b", re.I, 1.0),
    '", not …" contrast': (r",\s+not\s+\w", 0, 0.7),
    "semicolon": (r";", 0, 3.0),
    "em dash": (r"—|(?<!-)---(?!-)", 0, 1.5),
    "colon introducing a clause": (r"[a-z)\]}]:\s+[a-z]", 0, 2.5),
    "emphatic adverb": (r"\b(precisely|exactly|genuinely|crucially|importantly)\b", re.I, 0.5),
}


def clean(text: str, suffix: str) -> str:
    """Return text with markup reduced so counts refer to prose, keeping line numbers."""
    def blank(m: re.Match) -> str:
        return re.sub(r"[^\n]", " ", m.group(0))

    if suffix == ".tex":
        text = re.sub(r"(?<!\\)%.*", blank, text)
        for env in ("table", "tabular", "longtable", "figure", "equation", "align"):
            text = re.sub(r"\\begin\{%s\*?\}.*?\\end\{%s\*?\}" % (env, env), blank, text, flags=re.S)
        text = re.sub(r"\$[^$]*\$", blank, text)
        text = re.sub(r"\\(cite[pt]?|ref|eqref|label|input|include|url|href|bibliography\w*)\{[^}]*\}", blank, text)
    elif suffix in (".md", ".markdown"):
        text = re.sub(r"```.*?```", blank, text, flags=re.S)
        text = re.sub(r"`[^`\n]*`", blank, text)
        text = re.sub(r"\]\([^)]*\)", blank, text)
        text = re.sub(r"https?://\S+", blank, text)
    return text


def bold_lines(raw: str, suffix: str) -> list[int]:
    """Lines where bold appears inside a sentence (candidate rhetorical emphasis)."""
    pat = r"\\textbf\{" if suffix == ".tex" else r"\*\*[^*\n]+\*\*"
    hits = []
    for i, line in enumerate(raw.splitlines(), 1):
        s = line.strip()
        if not re.search(pat, s):
            continue
        # skip headings, table rows and label-style bold at line start ("**Term:**")
        if s.startswith(("#", "|", "&")) or "&" in s or re.match(r"(\\textbf\{[^}]*:\}|\*\*[^*]*:\*\*)", s):
            continue
        hits.append(i)
    return hits


def words(text: str) -> int:
    latin = len(re.findall(r"[A-Za-z]+(?:['’-][A-Za-z]+)*", text))
    thai_chars = len(re.findall(r"[ก-๙]", text))
    return latin + round(thai_chars / 4)  # rough Thai word estimate


def check(path: Path, strict: bool) -> bool:
    raw = path.read_text(encoding="utf-8")
    text = clean(raw, path.suffix.lower())
    n = max(words(text), 1)
    ok = True
    print(f"== {path}  (~{n:,} words)")
    for name, (pat, fl) in ZERO.items():
        lines = [text.count("\n", 0, m.start()) + 1 for m in re.finditer(pat, text, fl)]
        mark = "ok " if not lines else "FIX"
        ok &= not lines
        print(f"  [{mark}] {name}: {len(lines)}" + (f"  lines {sorted(set(lines))[:15]}" if lines else ""))
    bl = bold_lines(raw, path.suffix.lower())
    ok &= not bl
    print(f"  [{'ok ' if not bl else 'FIX'}] bold inside running text: {len(bl)}" + (f"  lines {bl[:15]}" if bl else ""))
    for name, (pat, fl, thr) in RATES.items():
        c = len(re.findall(pat, text, fl))
        rate = 1000 * c / n
        over = rate > thr
        if strict and over:
            ok = False
        print(f"  [{'chk' if over else 'ok '}] {name}: {c} ({rate:.1f}/1000; review above {thr})")
    return ok


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("files", nargs="+", type=Path)
    ap.add_argument("--strict", action="store_true", help="fail when a rate exceeds its threshold")
    args = ap.parse_args()
    results = [check(p, args.strict) for p in args.files]
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
