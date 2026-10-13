#!/usr/bin/env python3
"""Extract individual figures from a PDF into a reusable, hash-keyed cache.

Crops each figure (not the whole page) so later sessions reuse small, sharp
files instead of re-reading or re-rendering pages. The crop is designed around
the two failures that made older auto-crop unsafe:

  * captions were cut off      -> the crop is anchored on the caption block
                                  ("Figure 3", "Fig. 2a", "Table 1", "รูปที่ 4",
                                  "ภาพที่ 2", "ตารางที่ 5", ...) and always
                                  includes it;
  * multi-panel figures lost   -> every graphics cluster between the caption and
    panels                        the nearest prose block is merged, instead of
                                  keeping only the largest cluster.

Graphics are both embedded raster images and vector drawings (PyMuPDF
`cluster_drawings`), plus short label text sitting inside them (axis labels,
panel letters). Long prose blocks are never absorbed into a figure.

Quality:
  * every figure is rendered from the PDF itself at --dpi (default 300), so
    vector line art and text stay sharp;
  * when a figure is a single embedded raster image, the original image is also
    saved without resampling (`*_native.<ext>`);
  * --vector-pdf additionally saves a cropped single-page vector PDF.

Cache layout (one directory per source, keyed by SHA-256, so a renamed or moved
PDF still hits the cache and an edited PDF never reuses stale crops):

  <cache-dir>/<stem>-<sha12>/
      manifest.json       source, hash, tool/PyMuPDF version, settings, pages, figures
      INDEX.md            human/agent-readable table: id, page, label, caption, flags
      figures/<id>.png    rendered crop (+ _native.<ext>, .pdf when available)
      overview/p0012.png  low-res page with every crop boxed and labelled, for
                          one-glance visual QA (axis ticks are PDF points)
  <cache-dir>/INDEX.md    list of cached sources

Already-extracted pages are skipped unless the settings changed or --force is
given. Manual crops (--manual-crop) and review decisions (--review) persist
across re-runs.

Every figure carries `flags`; anything flagged must be checked on the overview
image before use. Unflagged figures should still be eyeballed once - the
heuristic is better, not infallible. Scanned pages (a full-page image with no
text layer) are reported, not cropped: OCR/vision needs a user decision first.

Requires the shared `text` environment (PyMuPDF >= 1.24):
  micromamba run -n text python scripts/reference_extract/pdf_figures.py \\
      SOURCE.pdf --pages 12-15,40 --cache-dir references/pdf-figures

  # reuse: read <cache-dir>/<stem>-<sha12>/INDEX.md, or
  ... pdf_figures.py SOURCE.pdf --list
  # fix a bad crop (PDF points, unrotated page; read them off the overview axes)
  ... pdf_figures.py SOURCE.pdf --manual-crop "14:60,90,540,420:Figure 5-8"
  # record the visual check
  ... pdf_figures.py SOURCE.pdf --review p014-f01=ok --review p015-f02=reject

Page numbers are 1-based PDF file pages, not printed page numbers.
Figures from references remain the publisher's copyright: use them as
compositional references unless the rights allow reuse.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import sys
from pathlib import Path

try:
    import pymupdf
except ImportError:
    sys.exit(
        "pymupdf not importable. Run with the shared 'text' environment, e.g.\n"
        "  micromamba run -n text python scripts/reference_extract/pdf_figures.py ..."
    )

TOOL_VERSION = "1.0.0"
SCHEMA = "apk-pdf-figures/1"
CACHE_ENV = "APK_PDF_FIGURE_CACHE"
DEFAULT_CACHE = Path("references") / "pdf-figures"

CAPTION_RE = re.compile(
    r"^\s*(?P<label>(?:(?:supplementary|extended\s+data)\s+)?"
    r"(?:fig(?:ure)?s?\.?|table|scheme|plate|chart|exhibit|"
    r"รูปที่|ภาพที่|แผนภาพที่|แผนภูมิที่|ตารางที่)"
    r"\s*[A-Z]?\d+(?:[.\-–]\d+)*[a-z]?)"
    r"\s*(?:[.:|)\-–—]|\s|$)",
    re.IGNORECASE,
)
TABLE_RE = re.compile(r"^\s*(table|ตารางที่)", re.IGNORECASE)
LEADER_RE = re.compile(r"(\.\s?){4,}|…{2,}")  # list-of-figures/TOC entries, not captions
RULE_TEXT_RE = re.compile(r"^[\s_\-–—=~.·•*]*$")  # "_____" separators typed as text

# Heuristic thresholds, in PDF points unless stated otherwise.
CLUSTER_TOLERANCE = 6.0     # drawing primitives closer than this form one cluster
MERGE_GAP = 8.0             # graphics closer than this are one region; captioned
                            # panels further apart are joined via their caption
MIN_REGION_SIDE = 36.0      # smaller regions are icons, rules, bullets
MIN_REGION_AREA = 0.006     # fraction of page area
PROSE_MIN_CHARS = 120       # a text block at least this long is running prose
CAPTION_MAX_GAP = 0.22      # fraction of page height between caption and figure
SCANNED_IMAGE_AREA = 0.85   # one image covering this much of a page = scan
SCANNED_TEXT_CHARS = 20
NATIVE_IMAGE_COVER = 0.9    # image must cover this much of the region to be native


# ---------------------------------------------------------------- helpers --

def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def slug(text: str, limit: int = 40) -> str:
    value = re.sub(r"[^A-Za-z0-9ก-๙]+", "-", text).strip("-")
    return (value or "source")[:limit]


def parse_pages(spec: str, count: int) -> list[int]:
    if spec.strip().lower() == "all":
        return list(range(1, count + 1))
    pages: set[int] = set()
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start, end = (int(x) for x in part.split("-", 1))
            pages.update(range(start, end + 1))
        else:
            pages.add(int(part))
    bad = sorted(p for p in pages if p < 1 or p > count)
    if bad:
        raise SystemExit(f"pages out of range 1-{count}: {bad}")
    return sorted(pages)


def rect_list(rect: "pymupdf.Rect") -> list[float]:
    return [round(rect.x0, 1), round(rect.y0, 1), round(rect.x1, 1), round(rect.y1, 1)]


def grow(rect: "pymupdf.Rect", pad: float) -> "pymupdf.Rect":
    return pymupdf.Rect(rect.x0 - pad, rect.y0 - pad, rect.x1 + pad, rect.y1 + pad)


def h_overlap(a: "pymupdf.Rect", b: "pymupdf.Rect") -> float:
    """Horizontal overlap as a fraction of the narrower rectangle."""
    width = min(a.x1, b.x1) - max(a.x0, b.x0)
    narrow = min(a.width, b.width) or 1.0
    return max(0.0, width) / narrow


def v_overlap(a: "pymupdf.Rect", b: "pymupdf.Rect") -> float:
    """Vertical overlap as a fraction of the shorter rectangle."""
    height = min(a.y1, b.y1) - max(a.y0, b.y0)
    short = min(a.height, b.height) or 1.0
    return max(0.0, height) / short


def merge_rects(rects: list["pymupdf.Rect"], gap: float) -> list["pymupdf.Rect"]:
    """Union rectangles that touch after growing by `gap`, until stable."""
    rects = [pymupdf.Rect(r) for r in rects]
    changed = True
    while changed:
        changed = False
        out: list[pymupdf.Rect] = []
        for rect in rects:
            for i, other in enumerate(out):
                if grow(other, gap).intersects(rect):
                    out[i] = other | rect
                    changed = True
                    break
            else:
                out.append(rect)
        rects = out
    return rects


# ------------------------------------------------------------- detection --

class PageLayout:
    """Text blocks and graphics of one page, in unrotated page coordinates."""

    def __init__(self, page: "pymupdf.Page"):
        self.page = page
        # Text and drawing coordinates are unrotated; page.rect is rotated.
        self.bounds = page.rect * page.derotation_matrix
        area = self.bounds.get_area() or 1.0
        self.captions: list[dict] = []
        self.prose: list[pymupdf.Rect] = []
        self.labels: list[pymupdf.Rect] = []
        self.text_chars = 0
        blocks = [b for b in page.get_text("blocks") if b[6] == 0]
        for x0, y0, x1, y1, text, *_ in blocks:
            rect = pymupdf.Rect(x0, y0, x1, y1) & self.bounds
            clean = " ".join(text.split())
            if RULE_TEXT_RE.match(clean):
                continue
            self.text_chars += len(clean)
            match = CAPTION_RE.match(clean)
            if match and not LEADER_RE.search(clean):
                self.captions.append({"rect": rect, "text": clean,
                                      "label": " ".join(match.group("label").split())})
            elif len(clean) >= PROSE_MIN_CHARS:
                self.prose.append(rect)
            else:
                self.labels.append(rect)
        leaders = sum(1 for b in blocks if LEADER_RE.search(b[4]))
        if leaders >= 3:
            # Contents / list-of-figures page: its "Figure N" lines are entries.
            self.labels += [c["rect"] for c in self.captions]
            self.captions = []
        self._join_caption_continuations()

        self.images: list[dict] = []
        for info in page.get_image_info(xrefs=True):
            rect = pymupdf.Rect(info["bbox"]) & self.bounds
            if rect.is_empty:
                continue
            self.images.append({"rect": rect, "xref": info.get("xref", 0)})
        # A page-sized image is a scanned page (possibly with an OCR text
        # layer). It is not a figure body; figures inside it are located from
        # their captions only and flagged.
        self.page_images = [img for img in self.images
                            if img["rect"].get_area() >= SCANNED_IMAGE_AREA * area]
        self.images = [img for img in self.images if img not in self.page_images]
        self.scanned = bool(self.page_images) and self.text_chars < SCANNED_TEXT_CHARS
        self.image_page = bool(self.page_images)

        drawings = []
        for path in page.get_drawings():
            rect = pymupdf.Rect(path["rect"])
            if not rect.is_valid or rect.get_area() > 0.9 * area:
                continue  # page background / frame
            if (rect.get_area() > 0.4 * area and path.get("fill") is not None
                    and all(item[0] in ("re", "qu") for item in path["items"])):
                continue  # plain background panel (slides, boxed pages)
            b = self.bounds
            if rect.x1 < b.x0 or rect.y1 < b.y0 or rect.x0 > b.x1 or rect.y0 > b.y1:
                continue  # entirely off-page
            drawings.append(path)
        self.vector: list[pymupdf.Rect] = []
        if drawings:
            for rect in page.cluster_drawings(drawings=drawings,
                                              x_tolerance=CLUSTER_TOLERANCE,
                                              y_tolerance=CLUSTER_TOLERANCE):
                rect = pymupdf.Rect(rect) & self.bounds
                if min(rect.width, rect.height) < 1.5 and max(rect.width, rect.height) > 0.5 * self.bounds.width:
                    continue  # a lone separator rule would chain unrelated figures
                self.vector.append(rect)

    def _join_caption_continuations(self) -> None:
        """A caption paragraph split over several blocks: absorb the blocks
        directly below that start at the same left edge."""
        for cap in self.captions:
            line_gap = 6.0
            changed = True
            while changed:
                changed = False
                for pool in (self.prose, self.labels):
                    for rect in list(pool):
                        below = 0 <= rect.y0 - cap["rect"].y1 <= line_gap
                        aligned = abs(rect.x0 - cap["rect"].x0) <= 6 and h_overlap(rect, cap["rect"]) > 0.6
                        if below and aligned:
                            cap["rect"] = cap["rect"] | rect
                            pool.remove(rect)
                            changed = True

    def regions(self) -> list["pymupdf.Rect"]:
        """Graphics regions: images + vector clusters + inner labels, merged."""
        area = self.bounds.get_area() or 1.0
        graphics = [img["rect"] for img in self.images] + list(self.vector)
        graphics = [r for r in graphics if r.width > 0 or r.height > 0]
        regions = merge_rects(graphics, MERGE_GAP)
        regions = [r for r in regions
                   if max(r.width, r.height) >= MIN_REGION_SIDE and r.get_area() >= MIN_REGION_AREA * area]
        # Absorb short label text that sits on or right next to a region.
        # Labels must not bridge two figures, so absorbed regions are only
        # re-merged when they actually overlap.
        changed = True
        while changed:
            changed = False
            for i in range(len(regions)):
                for label in self.labels:
                    if label not in regions[i] and grow(regions[i], 4).intersects(label):
                        regions[i] = regions[i] | label
                        changed = True
            regions = merge_rects(regions, 0.5)
        # A near-full-page region holding running prose is a text frame or
        # page decoration, not a figure body.
        def is_text_frame(region):
            return (region.get_area() >= 0.8 * area
                    and any((region & p).get_area() > 0.5 * p.get_area() for p in self.prose))
        return [r for r in regions if not is_text_frame(r)]


def blocked_between(a: "pymupdf.Rect", b: "pymupdf.Rect", walls: list["pymupdf.Rect"]) -> bool:
    """True if a prose block or caption lies vertically between a and b."""
    top, bottom = (a, b) if a.y1 <= b.y0 else (b, a)
    for wall in walls:
        if wall.y0 >= top.y1 - 1 and wall.y1 <= bottom.y0 + 1 and (h_overlap(wall, a) > 0.3 or h_overlap(wall, b) > 0.3):
            return True
    return False


def vertical_gap(region: "pymupdf.Rect", caption: "pymupdf.Rect") -> float:
    """Distance between region and caption; 0 when their boxes overlap
    (image boxes often include whitespace that runs into the caption)."""
    return max(0.0, caption.y0 - region.y1, region.y0 - caption.y1)


def is_above(region: "pymupdf.Rect", caption: "pymupdf.Rect") -> bool:
    return (region.y0 + region.y1) / 2 < (caption.y0 + caption.y1) / 2


def detect_figures(layout: PageLayout, pad: float) -> list[dict]:
    """Return figure candidates: caption-anchored first, then leftovers."""
    regions = layout.regions()
    max_gap = CAPTION_MAX_GAP * layout.bounds.height
    captions = sorted(layout.captions, key=lambda c: c["rect"].y0)
    owner: dict[int, int] = {}       # region index -> caption index
    body_of: dict[int, list[int]] = {}

    def walls_for(ci: int) -> list:
        return layout.prose + [c["rect"] for k, c in enumerate(captions) if k != ci]

    def candidates(ci: int, preferred_only: bool):
        cap = captions[ci]
        crect = cap["rect"]
        is_table = bool(TABLE_RE.match(cap["text"]))
        for ri, region in enumerate(regions):
            if h_overlap(region, crect) < 0.3:
                continue
            gap = vertical_gap(region, crect)
            if gap > max_gap or blocked_between(region, crect, walls_for(ci)):
                continue
            # Figures usually sit above their caption, tables below theirs.
            if preferred_only and is_above(region, crect) == is_table:
                continue
            yield gap, ci, ri

    # Nearest caption-region pairs win, first on the preferred side, then the other.
    for preferred_only in (True, False):
        pairs = sorted(p for ci in range(len(captions)) if ci not in body_of
                       for p in candidates(ci, preferred_only))
        for _gap, ci, ri in pairs:
            if ci in body_of or ri in owner:
                continue
            owner[ri] = ci
            body_of[ci] = [ri]

    # Multi-panel: free regions on the same side of the caption that sit in
    # the same row as an accepted panel or above/below the caption itself
    # (captions are often narrower than the figure), and are not separated
    # from it by prose or another caption. Repeat until no panel is added.
    for ci, members in body_of.items():
        crect = captions[ci]["rect"]
        walls = walls_for(ci)
        above = is_above(regions[members[0]], crect)
        added = True
        while added:
            added = False
            body = pymupdf.Rect(regions[members[0]])
            for ri in members[1:]:
                body |= regions[ri]
            for ri, region in enumerate(regions):
                if ri in owner or is_above(region, crect) != above:
                    continue
                same_row = any(v_overlap(region, regions[m]) > 0.5 for m in members)
                if not same_row and h_overlap(region, crect | body) < 0.2:
                    continue
                if vertical_gap(region, crect) > max_gap:
                    continue
                if blocked_between(region, crect, walls) or blocked_between(region, body, walls):
                    continue
                owner[ri] = ci
                members.append(ri)
                added = True

    figures = []
    for ci, cap in enumerate(captions):
        crect = cap["rect"]
        is_table = bool(TABLE_RE.match(cap["text"]))
        flags = []
        if ci in body_of:
            body = pymupdf.Rect(regions[body_of[ci][0]])
            for ri in body_of[ci][1:]:
                body |= regions[ri]
            if len(body_of[ci]) > 1:
                flags.append("multi_panel_merged")
        else:
            # Caption with no detected graphics: take the band between the
            # caption and the nearest prose/caption on the expected side.
            body = caption_band(layout, crect, is_table)
            flags.append("caption_without_graphics")
        figures.append({
            "label": cap["label"], "caption": cap["text"], "caption_rect": crect,
            "body": body, "crop": grow(body | crect, 0 if "caption_without_graphics" in flags else pad)
            & layout.bounds, "flags": flags,
            "kind": "table" if is_table else "figure",
        })

    for ri, region in enumerate(regions):
        if ri in owner:
            continue
        figures.append({
            "label": "", "caption": "", "caption_rect": None, "body": region,
            "crop": grow(region, pad) & layout.bounds, "flags": ["no_caption"], "kind": "figure",
        })

    # A figure split by a page break: graphics at the foot of one page,
    # caption at the head of the next.
    edge = 0.2 * layout.bounds.height
    for fig in figures:
        if "caption_without_graphics" in fig["flags"] and fig["caption_rect"].y0 < layout.bounds.y0 + edge:
            fig["flags"].append("graphics_maybe_previous_page")
        if "no_caption" in fig["flags"] and fig["body"].y1 > layout.bounds.y1 - edge:
            fig["flags"].append("caption_maybe_next_page")

    for fig in figures:
        if layout.image_page:
            fig["flags"].append("scanned_page")
        overlap = [p for p in layout.prose if (fig["crop"] & p).get_area() > 0.25 * p.get_area()]
        if overlap:
            fig["flags"].append("crop_overlaps_prose")
        if fig["crop"].get_area() > 0.8 * layout.bounds.get_area():
            fig["flags"].append("near_full_page")
    figures.sort(key=lambda f: (f["crop"].y0, f["crop"].x0))
    return figures


def caption_band(layout: PageLayout, crect: "pymupdf.Rect", is_table: bool) -> "pymupdf.Rect":
    """Fallback body for a caption whose graphics were not detected (scans,
    unusual drawing operators): the whole slot between the nearest prose or
    caption above and below it, across the text column. Generous on purpose -
    it may include white space but does not cut a side-by-side figure."""
    walls = layout.prose + [c["rect"] for c in layout.captions if c["rect"] != crect]
    reach = CAPTION_MAX_GAP * layout.bounds.height
    above = [w.y1 for w in walls if w.y1 <= crect.y0 + 1 and h_overlap(w, crect) > 0.3]
    below = [w.y0 for w in walls if w.y0 >= crect.y1 - 1 and h_overlap(w, crect) > 0.3]
    y0 = max(above, default=max(crect.y0 - reach, layout.bounds.y0))
    y1 = min(below, default=min(crect.y1 + reach, layout.bounds.y1))
    if is_table:
        y0 = crect.y0  # a table follows its caption
    column = layout.prose or [crect]
    x0 = min(r.x0 for r in column + [crect])
    x1 = max(r.x1 for r in column + [crect])
    return pymupdf.Rect(x0, y0, x1, y1)


# ---------------------------------------------------------------- output --

def native_image(layout: PageLayout, body: "pymupdf.Rect") -> dict | None:
    """The single embedded image that makes up this figure body, if any."""
    if any((v & body).get_area() > 0.05 * body.get_area() for v in layout.vector):
        return None
    inside = [img for img in layout.images if (img["rect"] & body).get_area() > 0]
    if len(inside) != 1 or not inside[0]["xref"]:
        return None
    rect = inside[0]["rect"]
    if (rect & body).get_area() < NATIVE_IMAGE_COVER * min(rect.get_area(), body.get_area()):
        return None
    if rect.get_area() < NATIVE_IMAGE_COVER * body.get_area() * 0.8:
        return None  # image is only part of the figure
    return inside[0]


def save_native(doc: "pymupdf.Document", xref: int, stem: Path) -> Path | None:
    try:
        info = doc.extract_image(xref)
    except Exception:
        return None
    if not info or not info.get("image"):
        return None
    if info.get("smask"):
        try:
            pix = pymupdf.Pixmap(pymupdf.Pixmap(doc, xref), pymupdf.Pixmap(doc, info["smask"]))
            out = stem.with_name(stem.name + "_native.png")
            pix.save(str(out))
            return out
        except Exception:
            pass
    out = stem.with_name(f"{stem.name}_native.{info['ext']}")
    out.write_bytes(info["image"])
    return out


def draw_overview(page: "pymupdf.Page", figures: list[dict], path: Path, dpi: int) -> None:
    """Low-res page render with crops boxed, ids written, and point ticks."""
    scratch = pymupdf.open()
    scratch.insert_pdf(page.parent, from_page=page.number, to_page=page.number)
    spage = scratch[0]
    shape = spage.new_shape()
    bounds = spage.rect * spage.derotation_matrix
    grey = (0.4, 0.4, 0.4)
    for tick in range(0, int(max(bounds.width, bounds.height)) + 1, 50):
        if tick <= bounds.width:
            shape.insert_text((tick + 1, 7), str(tick), fontsize=5, color=grey, rotate=spage.rotation)
        if tick <= bounds.height:
            shape.insert_text((1, tick + 6), str(tick), fontsize=5, color=grey, rotate=spage.rotation)
    for fig in figures:
        color = (0.85, 0.1, 0.1) if fig["flags"] and fig["flags"] != ["multi_panel_merged"] else (0.0, 0.55, 0.0)
        shape.draw_rect(fig["crop"])
        shape.finish(color=color, width=1.5)
        shape.insert_text((fig["crop"].x0 + 2, fig["crop"].y0 + 9), fig["id"], fontsize=8,
                          color=color, rotate=spage.rotation)
    shape.commit()
    spage.get_pixmap(dpi=dpi).save(str(path))
    scratch.close()


def render_clip(page: "pymupdf.Page", rect: "pymupdf.Rect") -> "pymupdf.Rect":
    """Unrotated crop rectangle -> the (rotated) space get_pixmap clips in."""
    return pymupdf.Rect(rect) * page.rotation_matrix


def write_outputs(doc, page, layout, figures, figdir: Path, args) -> list[dict]:
    entries = []
    for fig in figures:
        stem = figdir / fig["id"]
        files = {}
        pix = page.get_pixmap(dpi=args.dpi, clip=render_clip(page, fig["crop"]))
        pix.save(str(stem.with_suffix(".png")))
        files["png"] = f"figures/{fig['id']}.png"
        image = native_image(layout, fig["body"])
        if image:
            native = save_native(doc, image["xref"], stem)
            if native:
                files["native"] = f"figures/{native.name}"
        if args.vector_pdf:
            single = pymupdf.open()
            single.insert_pdf(doc, from_page=page.number, to_page=page.number)
            single[0].set_cropbox(fig["crop"] + (page.cropbox.x0, page.cropbox.y0) * 2)
            single.save(str(stem.with_suffix(".pdf")), garbage=3, deflate=True)
            single.close()
            files["pdf"] = f"figures/{fig['id']}.pdf"
        graphics = "raster" if image else (
            "vector" if not any((i["rect"] & fig["body"]).get_area() for i in layout.images) else "mixed")
        if "caption_without_graphics" in fig["flags"]:
            graphics = "unknown"
        entries.append({
            "id": fig["id"], "page": page.number + 1, "kind": fig["kind"], "label": fig["label"],
            "caption": fig["caption"], "graphics": graphics, "method": fig.get("method", "auto"),
            "crop_bbox": rect_list(fig["crop"]),
            "caption_bbox": rect_list(fig["caption_rect"]) if fig["caption_rect"] else None,
            "size_px": [pix.width, pix.height], "dpi": args.dpi, "files": files,
            "flags": fig["flags"], "review": "pending",
        })
    return entries


# ------------------------------------------------------------ cache/index --

def load_manifest(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def write_index(source_dir: Path, manifest: dict) -> None:
    src = manifest["source"]
    lines = [
        f"# Figures: {src['name']}", "",
        f"- SHA-256: `{src['sha256']}`",
        f"- Pages in file: {src['page_count']}; extracted: {compact_pages(manifest['pages'])}",
        f"- Tool: pdf_figures.py {manifest['tool_version']}, PyMuPDF {manifest['pymupdf_version']}, "
        f"{manifest['settings']['dpi']} dpi",
        "- Page numbers are PDF file pages. Check `overview/` for any flagged row before use.",
        "",
    ]
    scanned = [p for p, v in sorted(manifest["pages"].items(), key=lambda kv: int(kv[0])) if v["status"] == "scanned"]
    if scanned:
        lines += [f"- Scanned pages (no crops; OCR/vision needs a user decision): {', '.join(scanned)}", ""]
    lines += ["| id | page | label | graphics | flags | review | crop (with caption) | native image | caption |",
              "| --- | ---: | --- | --- | --- | --- | --- | --- | --- |"]
    for fig in sorted(manifest["figures"], key=lambda f: (f["page"], f["id"])):
        caption = fig["caption"].replace("|", "\\|")
        if len(caption) > 140:
            caption = caption[:137] + "..."
        lines.append(f"| {fig['id']} | {fig['page']} | {fig['label']} | {fig['graphics']} | "
                     f"{', '.join(fig['flags']) or '-'} | {fig['review']} | {fig['files']['png']} | "
                     f"{fig['files'].get('native', '-')} | {caption} |")
    (source_dir / "INDEX.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_root_index(cache_dir: Path) -> None:
    rows = ["# PDF figure cache", "",
            "One directory per source PDF, keyed by SHA-256. Read the source's INDEX.md before re-extracting.", "",
            "| source | sha256 | pages extracted | figures | directory |", "| --- | --- | --- | ---: | --- |"]
    for manifest_path in sorted(cache_dir.glob("*/manifest.json")):
        data = load_manifest(manifest_path)
        if not data or data.get("schema") != SCHEMA:
            continue
        src = data["source"]
        rows.append(f"| {src['name']} | `{src['sha256'][:12]}` | {compact_pages(data['pages'])} | "
                    f"{len(data['figures'])} | {manifest_path.parent.name}/ |")
    (cache_dir / "INDEX.md").write_text("\n".join(rows) + "\n", encoding="utf-8")


def compact_pages(pages: dict) -> str:
    numbers = sorted(int(p) for p in pages)
    if not numbers:
        return "none"
    spans, start, prev = [], numbers[0], numbers[0]
    for n in numbers[1:]:
        if n != prev + 1:
            spans.append(f"{start}-{prev}" if start != prev else str(start))
            start = n
        prev = n
    spans.append(f"{start}-{prev}" if start != prev else str(start))
    return ",".join(spans)


def parse_manual(spec: str) -> tuple[int, "pymupdf.Rect", str]:
    parts = spec.split(":", 2)
    if len(parts) < 2:
        raise SystemExit(f"--manual-crop expects PAGE:x0,y0,x1,y1[:label], got {spec!r}")
    coords = [float(x) for x in parts[1].split(",")]
    if len(coords) != 4:
        raise SystemExit(f"--manual-crop needs four coordinates, got {spec!r}")
    return int(parts[0]), pymupdf.Rect(*coords), parts[2] if len(parts) > 2 else ""


# ------------------------------------------------------------------ main --

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pdf", type=Path)
    ap.add_argument("--pages", default=None,
                    help='PDF pages to extract, e.g. "3,7-9" or "all" (required unless --list/--review)')
    ap.add_argument("--cache-dir", type=Path, default=None,
                    help=f"cache root (default ${CACHE_ENV} or ./{DEFAULT_CACHE.as_posix()})")
    ap.add_argument("--dpi", type=int, default=300, help="render resolution for crops (default 300)")
    ap.add_argument("--pad", type=float, default=6.0, help="margin around each crop in points (default 6)")
    ap.add_argument("--vector-pdf", action="store_true", help="also save a cropped single-page vector PDF")
    ap.add_argument("--overview-dpi", type=int, default=60, help="overview render resolution (default 60)")
    ap.add_argument("--force", action="store_true", help="re-extract requested pages even if cached")
    ap.add_argument("--manual-crop", action="append", default=[], metavar="PAGE:x0,y0,x1,y1[:label]",
                    help="add a hand-checked crop in unrotated PDF points; kept across re-runs")
    ap.add_argument("--review", action="append", default=[], metavar="ID=STATUS",
                    help="record a visual check: ok, recrop or reject")
    ap.add_argument("--list", action="store_true", help="print the cached INDEX.md and exit")
    args = ap.parse_args()

    if not args.pdf.is_file():
        sys.exit(f"File not found: {args.pdf}")
    cache_dir = args.cache_dir or Path(os.environ.get(CACHE_ENV) or DEFAULT_CACHE)
    sha = sha256_file(args.pdf)
    source_dir = cache_dir / f"{slug(args.pdf.stem)}-{sha[:12]}"
    manifest_path = source_dir / "manifest.json"
    manifest = load_manifest(manifest_path)

    if args.list:
        index = source_dir / "INDEX.md"
        if not index.exists():
            print(f"no cache for {args.pdf.name} (sha {sha[:12]}) under {cache_dir}", file=sys.stderr)
            return 1
        print(index.read_text(encoding="utf-8"))
        return 0

    settings = {"dpi": args.dpi, "pad": args.pad, "vector_pdf": args.vector_pdf,
                "tool_version": TOOL_VERSION}
    doc = pymupdf.open(str(args.pdf))
    if manifest is None or manifest.get("schema") != SCHEMA:
        manifest = {"schema": SCHEMA, "pages": {}, "figures": []}
    elif manifest.get("settings") != settings and args.pages:
        print("settings changed since the cache was built; requested pages will be re-extracted",
              file=sys.stderr)
        args.force = True
    manifest.update({
        "tool_version": TOOL_VERSION, "pymupdf_version": pymupdf.VersionBind,
        "settings": settings,
        "source": {"name": args.pdf.name, "path": str(args.pdf), "sha256": sha,
                   "bytes": args.pdf.stat().st_size, "page_count": doc.page_count},
    })

    figdir, overdir = source_dir / "figures", source_dir / "overview"
    if not (args.pages or args.manual_crop or args.review):
        sys.exit("nothing to do: give --pages, --manual-crop, --review or --list")
    figdir.mkdir(parents=True, exist_ok=True)
    overdir.mkdir(parents=True, exist_ok=True)

    pages = parse_pages(args.pages, doc.page_count) if args.pages else []
    manual_by_page: dict[int, list] = {}
    for spec in args.manual_crop:
        pno, rect, label = parse_manual(spec)
        if not 1 <= pno <= doc.page_count:
            sys.exit(f"--manual-crop page {pno} is out of range")
        manual_by_page.setdefault(pno, []).append((rect, label))

    reused = extracted = 0
    for pno in sorted(set(pages) | set(manual_by_page)):
        key = str(pno)
        cached = key in manifest["pages"]
        if cached and not args.force and pno not in manual_by_page:
            reused += 1
            continue
        page = doc[pno - 1]
        layout = PageLayout(page)
        keep = [f for f in manifest["figures"] if f["page"] == pno and f["method"] == "manual"]
        if cached and not args.force and pno in manual_by_page:
            # Only adding manual crops: keep the automatic ones as they are.
            keep = [f for f in manifest["figures"] if f["page"] == pno]
        manifest["figures"] = [f for f in manifest["figures"] if f["page"] != pno]
        for old in Path(figdir).glob(f"p{pno:04d}-*"):
            if not any(old.name.startswith(f["id"]) for f in keep):
                old.unlink()

        if layout.scanned and pno not in manual_by_page:
            figures = []
            status = "scanned"
        elif cached and not args.force:
            figures = []
            status = manifest["pages"][key]["status"]
        else:
            figures = detect_figures(layout, args.pad)
            status = "figures" if figures else "none"
        for n, fig in enumerate(figures, start=1):
            fig["id"] = f"p{pno:04d}-f{n:02d}"
        taken = {f["id"] for f in keep}
        manual = []
        for rect, label in manual_by_page.get(pno, []):
            n = 1
            while f"p{pno:04d}-m{n:02d}" in taken:
                n += 1
            fid = f"p{pno:04d}-m{n:02d}"
            taken.add(fid)
            caption = next((c["text"] for c in layout.captions if (c["rect"] & rect).get_area() > 0), "")
            manual.append({"id": fid, "label": label, "caption": caption, "caption_rect": None,
                           "body": rect & layout.bounds, "crop": rect & layout.bounds, "flags": [],
                           "kind": "table" if TABLE_RE.match(label or caption) else "figure",
                           "method": "manual"})
        entries = write_outputs(doc, page, layout, figures + manual, figdir, args)
        for entry in entries:
            if entry["method"] == "manual":
                entry["review"] = "ok"  # a manual crop is the human/agent visual decision
        manifest["figures"].extend(keep + entries)
        boxes = [dict(f, crop=pymupdf.Rect(f["crop_bbox"])) for f in keep + entries]
        draw_overview(page, boxes, overdir / f"p{pno:04d}.png", args.overview_dpi)
        manifest["pages"][key] = {
            "status": "scanned" if layout.scanned else ("figures" if keep or entries else status),
            "extracted_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        }
        extracted += 1

    known = {f["id"]: f for f in manifest["figures"]}
    for spec in args.review:
        fid, _, status = spec.partition("=")
        if fid not in known or status not in {"ok", "recrop", "reject"}:
            sys.exit(f"--review expects ID=ok|recrop|reject for a cached id, got {spec!r}")
        known[fid]["review"] = status

    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_index(source_dir, manifest)
    write_root_index(cache_dir)
    doc.close()

    requested = [f for f in manifest["figures"] if f["page"] in set(pages) | set(manual_by_page)]
    flagged = [f for f in requested if set(f["flags"]) - {"multi_panel_merged"} and f["review"] == "pending"]
    scanned = [p for p in pages if manifest["pages"].get(str(p), {}).get("status") == "scanned"]
    print(f"{source_dir}: {extracted} page(s) extracted, {reused} reused from cache, "
          f"{len(requested)} figure(s) on requested pages")
    for fig in requested:
        print(f"  {fig['id']}  p{fig['page']}  {fig['label'] or '(no caption)'}  "
              f"{fig['graphics']}  {','.join(fig['flags']) or 'ok'}  -> {fig['files']['png']}"
              + (f" (native {fig['files']['native']})" if "native" in fig["files"] else ""))
    if scanned:
        print(f"scanned pages, not cropped (ask before OCR/vision): {scanned}")
    if flagged:
        print(f"{len(flagged)} flagged figure(s): check overview/pNNNN.png, then --review ID=ok|recrop|reject "
              f"or add --manual-crop")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
