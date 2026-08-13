#!/usr/bin/env python3
"""Validate and compose the reusable book-writing method and a book profile."""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_METHOD = ROOT / "prompts/22_BOOK_WRITING.md"
DEFAULT_PROFILE = ROOT / "templates/BOOK_WRITING_PROFILE.md"

METHOD_BEGIN = "<!-- BOOK_METHOD_BEGIN -->\n"
METHOD_END = "<!-- BOOK_METHOD_END -->"
PLACEHOLDER_RE = re.compile(r"\{\{PROFILE:([a-z0-9-]+)\}\}")
PROFILE_RE = re.compile(
    r"<!-- BOOK_PROFILE_BEGIN:([a-z0-9-]+) -->\n"
    r"(.*?)"
    r"<!-- BOOK_PROFILE_END:\1 -->",
    re.DOTALL,
)
UNRESOLVED_RE = re.compile(r"\{\{BOOK:[A-Z0-9_]+\}\}")

# These terms are forbidden in the reusable profile template, where retaining
# source-book values would silently contaminate a different book. The method
# may retain clearly conditional source examples when its production contract
# explicitly prevents them from becoming cross-book defaults.
SOURCE_BOOK_PROFILE_TERMS = (
    "fluid mechanics",
    "กลศาสตร์ของไหล",
    "ของไหล",
    "white",
    "elger",
    "moody",
    "pump head",
    "w7",
    "e10",
    "cc3",
)


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Check profile coverage, reject source-book leakage, compose the "
            "book-writing method, and optionally compare it with a baseline."
        )
    )
    parser.add_argument("--method", type=Path, default=DEFAULT_METHOD)
    parser.add_argument("--profile", type=Path, default=DEFAULT_PROFILE)
    parser.add_argument(
        "--baseline",
        type=Path,
        help="Optional resolved baseline that the composed result must match exactly.",
    )
    parser.add_argument(
        "--expected-baseline-sha256",
        help="Optional SHA-256 guard for --baseline before comparing content.",
    )
    parser.add_argument(
        "--require-resolved",
        action="store_true",
        help="Fail if any {{BOOK:...}} value remains in the selected profile.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Write the composed prompt after all checks pass.",
    )
    return parser.parse_args()


def read_text(path: Path, label: str) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        fail(f"{label} not found: {path}")
    except UnicodeDecodeError:
        fail(f"{label} is not valid UTF-8: {path}")
    raise AssertionError("unreachable")


def first_difference(actual: str, expected: str) -> str:
    actual_lines = actual.splitlines()
    expected_lines = expected.splitlines()
    for line_no, (actual_line, expected_line) in enumerate(
        zip(actual_lines, expected_lines), start=1
    ):
        if actual_line != expected_line:
            return f"line {line_no}"
    return f"end of file (actual {len(actual_lines)} lines, expected {len(expected_lines)})"


def main() -> None:
    args = parse_args()
    if args.expected_baseline_sha256 and not args.baseline:
        fail("--expected-baseline-sha256 requires --baseline")

    method_file = read_text(args.method, "method")
    if method_file.count(METHOD_BEGIN) != 1 or method_file.count(METHOD_END) != 1:
        fail("method must contain exactly one BOOK_METHOD marker pair")
    template = method_file.split(METHOD_BEGIN, 1)[1].split(METHOD_END, 1)[0]

    profile_file = read_text(args.profile, "profile")
    if args.profile.resolve() == DEFAULT_PROFILE.resolve():
        lowered_profile = profile_file.casefold()
        leaked = sorted(
            term for term in SOURCE_BOOK_PROFILE_TERMS if term.casefold() in lowered_profile
        )
        if leaked:
            fail("source-book terms remain in reusable profile: " + ", ".join(leaked))

    entries: dict[str, str] = {}
    for name, value in PROFILE_RE.findall(profile_file):
        if name in entries:
            fail(f"duplicate profile entry: {name}")
        entries[name] = value

    required = set(PLACEHOLDER_RE.findall(template))
    supplied = set(entries)
    if missing := sorted(required - supplied):
        fail(f"missing profile entries: {', '.join(missing)}")
    if unused := sorted(supplied - required):
        fail(f"unused profile entries: {', '.join(unused)}")
    if args.require_resolved:
        unresolved = sorted(set(UNRESOLVED_RE.findall(profile_file)))
        if unresolved:
            fail("unresolved book values: " + ", ".join(unresolved))

    reconstructed = PLACEHOLDER_RE.sub(lambda match: entries[match.group(1)], template)

    if args.baseline:
        baseline = read_text(args.baseline, "baseline")
        digest = hashlib.sha256(baseline.encode("utf-8")).hexdigest()
        if args.expected_baseline_sha256 and digest != args.expected_baseline_sha256:
            fail(
                "baseline changed before comparison "
                f"(expected {args.expected_baseline_sha256}, actual {digest})"
            )
        if reconstructed != baseline:
            fail(
                "composed method differs from baseline at "
                + first_difference(reconstructed, baseline)
            )

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(reconstructed, encoding="utf-8")

    digest = hashlib.sha256(reconstructed.encode("utf-8")).hexdigest()
    resolution = "resolved" if not UNRESOLVED_RE.search(profile_file) else "template"
    print(
        "PASS: book-writing method/profile are structurally valid "
        f"({len(required)} profile entries, {resolution}, composed SHA-256 {digest})"
    )


if __name__ == "__main__":
    main()
