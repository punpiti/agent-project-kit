#!/usr/bin/env python3
"""
เรนเดอร์หน้า PDF เป็นภาพ PNG และ/หรือสกัดเป็น PDF หน้าเดียวที่ยังเป็นเวกเตอร์แท้
(สำหรับใช้จริงใน LaTeX ภายหลัง) — ใช้เมื่อรูปที่ต้องการเป็น vector graphic
(เส้น/สมการวาดด้วย PDF drawing primitives) ซึ่ง pdf_text_extract.py --images ดึงไม่ได้
(--images ดึงได้เฉพาะ raster image ที่ฝังเป็นไฟล์ JPEG/PNG ในหน้า)

ค่าเริ่มต้นคือเก็บทั้งหน้า (--no-crop) เพราะปลอดภัยสุด ยัง caption ครบเสมอ
แต่มี --auto-crop ให้ลองครอปเฉพาะบริเวณรูปอัตโนมัติด้วย heuristic นี้:
  1. ดึง vector drawing paths ทั้งหมดด้วย page.get_drawings()
  2. ตัดพวกที่ยื่นออกนอกขอบหน้า (กรอบ/เส้นขอบมาร์จิ้นของเทมเพลตหนังสือ)
  3. ตัดพวกที่มีพื้นที่ใกล้เคียงทั้งหน้า (พื้นหลังเต็มหน้า)
  4. รวมกลุ่ม (cluster) เส้นทางที่เหลือด้วยระยะห่างเชิงพื้นที่ (bbox ขยาย padding แล้วเช็คซ้อนทับ)
  5. เลือกกลุ่มที่มีจำนวนเส้นทางมากที่สุดเป็น "รูป" แล้วครอปตาม bounding box ของกลุ่มนั้น + padding
ทดสอบแล้วได้ผลดีบนหน้าตัวอย่างจริง (แยกรูปจากเนื้อความ/เชิงอรรถ/ตัวอักษรท้ายหน้าได้ถูกต้อง)
แต่ไม่รับประกันทุกหน้า — หน้าที่มีหลายรูปพร้อมกัน รูปที่กินพื้นที่เกือบเต็มหน้า
หรือรูปที่อยู่ติดเนื้อความมาก อาจครอปผิดหรือครอปตกบางส่วน **ต้องเปิดดูผลลัพธ์ทุกครั้ง**
ถ้าครอปผิดให้ใช้ค่าเริ่มต้น (ทั้งหน้า) แล้วครอปเองด้วยมือแทน

ไฟล์ PDF หน้าเดียวที่ได้ (--vector-pdf) คัดลอกเนื้อหาเวกเตอร์ต้นฉบับมาตรง ๆ
(ไม่ใช่การแปลงจากภาพ raster) จึงคมชัดไม่จำกัดระดับซูม เหมาะกับ \\includegraphics
ใน LaTeX มากกว่า PNG — ยังเป็นลิขสิทธิ์ของสำนักพิมพ์เดิม ใช้เป็น compositional
reference เท่านั้น ห้ามใช้เป็นรูปจริงในเล่ม

Usage:
    python3 tools/pdf_render_pages.py <PDF> <PDF_page1> [PDF_page2 ...] --out-dir <DIR> \\
        [--dpi 200] [--label PREFIX] [--vector-pdf] [--no-png] [--auto-crop] [--crop-pad 20]

ตัวอย่าง:
    python3 tools/pdf_render_pages.py 05_references/books/White_2011_Fluid_Mechanics_7ed.pdf 87 \\
        --out-dir 02_manuscript/ch02_fluid_statics/references/figures --label W7 --vector-pdf --auto-crop

เลขหน้าที่ใส่คือเลข PDF page (1-indexed ตามที่เปิดในตัวอ่าน PDF ทั่วไป) ไม่ใช่เลขหน้าพิมพ์บนกระดาษ
ถ้าไม่แน่ใจเลข PDF page ให้เปิด pdf_text_extract.py ช่วงกว้าง ๆ ก่อนเพื่อหาเลขหน้าพิมพ์ที่ต้องการ
แล้วดูบรรทัด "--- PDF page N ---" ที่ตรงกับเลขหน้าพิมพ์นั้น
"""
import argparse
import functools
import sys
from pathlib import Path

try:
    import pymupdf as fitz  # PyMuPDF — import ผ่านชื่อใหม่ตัดคำเตือน deprecation ของชื่อ 'fitz'
except ImportError:
    print("ต้องใช้ python ของ conda env 'text' (มี pymupdf) เช่น "
          "/home/punpiti/.local/share/mamba/envs/text/bin/python3", file=sys.stderr)
    sys.exit(1)


