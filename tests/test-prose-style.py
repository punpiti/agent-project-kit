#!/usr/bin/env python3
"""Regression tests for scripts/check_prose_style.py."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "scripts" / "check_prose_style.py"


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

print("prose style checker tests: PASS")
