# Reference PDF extraction tools

เครื่องมือชุดนี้นำ workflow ที่ทดสอบแล้วจากโครงการหนังสือ fluid-mechanics มาเก็บเป็น reusable tools สำหรับหนังสือหลายเล่ม

## หลักการ

- ดึงเฉพาะช่วงหน้า/section ที่เกี่ยวข้องเมื่อทำได้ ไม่แปลง PDF ใหญ่ทั้งเล่มโดยไม่จำเป็น
- เก็บข้อความพร้อมเลขหน้า PDF และ source locator ใน reading cache หรือ evidence Markdown
- แยกภาพ raster ที่ฝังอยู่ใน PDF ออกจาก vector diagram ที่ต้อง render หน้า
- เก็บ figure, caption และข้อความรอบ figure เพื่อวิเคราะห์ลำดับการอธิบายของแหล่งอ้างอิง
- รูปจากแหล่งอ้างอิงเป็น compositional reference เท่านั้น ห้ามนำเข้าเล่มจริงโดยอัตโนมัติ
- auto-crop เป็นเพียงตัวช่วย ต้องเปิดตรวจผลทุกครั้ง; full-page render เป็น fallback ที่ปลอดภัยกว่า
- ไม่ทำ OCR โดยอัตโนมัติ ถ้า PDF เป็น scan ให้ผู้ใช้ตัดสินใจก่อนใช้ `--ocr`

## เครื่องมือ

- `pdf_text_extract.py`: ดึง text layer ตามช่วงหน้า และดึง embedded raster images ด้วย `--images`
- `pdf_render_pages.py`: render หน้า PDF เป็น PNG และเลือกเก็บ single-page vector PDF สำหรับ vector diagrams

ให้ใช้ร่วมกับ:

- `PDF_READING_CACHE_*.md`
- `EVIDENCE_*.md`
- `references/figures/INDEX.md`
- reference manifest และ citation registry ของหนังสือเป้าหมาย

## Environment

ใช้ shared `text` environment ที่มี PyMuPDF:

```bash
micromamba run -n text python scripts/reference_extract/pdf_text_extract.py \
  path/to/source.pdf 30 34 \
  --out path/to/cache/section.md \
  --images path/to/references/figures
```

สำหรับ vector figure:

```bash
micromamba run -n text python scripts/reference_extract/pdf_render_pages.py \
  path/to/source.pdf 87 \
  --out-dir path/to/references/figures \
  --label REF --vector-pdf --auto-crop
```

ถ้าไม่มี `micromamba` ให้ใช้ shared Conda-family manager ที่ติดตั้งอยู่ตาม machine profile

## Output review

หลัง extraction ต้องตรวจ:

1. PDF page กับ printed page ให้ถูกต้อง
2. caption และข้อความนำ/ตีความรูปยังอยู่ครบ
3. multi-column reading order ไม่สลับ
4. รูป vector ไม่ถูกตัด และ auto-crop ไม่ตัด caption
5. source path, edition/version หรือ hash, extraction tool/version และ scope ถูกบันทึก
6. license/access note ระบุว่ารูปเป็น reference ไม่ใช่ artwork สำหรับเผยแพร่

ถ้า source ไม่มี text layer ให้รายงานก่อน OCR และเก็บข้อจำกัดของ extraction ไว้ใน cache