def find_figure_bbox(page: "fitz.Page", pad: float = 20.0):
    """heuristic: filter out page-frame/background vector paths, cluster the rest by
    proximity, return bbox of the largest cluster (+ pad), or None if nothing usable found."""
    pr = page.rect
    drawings = page.get_drawings()
    candidates = []
    for d in drawings:
        r = d["rect"]
        if r.x0 < 0 or r.y0 < 0 or r.x1 > pr.width or r.y1 > pr.height:
            continue  # sticks out of page => likely a margin/frame decoration, not the figure
        if r.width * r.height > 0.9 * pr.width * pr.height:
            continue  # near full-page => likely a background fill, not the figure
        candidates.append(r)
    if not candidates:
        return None

    def expand(r, p=15):
        return fitz.Rect(r.x0 - p, r.y0 - p, r.x1 + p, r.y1 + p)

    parent = list(range(len(candidates)))

    def find(i):
        while parent[i] != i:
            i = parent[i]
        return i

    def union(i, j):
        pi, pj = find(i), find(j)
        if pi != pj:
            parent[pi] = pj

    for i in range(len(candidates)):
        for j in range(i + 1, len(candidates)):
            if expand(candidates[i]).intersects(candidates[j]):
                union(i, j)

    groups: dict[int, list] = {}
    for i in range(len(candidates)):
        groups.setdefault(find(i), []).append(candidates[i])

    largest = max(groups.values(), key=len)
    bbox = functools.reduce(lambda a, b: a | b, largest)
    return fitz.Rect(bbox.x0 - pad, bbox.y0 - pad, bbox.x1 + pad, bbox.y1 + pad) & pr


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pdf", type=Path)
    ap.add_argument("pages", type=int, nargs="+", help="เลข PDF page (1-indexed) ที่จะเรนเดอร์")
    ap.add_argument("--out-dir", type=Path, required=True)
    ap.add_argument("--dpi", type=int, default=200)
    ap.add_argument("--label", type=str, default=None,
                     help="คำนำหน้าชื่อไฟล์ (เช่นชื่อย่อหนังสือ W7/CC3/E10) ค่าเริ่มต้นใช้ pdf stem")
    ap.add_argument("--vector-pdf", action="store_true",
                     help="สกัดหน้านั้นเป็น PDF หน้าเดียว (เวกเตอร์แท้ ไม่ re-render) เพิ่มจาก PNG "
                          "— ใช้เมื่อจะเอาไป \\includegraphics ใน LaTeX ภายหลัง")
    ap.add_argument("--no-png", action="store_true", help="ข้ามการเรนเดอร์ PNG (ใช้กับ --vector-pdf เท่านั้น)")
    ap.add_argument("--auto-crop", action="store_true",
                     help="ลองครอปเฉพาะบริเวณรูปอัตโนมัติ (heuristic, ไม่รับประกันทุกหน้า — เปิดดูผลลัพธ์เสมอ) "
                          "ใช้ได้ทั้งกับ PNG และ --vector-pdf; ถ้าหาบริเวณรูปไม่ได้จะ fallback เป็นทั้งหน้า")
    ap.add_argument("--crop-pad", type=float, default=20.0, help="ระยะขอบเพิ่มรอบบริเวณรูปที่ครอปได้ (points)")
    args = ap.parse_args()

    if not args.pdf.exists():
        print(f"ไม่พบไฟล์ {args.pdf}", file=sys.stderr)
        return 1
    if args.no_png and not args.vector_pdf:
        print("--no-png ต้องใช้คู่กับ --vector-pdf (ไม่งั้นจะไม่ได้ไฟล์ output เลย)", file=sys.stderr)
        return 1
    args.out_dir.mkdir(parents=True, exist_ok=True)

    label = args.label or args.pdf.stem
    doc = fitz.open(args.pdf)
    saved = []
    for pno in args.pages:
        if pno < 1 or pno > doc.page_count:
            print(f"ข้าม PDF page {pno}: อยู่นอกช่วง (เอกสารมี {doc.page_count} หน้า)", file=sys.stderr)
            continue
        page = doc[pno - 1]

        crop = None
        suffix = "fullpage"
        if args.auto_crop:
            crop = find_figure_bbox(page, pad=args.crop_pad)
            if crop is None or crop.is_empty:
                print(f"  [PDF page {pno}] auto-crop หาบริเวณรูปไม่ได้ ใช้ทั้งหน้าแทน", file=sys.stderr)
                crop = None
            else:
                suffix = "autocrop"

        if not args.no_png:
            pix = page.get_pixmap(dpi=args.dpi, clip=crop)
            out_path = args.out_dir / f"{label}_PDFp{pno}_{suffix}.png"
            pix.save(str(out_path))
            saved.append(out_path)
            print(f"saved {out_path} ({pix.width}x{pix.height} @ {args.dpi}dpi)")

        if args.vector_pdf:
            single = fitz.open()
            single.insert_pdf(doc, from_page=pno - 1, to_page=pno - 1)
            if crop is not None:
                single[0].set_cropbox(crop)
            vec_path = args.out_dir / f"{label}_PDFp{pno}_{suffix}_vector.pdf"
            single.save(str(vec_path))
            single.close()
            saved.append(vec_path)
            note = "ครอปอัตโนมัติแล้ว แต่ยังควรเปิดตรวจ" if crop is not None else "ทั้งหน้า — ครอปด้วย pdfcrop ก่อนใช้จริง"
            print(f"saved {vec_path} (vector, single page — {note})")
    doc.close()

    if saved:
        print(f"\nรวม {len(saved)} ไฟล์ — อย่าลืม: "
              f"(1) เปิดดูภาพ/ไฟล์ยืนยันว่าตรงรูป/มี caption จริง/ครอปไม่ตัดขาด "
              f"(บางครั้งรูปที่อ้างถึงอยู่หน้าถัดไป, auto-crop อาจครอปผิดบางหน้า) "
              f"(2) เพิ่มแถวใน references/figures/INDEX.md (ไฟล์ | แหล่ง | เลขหน้า | รูปที่มี | caption | ใช้ในหัวข้อ) "
              f"(3) โน้ตชื่อไฟล์ไว้ใน EVIDENCE_x.x.x.md ที่เกี่ยวข้อง")
    return 0


if __name__ == "__main__":
    sys.exit(main())
