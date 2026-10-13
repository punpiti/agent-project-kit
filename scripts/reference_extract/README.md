# Reference PDF extraction tools

เครื่องมือชุดนี้นำ workflow ที่ทดสอบแล้วจากโครงการหนังสือ fluid-mechanics มาเก็บเป็น reusable tools สำหรับหนังสือหลายเล่ม

## หลักการ

- ดึงเฉพาะช่วงหน้า/section ที่เกี่ยวข้องเมื่อทำได้ ไม่แปลง PDF ใหญ่ทั้งเล่มโดยไม่จำเป็น
- เก็บข้อความพร้อมเลขหน้า PDF และ source locator ใน reading cache หรือ evidence Markdown
- แยกภาพ raster ที่ฝังอยู่ใน PDF ออกจาก vector diagram (`--images` มองไม่เห็น vector; `pdf_figures.py` เห็นทั้งสองแบบ)
- เก็บ figure, caption และข้อความรอบ figure เพื่อวิเคราะห์ลำดับการอธิบายของแหล่งอ้างอิง
- รูปจากแหล่งอ้างอิงเป็น compositional reference เท่านั้น ห้ามนำเข้าเล่มจริงโดยอัตโนมัติ
- แกะรูปเป็นรายรูป (ไม่เก็บทั้งหน้า) ด้วย `pdf_figures.py` ซึ่งยึด caption และรวมทุก panel
  แล้วเก็บใน cache แยกตาม SHA-256 ของไฟล์ เพื่อให้รอบถัดไปใช้ซ้ำได้ทันที
- รูปที่มี flag ต้องเปิด `overview/` ตรวจก่อนใช้; full-page render เป็น fallback ที่ปลอดภัย
- ไม่ทำ OCR โดยอัตโนมัติ ถ้า PDF เป็น scan ให้ผู้ใช้ตัดสินใจก่อนใช้ `--ocr`

## เครื่องมือ

- `pdf_text_extract.py`: ดึง text layer ตามช่วงหน้า และดึง embedded raster images ด้วย `--images`
- `pdf_figures.py`: แกะรูป/ตารางเป็นรายรูปพร้อม caption ทั้ง raster และ vector,
  render 300 dpi, เก็บภาพต้นฉบับแบบไม่ resample เมื่อรูปเป็นภาพฝังภาพเดียว,
  cache ตาม hash พร้อม `manifest.json`, `INDEX.md` และ `overview/` สำหรับตรวจด้วยตา
- `pdf_render_pages.py`: render ทั้งหน้าเป็น PNG/single-page vector PDF — ใช้เป็น fallback
  เมื่อ `pdf_figures.py` ครอปไม่ได้ (`--auto-crop` แบบ largest-cluster เลิกใช้สำหรับแกะรูป)

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

สำหรับรูป (raster หรือ vector) ให้ตรวจ cache ก่อน แล้วแกะเฉพาะหน้าที่ยังไม่มี:

```bash
T="micromamba run -n text python scripts/reference_extract/pdf_figures.py"
$T path/to/source.pdf --list                      # มี cache แล้วหรือยัง
$T path/to/source.pdf --pages 85-90               # แกะเพิ่ม; หน้าที่มีแล้วจะถูกข้าม
$T path/to/source.pdf --pages 87 --vector-pdf     # เก็บ PDF เวกเตอร์ที่ครอปแล้วด้วย
$T path/to/source.pdf --review p0087-f01=ok       # บันทึกผลตรวจด้วยตา
$T path/to/source.pdf --manual-crop "87:60,90,540,420:Figure 3.4"   # แก้ครอปเอง
```

cache เริ่มต้นอยู่ที่ `references/pdf-figures/` (เปลี่ยนด้วย `--cache-dir` หรือ
`APK_PDF_FIGURE_CACHE`) โครงสร้าง:

```text
references/pdf-figures/
  INDEX.md                      รายการ source ทั้งหมด
  <stem>-<sha12>/
    manifest.json               source path/hash, tool/PyMuPDF version, settings, หน้า, รูป, flags, review
    INDEX.md                    ตาราง id | page | label | graphics | flags | review | crop | native | caption
    figures/p0087-f01.png       crop พร้อม caption ที่ 300 dpi (+ _native.<ext>, .pdf)
    overview/p0087.png          ภาพทั้งหน้าความละเอียดต่ำ ตีกรอบทุก crop และมีสเกลเป็น PDF points
```

flags ที่ต้องตรวจ: `no_caption`, `caption_without_graphics`, `crop_overlaps_prose`,
`scanned_page`, `near_full_page`, `graphics_maybe_previous_page`, `caption_maybe_next_page`
(`multi_panel_merged` เป็นข้อมูล ไม่ใช่คำเตือน) หน้า scan จะถูกรายงานแต่ไม่ครอป

ถ้ายังต้องการทั้งหน้า (fallback):

```bash
micromamba run -n text python scripts/reference_extract/pdf_render_pages.py \
  path/to/source.pdf 87 \
  --out-dir path/to/references/figures \
  --label REF --vector-pdf
```

ถ้าไม่มี `micromamba` ให้ใช้ shared Conda-family manager ที่ติดตั้งอยู่ตาม machine profile

## Output review

หลัง extraction ต้องตรวจ:

1. PDF page กับ printed page ให้ถูกต้อง
2. caption และข้อความนำ/ตีความรูปยังอยู่ครบ
3. multi-column reading order ไม่สลับ
4. ทุกรูปที่มี flag เปิดดู `overview/` แล้ว, caption และทุก panel อยู่ใน crop, บันทึก `--review`
5. source path, edition/version หรือ hash, extraction tool/version และ scope ถูกบันทึก
6. license/access note ระบุว่ารูปเป็น reference ไม่ใช่ artwork สำหรับเผยแพร่

ถ้า source ไม่มี text layer ให้รายงานก่อน OCR และเก็บข้อจำกัดของ extraction ไว้ใน cache
