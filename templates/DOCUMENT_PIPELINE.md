# DOCUMENT_PIPELINE

Purpose: record how this project creates documents from Markdown sources.

## Document Targets

| Name | Type | Source MD | Output | Page/Screen | Status | Notes |
|---|---|---|---|---|---|---|
|  | formal/public/teaching/internal/book | project-defined | project-defined | project-defined (A4/16:9 are non-book fallbacks only) | draft/final |  |

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

## Large Reference Source Extraction Cache

| Source + version/hash | Format | Tool | Cache path | Locator/scope extracted | Structure/media/revision handling | OCR/conversion status | Original verified? | Notes |
|---|---|---|---|---|---|---|---|---|
|  | PDF/DOCX/PPTX/ODP/EPUB/HTML/text set/other | format-native extractor |  | page/slide/section/paragraph/table; full/partial | headings/tables/notes/comments/revisions/media/layout | not needed / result / fallback reason | yes/no/n/a |  |

## Figures Extracted from Reference PDFs

Record raster/vector figures pulled from reference PDFs for compositional reference (layout examples), not for direct reuse in the final document unless rights allow it.

| Source PDF | Page (printed/file) | Figure/table ref | Type (raster/vector) | Method (direct extract/full-page render) | File path | Verified by eye? | Notes |
|---|---|---|---|---|---|---|---|
|  |  |  | raster / vector | direct extract / full-page render (+ auto-crop if used) |  | yes/no |  |

## Final QA Status

- Content approved: no
- Style approved: no
- Required output(s) generated: no
- Required paged/screen/reflow output(s) inspected with the appropriate viewer: no
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
