# DOCUMENT_PIPELINE

Purpose: record how this project creates documents from Markdown sources.

## Document Targets

| Name | Type | Source MD | Output | Page/Screen | Status | Notes |
|---|---|---|---|---|---|---|
|  | formal/public/teaching/internal | docs/source/main.md | docs/output/main.pdf | A4 / 16:9 | draft/final |  |

## Source of Truth

- Markdown source folder:
- Figures folder:
- Tables/data source:
- Style/template path:
- Bibliography path, if any:

## Build Commands

```bash
# Example only; replace with project command
make pdf
```

## Build Dependencies

- Document toolchain in `text` (Markdown/Pandoc/Quarto/LaTeX/WeasyPrint/etc.):
- Shared Conda-family environment (`text`, `image`, or `ml`) and selected manager:
- Node environment:
- Fonts required:
- Thai font route: Word/DOCX = TH Sarabun New; LaTeX = Google Fonts Sarabun

## Local / Non-shared/synced project storage Build Resources

Record large temporary files, caches, OCR images, exported figures, or external datasets used to build documents.

| Resource | Machine | Path | Required for full build? | Portable alternative | Notes |
|---|---|---|---|---|---|
|  | known machine roles |  | yes/no |  |  |

## PDF Reference Extraction Cache

| Source PDF | Tool | Cache path | Pages/sections extracted | Layout normalization | OCR status / fallback reason | Notes |
|---|---|---|---|---|---|---|
|  | PDF-to-text / Tesseract / AI OCR |  | full / explicit partial scope | single-column / not needed | not needed / Tesseract result / AI fallback reason |  |

## Final QA Status

- Content approved: no
- Style approved: no
- PDF generated: no
- PDF visually inspected: no
- Tables checked: no
- Thai word breaks checked: no
- Hanging titles/lines checked: no
- Final file ready: no

## Last Document Session

- Date:
- Machine:
- What changed:
- Build/test command:
- Result:
- Next action:
