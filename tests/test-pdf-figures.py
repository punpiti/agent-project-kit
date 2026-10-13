#!/usr/bin/env python3
"""Regression checks for scripts/reference_extract/pdf_figures.py.

Builds a synthetic PDF covering the failures that made figure auto-crop unsafe
(lost captions, lost panels, figures chained across a separator rule, contents
pages, rotated pages) and checks the hash-keyed cache, manual crops and review
records. Needs PyMuPDF; when this interpreter lacks it, the test re-runs itself
in the shared `text` environment, and skips only if no such environment exists.
"""

import sys
sys.dont_write_bytecode = True  # never add caches to the source tree
import importlib.util
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "reference_extract" / "pdf_figures.py"

try:
    import pymupdf
except ImportError:
    if os.environ.get("APK_PDF_FIGURES_REEXEC"):
        sys.exit("pymupdf missing inside the text environment")
    for manager in ("micromamba", "mamba", "conda"):
        if shutil.which(manager):
            probe = subprocess.run([manager, "run", "-n", "text", "python", "-c", "import pymupdf"],
                                   capture_output=True)
            if probe.returncode == 0:
                env = dict(os.environ, APK_PDF_FIGURES_REEXEC="1")
                sys.exit(subprocess.run([manager, "run", "-n", "text", "python", __file__], env=env).returncode)
    print("SKIP test-pdf-figures: PyMuPDF and the shared text environment are unavailable")
    sys.exit(0)

