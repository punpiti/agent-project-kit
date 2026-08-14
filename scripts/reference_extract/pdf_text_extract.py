#!/usr/bin/env python3
"""Extract a page range from a reference PDF into single-column plain text.

Design goals (per project convention, see 00_project_admin/PROSE_WRITING_METHOD.md):
  - Never read/convert an entire large PDF when only a page range is needed.
  - Reflow multi-column pages into normal single-column reading order automatically
    (PyMuPDF's default text-extraction order already does this correctly; no manual
    column-splitting heuristic is applied, since that would risk mis-ordering pages
    that only have margin headings rather than true side-by-side columns).
  - Never attempt OCR by default. A page with no extractable text layer is reported
    as "likely scanned" and left alone.
  - When OCR is explicitly requested (--ocr), use the local tesseract binary first.
    This script never falls back to AI-vision transcription itself; if tesseract
    output looks empty or too short to be real, it says so and stops, leaving the
    decision to fall back to AI-vision reading to the operator.

Requires the `text` conda/mamba environment (has pymupdf + PIL). Run with:
  /home/punpiti/.local/share/mamba/envs/text/bin/python tools/pdf_text_extract.py ...

Usage:
  pdf_text_extract.py PDF START END [--out FILE] [--ocr] [--lang eng+tha] [--dpi 300]
                       [--images DIR [--min-image-size 80]]

  PDF          path to the PDF file
  START, END   1-indexed printed... actually PDF page numbers, inclusive (as counted
               by `pdfinfo`/PyMuPDF, i.e. page 1 is the first page of the file)
  --out FILE   write result to FILE instead of stdout (parent dir must exist)
  --ocr        allow OCR (via tesseract) for pages with no text layer
  --lang       tesseract language codes, default "eng"
  --dpi        rasterization resolution for OCR, default 300
  --images DIR also save each page's embedded raster images as
               DIR/<pdf-stem>_pPAGE_imgN.<ext> (created if missing). Per
               PROSE_WRITING_METHOD.md, when a source page you're reading for
               evidence has a figure worth keeping as a compositional
               reference for the eventual original artwork (not to copy, just
               to see how the source book presents it) — save it here and
               note the file in that heading's reading cache / EVIDENCE_x.x.x.md.
  --min-image-size
               skip embedded images smaller than this many pixels on both
               sides (default 80) — filters out bullet icons/rules, not real
               figures

Example:
  python tools/pdf_text_extract.py 05_references/books/White_2011_Fluid_Mechanics_7ed.pdf 30 34 \\
      --out /tmp/white_30_34.md --images 02_manuscript/ch01_fluid_properties/references/figures
"""
import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    import pymupdf as fitz  # import ผ่านชื่อใหม่ตัดคำเตือน deprecation ของชื่อ 'fitz'
except ImportError:
    sys.exit(
        "pymupdf not importable. Run this script with the 'text' env's python, e.g.\n"
        "  /home/punpiti/.local/share/mamba/envs/text/bin/python tools/pdf_text_extract.py ..."
    )

SCANNED_TEXT_THRESHOLD = 20  # chars; below this + has images => treat as scanned


def find_tesseract() -> str | None:
    candidates = [
        shutil.which("tesseract"),
        "/home/punpiti/.local/share/mamba/envs/text/bin/tesseract",
    ]
    for c in candidates:
        if c and Path(c).exists():
            return c
    return None


def ocr_page(page: "fitz.Page", dpi: int, lang: str, tesseract_bin: str) -> str:
    pix = page.get_pixmap(dpi=dpi)
    with tempfile.TemporaryDirectory() as td:
        img_path = Path(td) / "page.png"
        pix.save(str(img_path))
        result = subprocess.run(
            [tesseract_bin, str(img_path), "stdout", "-l", lang],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            return f"[tesseract failed: {result.stderr.strip()}]"
        return result.stdout


def save_page_images(doc: "fitz.Document", page: "fitz.Page", page_no: int, pdf_stem: str,
                      out_dir: Path, min_size: int) -> list[str]:
    """Save each embedded raster image on `page` to `out_dir`; return saved filenames."""
    out_dir.mkdir(parents=True, exist_ok=True)
    saved = []
    for n, img in enumerate(page.get_images(full=True), start=1):
        xref = img[0]
        try:
            info = doc.extract_image(xref)
        except Exception:
            continue
        if info["width"] < min_size or info["height"] < min_size:
            continue
        filename = f"{pdf_stem}_p{page_no}_img{n}.{info['ext']}"
        (out_dir / filename).write_bytes(info["image"])
        saved.append(filename)
    return saved


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pdf", type=Path)
    ap.add_argument("start", type=int)
    ap.add_argument("end", type=int)
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--ocr", action="store_true")
    ap.add_argument("--lang", default="eng")
    ap.add_argument("--dpi", type=int, default=300)
    ap.add_argument("--images", type=Path, default=None)
    ap.add_argument("--min-image-size", type=int, default=80)
    args = ap.parse_args()

    if not args.pdf.exists():
        sys.exit(f"File not found: {args.pdf}")

    doc = fitz.open(str(args.pdf))
    total_pages = doc.page_count
    if args.start < 1 or args.end > total_pages or args.start > args.end:
        sys.exit(f"Invalid range {args.start}-{args.end} for a {total_pages}-page PDF.")

    span = args.end - args.start + 1
    if span > 30 and not args.out:
        print(
            f"warning: extracting {span} pages to stdout; consider --out and/or a narrower range",
            file=sys.stderr,
        )

    tesseract_bin = find_tesseract() if args.ocr else None
    if args.ocr and not tesseract_bin:
        sys.exit("--ocr requested but no tesseract binary found on PATH or in the text env.")

    out_chunks = []
    for i in range(args.start - 1, args.end):
        page = doc[i]
        text = page.get_text("text")
        printed_no = i + 1
        header = f"--- PDF page {printed_no} ({args.pdf.name}) ---"

        if len(text.strip()) < SCANNED_TEXT_THRESHOLD:
            has_images = len(page.get_images()) > 0
            if has_images:
                if args.ocr:
                    ocr_text = ocr_page(page, args.dpi, args.lang, tesseract_bin)
                    if len(ocr_text.strip()) < SCANNED_TEXT_THRESHOLD:
                        body = (
                            "[OCR produced little/no usable text — this page may need "
                            "AI-vision transcription instead of tesseract]"
                        )
                    else:
                        body = ocr_text
                else:
                    body = (
                        "[likely scanned page, no extractable text layer — skipped. "
                        "Rerun with --ocr to attempt tesseract, or confirm before using "
                        "AI-vision transcription as a last resort.]"
                    )
            else:
                body = "[no extractable text and no images detected — page may be blank]"
        else:
            body = text

        if args.images:
            saved = save_page_images(doc, page, printed_no, args.pdf.stem, args.images, args.min_image_size)
            if saved:
                body += "\n\n[" + str(len(saved)) + " image(s) saved to " + str(args.images) + ": " + ", ".join(saved) + "]"

        out_chunks.append(f"{header}\n\n{body}".rstrip())

    result = "\n\n".join(out_chunks) + "\n"

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(result, encoding="utf-8")
        print(f"wrote {len(result)} chars to {args.out}", file=sys.stderr)
    else:
        print(result)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
