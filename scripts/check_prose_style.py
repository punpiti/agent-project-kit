#!/usr/bin/env python3
"""Count prose patterns that read as formulaic or AI-generated.

See prompts/24_PROSE_STYLE.md. The counts are review signals, not verdicts:
every flagged line must be read in context before it is changed.
This tool does not determine whether AI generated any text.

Usage:
    check_prose_style.py FILE [FILE ...] [--strict] [--profile GENRE]

GENRE matches the prose genre overlays in prompts/prose-genres/. Without
--profile the general rules apply; they are also the academic rules and the
ones prompts/22_BOOK_WRITING.md uses for textbook prose.

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
    '"ไม่ใช่แค่" / "ไม่ใช่เพียง"': (r"ไม่ใช่(แค่|เพียง)", 0),
    '"not just" / "not merely"': (r"\bnot (just|merely|simply)\b", re.I),
    "question mark in running text": (r"[A-Za-zก-๙)]\?(\s|$)", 0),
}
# pattern name -> (regex, flags, review threshold per 1,000 words)
RATES = {
    '"rather than" / "instead of"': (r"\b(rather than|instead of)\b", re.I, 1.0),
    '", not …" contrast': (r",\s+not\s+\w", 0, 0.7),
    # "X is not A; it is B" is usually a rhetorical reframe, but a factual
    # "was not run; it was skipped" matches too, so this is a review signal.
    '"is not X; it is Y"': (r"\b(?:(?:is|are|was|were)\s+not|isn't|aren't|wasn't|weren't)\b[^.!?;:\u2014\n]{1,80}[;:\u2014]\s*(?:it|this|that|they)\s*(?:is|are|was|were|'s|'re)\b", re.I, 0.7),
    "semicolon": (r";", 0, 3.0),
    "em dash": (r"—|(?<!-)---(?!-)", 0, 1.5),
    "colon introducing a clause": (r"[a-z)\]}]:\s+[a-z]", 0, 2.5),
    "emphatic adverb": (r"\b(precisely|exactly|genuinely|crucially|importantly)\b", re.I, 0.5),
}

# Exact phrases from observed scientific-writing failures. These are review
# candidates, not evidence of AI use and never affect the exit status. The
# semantic gate in prompts/24_PROSE_STYLE.md must catch equivalent wording.
REVIEW_ONLY = {
    "internal artifact named instead of research object": (
        r"\b(cleaning notebooks?|archived workflow|analysis cache|stored metrics)\b",
        re.I,
    ),
    "method deferred to notebook or caption": (
        r"\b(?:the\s+)?notebooks?\s+(?:document|describe|show)|"
        r"\b(?:the\s+|its\s+)?caption\s+summarizes\b",
        re.I,
    ),
}


QUESTION = "question mark in running text"
BOLD = "bold inside running text"
# Genre differences only; anything not listed keeps the general rule.
#   allow:   zero-tolerance checks that do not apply to the genre
#   rates:   review thresholds replaced for the genre; None skips the check
#   review:  whether scientific-writing review phrases are reported
#   bold_negation: bold is allowed only on a negation word ("**not**", "**ไม่**")
PROFILES = {
    "general": {"allow": set(), "rates": {}, "review": True},
    "academic": {"allow": set(), "rates": {}, "review": True},
    # Posts ask readers questions and use looser punctuation.
    "social": {"allow": {QUESTION}, "rates": {"em dash": 3.0, "colon introducing a clause": 4.0}, "review": False},
    # Items are questions; bold marks a negation in a stem ("which is **not**").
    # A per-1,000-word rate cannot tolerate labels in short copy, so the colon
    # check is off for item stems ("Given: ...") and web labels ("Price: free").
    "exam": {"allow": {QUESTION}, "bold_negation": True, "rates": {"colon introducing a clause": None}, "review": False},
    # FAQ headings and labels ("Price: free") are normal web copy.
    "web": {"allow": {QUESTION}, "rates": {"colon introducing a clause": None}, "review": False},
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
        # Image alt text labels a figure; it is not running prose.
        text = re.sub(r"!\[[^\]\n]*\]", blank, text)
        text = re.sub(r"\]\([^)]*\)", blank, text)
        text = re.sub(r"https?://\S+", blank, text)
        # Parse separator lines one at a time. This avoids a nested quantified
        # regex whose backtracking can grow catastrophically on long malformed rows.
        def separator_line(line: str) -> bool:
            stripped = line.strip()
            if re.fullmatch(r"(?:(?:-\s*){3,}|(?:\*\s*){3,}|(?:_\s*){3,})", stripped):
                return True
            cells = stripped.strip("|").split("|")
            return bool(stripped) and all(
                re.fullmatch(r"[ \t]*:?-{3,}:?[ \t]*", cell) for cell in cells
            )

        text = "".join(
            re.sub(r"[^\n]", " ", line) if separator_line(line) else line
            for line in text.splitlines(keepends=True)
        )
    return text


# Exam stems may bold a negation so it is not misread ("which is **not** ...").
NEGATION_BOLD = re.compile(
    r"\*\*(?:not|never|except|least|ไม่|ไม่ใช่|ยกเว้น|ไม่ถูกต้อง)\*\*|"
    r"\\textbf\{(?:not|never|except|least|ไม่|ไม่ใช่|ยกเว้น|ไม่ถูกต้อง)\}", re.I)
TITLE_MAX = 80


def bold_lines(raw: str, suffix: str, allow_negation: bool = False,
               question_titles: bool = True) -> tuple[list[int], list[int]]:
    """Lines where bold appears inside a sentence (candidate rhetorical emphasis),
    and whole bold lines that may be a title or an emphasized sentence."""
    pat = r"\\textbf\{" if suffix == ".tex" else r"\*\*[^*\n]+\*\*"
    hits, unclear = [], []
    for i, line in enumerate(raw.splitlines(), 1):
        # A label inside a callout or list item ("> **Problem:** ...") is still a label.
        s = re.sub(r"^(?:>\s*)+|^(?:[-*+]|\d+[.)])\s+", "", line.strip())
        if allow_negation:
            s = NEGATION_BOLD.sub("not", s)
        if not re.search(pat, s):
            continue
        # skip headings, table rows and label-style bold at line start ("**Term:**")
        # A whole bold line: a question is a FAQ-style title, a line ending in
        # "." or "!" is an emphasized sentence, and anything else (most Thai
        # sentences end without punctuation) needs a human look.
        whole = re.fullmatch(r"\*\*([^*\n]+)\*\*|\\textbf\{([^{}]*)\}", s)
        if whole:
            inner = (whole.group(1) or whole.group(2) or "").strip()
            if inner.endswith(("?", "？")):
                if question_titles and len(inner) <= TITLE_MAX:
                    continue
                hits.append(i)
                continue
            if len(inner) <= TITLE_MAX and not re.search(r"[.!。]$", inner):
                unclear.append(i)
                continue
        if s.startswith(("#", "|", "&")) or "&" in s or re.match(r"(\\textbf\{[^}]*:\}|\*\*[^*]*:\*\*)", s):
            continue
        hits.append(i)
    return hits, unclear


def words(text: str) -> int:
    latin = len(re.findall(r"[A-Za-z]+(?:['’-][A-Za-z]+)*", text))
    thai_chars = len(re.findall(r"[ก-๙]", text))
    return latin + round(thai_chars / 4)  # rough Thai word estimate


def check(path: Path, strict: bool, profile: str = "general") -> bool:
    rules = PROFILES[profile]
    raw = path.read_text(encoding="utf-8")
    text = clean(raw, path.suffix.lower())
    n = max(words(text), 1)
    ok = True
    print(f"== {path}  (~{n:,} words, profile {profile})")
    for name, (pat, fl) in ZERO.items():
        if name in rules["allow"]:
            continue
        lines = [text.count("\n", 0, m.start()) + 1 for m in re.finditer(pat, text, fl)]
        mark = "ok " if not lines else "FIX"
        ok &= not lines
        print(f"  [{mark}] {name}: {len(lines)}" + (f"  lines {sorted(set(lines))[:15]}" if lines else ""))
    # Exam items are questions, so a bold question line is a bold stem, not a title.
    bl, unclear = bold_lines(raw, path.suffix.lower(), rules.get("bold_negation", False),
                             question_titles=not rules.get("bold_negation", False))
    ok &= not bl
    print(f"  [{'ok ' if not bl else 'FIX'}] {BOLD}: {len(bl)}" + (f"  lines {bl[:15]}" if bl else ""))
    print(f"  [{'review' if unclear else 'ok '}] whole bold line (title or emphasized sentence?): {len(unclear)}"
          + (f"  lines {unclear[:15]}" if unclear else ""))
    for name, (pat, fl) in (REVIEW_ONLY.items() if rules["review"] else ()):
        lines = [text.count("\n", 0, m.start()) + 1 for m in re.finditer(pat, text, fl)]
        mark = "review" if lines else "ok "
        print(f"  [{mark}] {name}: {len(lines)}" + (f"  lines {sorted(set(lines))[:15]}" if lines else ""))
    for name, (pat, fl, thr) in RATES.items():
        thr = rules["rates"].get(name, thr)
        if thr is None:
            continue
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
    ap.add_argument("--profile", choices=sorted(PROFILES), default="general",
                    help="prose genre (see prompts/24_PROSE_STYLE.md section 1A)")
    args = ap.parse_args()
    results = [check(p, args.strict, args.profile) for p in args.files]
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
