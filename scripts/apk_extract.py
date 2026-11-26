#!/usr/bin/env python3
"""Extract a reference PDF once into the shared cache and print where to read it.

    apk_extract.py FILE.pdf [--pages A-B] [--check] [--json]

Prints the cache directory. Read `<dir>/text.md` (pages are marked with
`<!-- page N -->`) and grep it; do not open the PDF again for its text.

Cache contract (DATA_FLOW_POLICY.md "Extraction cache contract"):
  root   ${APK_CACHE_ROOT:-${XDG_CACHE_HOME:-~/.cache}/agent-project-kit-cache}
  dir    <root>/extract/<stem>-<sha12>/
  index  INDEX.md with front matter source, source_sha256, extractor, pages,
         page_count, created; text in text.md

A hit is any existing `<stem>-<sha12>/INDEX.md` for the same SHA-256, so a
renamed or moved PDF reuses its cache. A hit that does not cover the requested
pages is extended in place. Extraction uses PyMuPDF when importable and falls
back to poppler `pdftotext -layout`, so system Python works. No OCR is run
here: pages without a text layer are reported, and the escalation order in
AGENTS.md (local Tesseract, then AI OCR) applies to them.

--check reports hit/miss without extracting (exit 0 on hit, 3 on miss).
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

TEXT_NAMES = ("text.md", "content.md", "final.md", "text.txt", "extract.md")
SCANNED_CHARS = 20


def cache_root() -> Path:
    base = os.environ.get("APK_CACHE_ROOT")
    if base:
        return Path(base).expanduser()
    xdg = os.environ.get("XDG_CACHE_HOME")
    return (Path(xdg) if xdg else Path.home() / ".cache") / "agent-project-kit-cache"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_stem(path: Path) -> str:
    # Short ASCII-friendly stems keep paths well under Windows/OneDrive limits.
    stem = re.sub(r"[^\w.-]+", "-", path.stem, flags=re.UNICODE).strip("-.")
    return (stem[:40].rstrip("-.") or "source")


def front_matter(index: Path) -> dict:
    meta = {}
    lines = index.read_text(encoding="utf-8", errors="replace").splitlines()
    if lines and lines[0].strip() == "---":
        for line in lines[1:]:
            if line.strip() == "---":
                break
            key, sep, value = line.partition(":")
            if sep:
                meta[key.strip()] = value.strip()
    return meta


def covered_pages(directory: Path) -> set[int] | None:
    """Pages a cache covers, or None when it does not say (legacy layouts)."""
    meta = front_matter(directory / "INDEX.md")
    spec = meta.get("pages")
    if spec:
        return parse_pages(spec, None)
    manifest = directory / "manifest.json"
    if manifest.exists():
        try:
            settings = json.loads(manifest.read_text(encoding="utf-8")).get("settings", {})
            start, end = int(settings["start_page"]), int(settings["end_page"])
            return set(range(start, end + 1))
        except (ValueError, KeyError, TypeError, json.JSONDecodeError):
            return None
    return None


def parse_pages(spec: str, page_count: int | None) -> set[int]:
    pages: set[int] = set()
    for part in str(spec).replace(" ", "").split(","):
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-", 1)
            start = int(a) if a else 1
            end = int(b) if b else (page_count or start)
            pages.update(range(start, end + 1))
        else:
            pages.add(int(part))
    return pages


def format_pages(pages: set[int]) -> str:
    out, run = [], []
    for page in sorted(pages):
        if run and page == run[-1] + 1:
            run.append(page)
            continue
        if run:
            out.append(f"{run[0]}-{run[-1]}" if len(run) > 1 else str(run[0]))
        run = [page]
    if run:
        out.append(f"{run[0]}-{run[-1]}" if len(run) > 1 else str(run[0]))
    return ",".join(out)


def find_hit(digest: str) -> Path | None:
    root = cache_root() / "extract"
    if not root.is_dir():
        return None
    for index in sorted(root.glob(f"*-{digest[:12]}/INDEX.md")):
        return index.parent
    return None


def text_file(directory: Path) -> Path | None:
    for name in TEXT_NAMES:
        if (directory / name).exists():
            return directory / name
    found = sorted(directory.glob("*.txt")) + sorted(directory.glob("*.md"))
    found = [p for p in found if p.name != "INDEX.md"]
    return found[0] if found else None


def page_count_of(pdf: Path) -> int | None:
    try:
        import pymupdf  # type: ignore
        with pymupdf.open(pdf) as doc:
            return doc.page_count
    except Exception:
        pass
    tool = shutil.which("pdfinfo")
    if tool:
        out = subprocess.run([tool, str(pdf)], capture_output=True, text=True, errors="replace")
        match = re.search(r"^Pages:\s+(\d+)", out.stdout, re.M)
        if match:
            return int(match.group(1))
    return None


def extract_pages(pdf: Path, pages: list[int]) -> tuple[dict[int, str], str]:
    try:
        import pymupdf  # type: ignore
        out = {}
        with pymupdf.open(pdf) as doc:
            for page in pages:
                out[page] = doc[page - 1].get_text()
        return out, f"PyMuPDF {getattr(pymupdf, 'VersionBind', '?')}"
    except ImportError:
        pass
    tool = shutil.which("pdftotext")
    if not tool:
        raise RuntimeError("neither PyMuPDF nor poppler pdftotext is available; "
                           "run python3 scripts/discover_tools.py to locate them")
    out = {}
    for page in pages:
        result = subprocess.run([tool, "-layout", "-enc", "UTF-8", "-f", str(page), "-l", str(page),
                                 str(pdf), "-"], capture_output=True)
        if result.returncode:
            raise RuntimeError(result.stderr.decode("utf-8", "replace").strip())
        out[page] = result.stdout.decode("utf-8", "replace").replace("\f", "")
    version = subprocess.run([tool, "-v"], capture_output=True, text=True).stderr.splitlines()
    return out, f"pdftotext -layout ({version[0].strip() if version else 'poppler'})"


def read_existing_pages(text: Path) -> dict[int, str]:
    pages, current, buf = {}, None, []
    for line in text.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True):
        match = re.match(r"<!-- page (\d+) -->\s*$", line)
        if match:
            if current is not None:
                pages[current] = "".join(buf)
            current, buf = int(match.group(1)), []
        elif current is not None:
            buf.append(line)
    if current is not None:
        pages[current] = "".join(buf)
    return pages


def write_cache(directory: Path, pdf: Path, digest: str, texts: dict[int, str],
                extractor: str, page_count: int | None) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    body = "".join(f"<!-- page {page} -->\n{texts[page].rstrip()}\n\n" for page in sorted(texts))
    (directory / "text.md").write_text(body, encoding="utf-8")
    scanned = [p for p, t in sorted(texts.items()) if len(re.sub(r"\s", "", t)) < SCANNED_CHARS]
    lines = [
        "---",
        f"source: {pdf}",
        f"source_sha256: {digest}",
        f"extractor: {extractor}",
        f"pages: {format_pages(set(texts))}",
        f"page_count: {page_count if page_count is not None else 'unknown'}",
        f"no_text_layer_pages: {format_pages(set(scanned)) or 'none'}",
        f"created: {dt.date.today().isoformat()}",
        "---",
        f"# {pdf.stem}",
        "",
        f"Text of pages {format_pages(set(texts))}: [text.md](text.md), one `<!-- page N -->` marker per page.",
        "Grep this file instead of re-extracting the PDF. Layout, tables, equations and",
        "figures are not preserved; render the needed pages when they matter.",
    ]
    if scanned:
        lines.append(f"Pages without a usable text layer: {format_pages(set(scanned))}. "
                     "Use local Tesseract on those pages before any AI OCR.")
    (directory / "INDEX.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(pdf: Path, page_spec: str | None, check: bool) -> dict:
    digest = sha256_file(pdf)
    hit = find_hit(digest)
    page_count = None
    wanted = None
    if page_spec:
        page_count = page_count_of(pdf)
        wanted = parse_pages(page_spec, page_count)
        if page_count is not None:
            beyond = {p for p in wanted if p < 1 or p > page_count}
            if beyond:
                raise ValueError(f"pages {format_pages(beyond)} are outside 1-{page_count}")
    if hit:
        covered = covered_pages(hit)
        if wanted is None and covered is not None:
            page_count = page_count_of(pdf)
            wanted = set(range(1, page_count + 1)) if page_count else None
        missing = sorted(wanted - covered) if (wanted and covered is not None) else []
        if not missing:
            return {"status": "hit", "dir": str(hit), "text": str(text_file(hit) or ""),
                    "sha256": digest}
        if check:
            return {"status": "partial", "dir": str(hit), "missing_pages": format_pages(set(missing)),
                    "sha256": digest}
        if (hit / "text.md").exists() and front_matter(hit / "INDEX.md").get("pages"):
            texts = read_existing_pages(hit / "text.md")
            new, extractor = extract_pages(pdf, missing)
            texts.update(new)
            write_cache(hit, pdf, digest, texts, extractor, page_count or page_count_of(pdf))
            return {"status": "extended", "dir": str(hit), "text": str(hit / "text.md"),
                    "sha256": digest, "added_pages": format_pages(set(missing))}
        # Legacy layout without page markers: write a fresh cache beside it.
    if check:
        return {"status": "miss", "sha256": digest}
    page_count = page_count or page_count_of(pdf)
    if wanted is None:
        if page_count is None:
            raise RuntimeError("cannot determine the page count; pass --pages")
        wanted = set(range(1, page_count + 1))
    texts, extractor = extract_pages(pdf, sorted(wanted))
    directory = cache_root() / "extract" / f"{safe_stem(pdf)}-{digest[:12]}"
    if hit and hit == directory:
        directory = directory.with_name(directory.name + "-pages")  # never overwrite a legacy cache
    write_cache(directory, pdf, digest, texts, extractor, page_count)
    return {"status": "created", "dir": str(directory), "text": str(directory / "text.md"),
            "sha256": digest}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("pdf")
    parser.add_argument("--pages", help="page ranges such as 1-5,9 (default: all pages)")
    parser.add_argument("--check", action="store_true", help="report hit/miss without extracting")
    parser.add_argument("--json", action="store_true", help="print a JSON result")
    args = parser.parse_args(argv)
    pdf = Path(args.pdf).expanduser().resolve()
    if not pdf.is_file():
        print(f"not a file: {pdf}", file=sys.stderr)
        return 2
    try:
        result = run(pdf, args.pages, args.check)
    except (RuntimeError, ValueError, OSError) as exc:
        print(f"apk extract: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(result, ensure_ascii=False))
    elif result["status"] in {"miss", "partial"}:
        print(f"{result['status']}" + (f" {result['dir']} (missing pages {result['missing_pages']})"
                                       if result["status"] == "partial" else ""))
    else:
        print(result["dir"])
        print(f"read: {result['text']}", file=sys.stderr)
    return 3 if args.check and result["status"] != "hit" else 0


if __name__ == "__main__":
    raise SystemExit(main())
