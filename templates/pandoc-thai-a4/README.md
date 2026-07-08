# Pandoc Thai A4 PDF Template

ใช้สำหรับแปลง Markdown ภาษาไทยเป็น PDF ด้วย format เดียวกับเอกสาร KU council:

- A4
- margin 2 cm
- font: TH Sarabun New
- XeLaTeX Thai line breaking
- มี fallback สำหรับสัญลักษณ์ `€` เพื่อกันปัญหา missing glyph ใน inline code/table
- รองรับ raw LaTeX ใน Markdown เช่น `\newpage`, `\newgeometry`, `\includegraphics`

## วิธีใช้

จากโฟลเดอร์ที่มีไฟล์ Markdown:

```bash
/mnt/c/Users/<windows-user>/shared/synced project storage/computing-environment/templates/pandoc-thai-a4/build-thai-a4-pdf.sh input.md output.pdf
```

หรือเรียก `pandoc` โดยตรง:

```bash
pandoc input.md \
  --defaults="/mnt/c/Users/<windows-user>/shared/synced project storage/computing-environment/templates/pandoc-thai-a4/thai-a4-defaults.yaml" \
  --resource-path=".:/mnt/c/Users/<windows-user>/shared/synced project storage/computing-environment/templates/pandoc-thai-a4" \
  -o output.pdf
```

ถ้าไฟล์ Markdown มีรูปแนบ ให้วางรูปไว้ในโฟลเดอร์เดียวกับไฟล์ Markdown หรือเพิ่ม path ของรูปใน `--resource-path`

## หมายเหตุ

ต้องมี `pandoc`, `xelatex`, ฟอนต์ `TH Sarabun New`, และฟอนต์ `DejaVu Sans` ในเครื่อง