SPEC = importlib.util.spec_from_file_location("pdf_figures", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

PROSE = ("Running prose that explains the experiment in enough words to look like a real "
         "paragraph of body text, which the extractor must never absorb into a figure crop. ") * 2


def prose(page, y):
    page.insert_textbox(pymupdf.Rect(60, y, 535, y + 60), PROSE, fontsize=9)


def panel(page, rect, label):
    shape = page.new_shape()
    shape.draw_rect(rect)
    shape.draw_line((rect.x0 + 5, rect.y1 - 5), (rect.x1 - 5, rect.y0 + 5))
    shape.draw_circle(rect.tl + (30, 30), 8)
    shape.finish(color=(0, 0, 0.6), width=1)
    shape.commit()
    page.insert_text((rect.x0 + 4, rect.y0 + 12), label, fontsize=9)


def build(path: Path) -> None:
    doc = pymupdf.open()

    # Page 1: two-panel vector figure, raster figure, table with caption above.
    page = doc.new_page(width=595, height=842)
    prose(page, 50)
    panel(page, pymupdf.Rect(70, 130, 270, 280), "(a)")
    # Unlabelled so that only the caption can join the two panels (labels on
    # one line become one text block that would bridge them on its own).
    panel(page, pymupdf.Rect(320, 130, 520, 280), "")
    page.insert_textbox(pymupdf.Rect(70, 290, 520, 320),
                        "Figure 1. Two panels that must stay together with this caption.", fontsize=9)
    prose(page, 335)
    pix = pymupdf.Pixmap(pymupdf.csRGB, pymupdf.IRect(0, 0, 160, 100), False)
    pix.set_rect(pix.irect, (200, 120, 40))
    page.insert_image(pymupdf.Rect(150, 410, 450, 598), pixmap=pix)
    page.insert_textbox(pymupdf.Rect(150, 604, 450, 630), "Fig. 2: A raster photograph.", fontsize=9)
    page.insert_textbox(pymupdf.Rect(100, 650, 500, 670), "Table 1. Measured values.", fontsize=9)
    grid = page.new_shape()
    for y in (675, 700, 725, 750):
        grid.draw_line((100, y), (500, y))
    for x in (100, 300, 500):
        grid.draw_line((x, 675), (x, 750))
    grid.finish(color=(0, 0, 0), width=0.8)
    grid.commit()

    # Page 2: two figures separated only by a full-width rule (was chained).
    page = doc.new_page(width=595, height=842)
    panel(page, pymupdf.Rect(150, 60, 450, 230), "")
    page.insert_textbox(pymupdf.Rect(90, 236, 505, 262), "Figure 3. Upper figure.", fontsize=9)
    page.draw_line((60, 268), (535, 268), width=0.5)
    panel(page, pymupdf.Rect(150, 285, 450, 455), "")
    page.insert_textbox(pymupdf.Rect(90, 461, 505, 487), "Figure 4. Lower figure.", fontsize=9)

    # Page 3: list of figures - entries are not captions.
    page = doc.new_page(width=595, height=842)
    for n, y in enumerate((80, 100, 120, 140), start=1):
        page.insert_text((70, y), f"Figure {n}. Entry title .................. {n + 2}", fontsize=9)

    # Page 4: rotated page with a captioned figure.
    page = doc.new_page(width=595, height=842)
    panel(page, pymupdf.Rect(100, 100, 400, 300), "")
    page.insert_textbox(pymupdf.Rect(100, 306, 450, 330), "Figure 5. On a rotated page.", fontsize=9)
    page.set_rotation(90)

    doc.save(str(path))
    doc.close()


def run(*args: str) -> str:
    result = subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    return result.stdout + result.stderr


def contains(outer, inner, tol=0.5):
    return (outer[0] <= inner[0] + tol and outer[1] <= inner[1] + tol
            and outer[2] >= inner[2] - tol and outer[3] >= inner[3] - tol)


# Caption vocabulary, including Thai, and leader rejection.
for text in ("Figure 3. x", "Fig. 2a: x", "FIG. 10 x", "Table S1. x", "Supplementary Figure 4 x",
             "Extended Data Fig. 2 | x", "รูปที่ 4 x", "ภาพที่ 2.1 x", "ตารางที่ 5 x", "Figure 5-8. x"):
    assert MODULE.CAPTION_RE.match(text), text
for text in ("Figures show that", "Tablet devices", "Figure skating is"):
    assert not MODULE.CAPTION_RE.match(text), text
assert MODULE.LEADER_RE.search("Figure 1. Entry ............ 3")

with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp)
    pdf = tmp / "synthetic paper.pdf"
    cache = tmp / "cache"
    build(pdf)

    out = run(str(pdf), "--pages", "1-4", "--cache-dir", str(cache))
    dirs = list(cache.glob("synthetic-paper-*"))
    assert len(dirs) == 1, dirs
    source = dirs[0]
    manifest = json.loads((source / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["schema"] == "apk-pdf-figures/1"
    assert manifest["source"]["sha256"] == MODULE.sha256_file(pdf)
    figs = {f["label"]: f for f in manifest["figures"]}

    # Multi-panel figure keeps both panels and its caption, and no prose.
    fig1 = figs["Figure 1"]
    assert contains(fig1["crop_bbox"], [70, 130, 520, 280]), fig1
    assert contains(fig1["crop_bbox"], fig1["caption_bbox"]), fig1
    assert "multi_panel_merged" in fig1["flags"] and "crop_overlaps_prose" not in fig1["flags"], fig1
    assert "Two panels" in fig1["caption"]

    # Raster figure: caption kept, original image saved without resampling.
    fig2 = figs["Fig. 2"]
    assert fig2["graphics"] == "raster" and "native" in fig2["files"], fig2
    assert contains(fig2["crop_bbox"], [150, 410, 450, 598]) and contains(fig2["crop_bbox"], fig2["caption_bbox"])
    native = pymupdf.Pixmap(str(source / fig2["files"]["native"]))
    assert (native.width, native.height) == (160, 100), (native.width, native.height)

    # Table: caption above, grid below, both in the crop.
    table = figs["Table 1"]
    assert table["kind"] == "table" and contains(table["crop_bbox"], [100, 650, 500, 750]), table

    # Separator rule does not chain two figures; each keeps only its own body.
    fig3, fig4 = figs["Figure 3"], figs["Figure 4"]
    assert fig3["crop_bbox"][3] < 270 and fig4["crop_bbox"][1] > 266, (fig3, fig4)
    assert not set(fig3["flags"]) | set(fig4["flags"]), (fig3, fig4)

    # Contents page yields nothing; rotated page still crops its figure.
    assert not [f for f in manifest["figures"] if f["page"] == 3], manifest["figures"]
    fig5 = figs["Figure 5"]
    assert contains(fig5["crop_bbox"], [100, 100, 400, 300]) and contains(fig5["crop_bbox"], fig5["caption_bbox"]), fig5
    png = pymupdf.Pixmap(str(source / fig5["files"]["png"]))
    assert png.height > png.width, (png.width, png.height)  # rendered as displayed (rotated)

    for fig in manifest["figures"]:
        assert (source / fig["files"]["png"]).is_file(), fig
        assert fig["dpi"] == 300 and fig["review"] == "pending"
    assert all((source / "overview" / f"p{n:04d}.png").is_file() for n in range(1, 5))
    index = (source / "INDEX.md").read_text(encoding="utf-8")
    assert "Figure 1" in index and manifest["source"]["sha256"] in index
    assert "synthetic paper.pdf" in (cache / "INDEX.md").read_text(encoding="utf-8")

    # Second run reuses the cache; a renamed copy hits the same entry.
    out = run(str(pdf), "--pages", "1-4", "--cache-dir", str(cache))
    assert "0 page(s) extracted, 4 reused" in out, out
    renamed = tmp / "synthetic paper.pdf"
    out = run(str(renamed), "--pages", "2", "--cache-dir", str(cache))
    assert "1 reused" in out, out

    # Manual crop and review survive a forced re-extraction.
    run(str(pdf), "--manual-crop", "1:60,120,530,330:Figure 1", "--cache-dir", str(cache))
    run(str(pdf), "--review", f"{fig4['id']}=ok", "--cache-dir", str(cache))
    out = run(str(pdf), "--pages", "1", "--force", "--cache-dir", str(cache))
    manifest = json.loads((source / "manifest.json").read_text(encoding="utf-8"))
    manual = [f for f in manifest["figures"] if f["method"] == "manual"]
    assert len(manual) == 1 and manual[0]["review"] == "ok" and manual[0]["crop_bbox"] == [60, 120, 530, 330], manual
    assert (source / manual[0]["files"]["png"]).is_file()
    assert next(f for f in manifest["figures"] if f["id"] == fig4["id"])["review"] == "ok"

    # Changing render settings re-extracts instead of serving stale files.
    out = run(str(pdf), "--pages", "2", "--dpi", "150", "--cache-dir", str(cache))
    assert "settings changed" in out and "1 page(s) extracted" in out, out

    # An edited PDF gets its own cache entry.
    doc = pymupdf.open(str(pdf))
    doc[2].insert_text((70, 400), "edited")
    edited = tmp / "edited.pdf"
    doc.save(str(edited))
    doc.close()
    shutil.copy(edited, pdf)
    run(str(pdf), "--pages", "3", "--cache-dir", str(cache))
    assert len(list(cache.glob("synthetic-paper-*"))) == 2

    # --list reads the cache without extracting.
    assert "Figures: synthetic paper.pdf" in run(str(pdf), "--list", "--cache-dir", str(cache))

print("PASS test-pdf-figures")
