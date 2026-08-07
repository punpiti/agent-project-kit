# Document Production Policy

This policy applies to formal documents, public documents, reports, PDF handouts, slide-like screens, and any project that produces written artifacts.

## Core Principle

Start with Markdown. Improve the content until the structure, argument, evidence, and tone are acceptable. Only then generate PDF, DOCX, HTML, or slide-like outputs.

Do not jump directly into visual formatting while the content is still weak.

Preferred loop:

```text
content.md -> critique -> revised content.md -> style decision -> PDF/build -> final QA
```

For substantial documents, the project should keep:

```text
docs/source/*.md
docs/styles/*
docs/build/* or output/*
.ai/DOCUMENT_PIPELINE.md
.ai/DOCUMENT_STYLE.md
.ai/DOCUMENT_QA.md
```

## Page and Screen Defaults

- Paper documents: A4.
- Screen / presentation / web visual documents: 16:9.
- Use one shared stylesheet per project unless there is a clear reason to create variants.
- Do not create one-off formatting hacks for each document.

## Font Policy

### Formal Thai documents

For official/formal Thai documents, apply the toolchain-specific routing below:

- Word/DOCX Thai body and headings: `TH Sarabun New`, using hierarchy by
  size/weight rather than excessive decoration.
- LaTeX Thai body and headings: prefer Google Fonts `Sarabun`.
- English text: modern thin/light sans-serif where available.
- Avoid mixing many fonts.
- If the exact English font is unavailable, use a documented fallback.

Toolchain-specific Thai font routing:

- Microsoft Word / DOCX: use `TH Sarabun New`.
- LaTeX, particularly XeLaTeX or LuaLaTeX: prefer Google Fonts `Sarabun`.
- Verify the selected family and required weights before building. Font
  substitution can change Thai wrapping, pagination, and table layout.
- If a required font is missing, download/install it only when the task needs
  that output and follow the metered-network warning and approval policy.

Suggested English fallback family, in order:

```text
Inter Light / Inter
Noto Sans Light / Noto Sans
Segoe UI Light / Segoe UI
Arial
sans-serif
```

### Public-facing / published documents

For documents meant for public distribution rather than official bureaucracy:

- Choose a modern, minimal, readable font.
- Prefer thin/light appearance, but do not sacrifice readability.
- Use a restrained color palette.
- Use whitespace and hierarchy rather than heavy borders or decorations.

Suggested families:

```text
Noto Sans Thai + Inter
Noto Sans Thai + Noto Sans
IBM Plex Sans Thai + IBM Plex Sans
Sarabun + Inter
```

## Minimal Color Style

Use color, but minimally:

- 1 primary accent color
- 1 secondary accent color if needed
- neutral grays for lines/backgrounds
- avoid saturated large backgrounds unless intentionally public/poster-like

Project style should be stored in:

```text
docs/styles/document-style.css
# or
docs/styles/pandoc-template.tex
# or
.ai/DOCUMENT_STYLE.md
```

## Markdown First Rules

When creating a document:

1. Create or update Markdown source first.
2. Improve content before formatting.
3. Check argument, structure, audience, evidence, and missing sections.
4. Only generate final PDF after the Markdown is stable.
5. Keep generated files separate from source files.

AI should not force repeated user prompting for these steps. It should propose and run a complete document loop when possible.

## PDF Reference Ingestion and Cache

When a PDF is used as a reference rather than merely checked as a final output:

1. Use a PDF-to-text tool before reading it in depth, and retain the extracted
   text or Markdown as a reusable cache for later sessions.
2. If the source uses two columns, reconstruct it into a single-column reading
   order. Preserve page markers and enough structure to trace passages back to
   the source.
3. If the PDF is scanned or lacks a usable text layer, notify the user and ask
   them to decide before running OCR. State that OCR can be appropriate for an
   important source, but may be slow and may return incomplete or inaccurate
   text even though its token cost is usually modest.
4. Once the user approves OCR, use Tesseract as the first OCR attempt. Escalate
   to AI-based OCR only if Tesseract is unavailable or its output is inadequate
   for the task, and record the reason for that escalation. Run Tesseract and
   other OCR/image-processing tools through the shared Conda-family `image`
   environment.
5. For a large PDF, extract only the pages or sections needed for the current
   task when practical. Treat this as a partial cache that can be extended later
   instead of reprocessing the whole file.
6. Record the source PDF, extraction tool, extracted page range or section,
   cache path, and whether OCR was used in `.ai/DOCUMENT_PIPELINE.md` or
   `.ai/LOCAL_RESOURCES.md`. Do not imply that a partial cache covers the full
   document.

## Mandatory Thai DOCX Language/Script Finalization

AI-generated DOCX files containing Thai must not rely on visible fonts alone.
Before delivery, runs and document defaults must contain language/script metadata
that Word can use for Thai line breaking, font shaping, and spell checking:

- Thai runs: a complex-script font (`w:rFonts/@w:cs`), complex-script hint and
  run marker, and `th-TH` in `w:lang/@w:val`, `w:eastAsia`, and `w:bidi`.
- Latin runs: `en-US` language metadata without forcing the run through the
  Thai complex-script proofing path.
- Mixed Thai/Latin runs: split into script-specific runs without changing any
  character in the visible text.
- Document styles/settings: consistent Latin, East Asian, and bidirectional
  language defaults.
- All Word text stories: document body, headers, footers, footnotes, endnotes,
  and comments when present.

After generating a Thai DOCX, run:

```bash
micromamba run -n text python \
  .ai/agent-project-kit/scripts/repair_thai_wordbreak_docx.py \
  input.docx output.docx
```

This step is mandatory for every newly generated or materially rebuilt Thai
Word/DOCX file. Deliver the repaired output, not the pre-repair intermediate.
The sequence is: verify `TH Sarabun New`, generate DOCX, repair in the shared
`text` environment, verify invariants, then sample the result in Microsoft Word.
The repair must also replace legacy `TH Sarabun ๙`, `TH Sarabun IT๙`, and
`TH SarabunPSK` font references with `TH Sarabun New` throughout the DOCX.

The repair is a post-build gate, not a substitute for visual Word/PDF QA. Verify
afterward that:

- extracted text is identical before and after repair;
- the DOCX ZIP structure is valid;
- embedded images, hyperlinks, headers/footers, tables, and page geometry remain;
- Thai line wrapping and spell checking behave correctly in Microsoft Word;
- English terms use the English proofing language and are not checked with the
  Thai dictionary.

The script requires Python plus `lxml`; use the shared machine-local `text`
environment through the preferred available manager (`micromamba`, `mamba`,
`microconda`, then `conda`), not a project-local virtual environment.

## Final PDF QA

Before calling a PDF final, check:

- Thai spelling and obvious typo issues.
- Thai word breaks / line breaks are acceptable.
- Tables fit the page.
- Table columns are autofit to content/column where possible.
- No table columns are absurdly narrow or wastefully wide.
- No hanging title at the bottom of a page.
- No hanging line / orphan / widow that looks visibly bad.
- No section heading separated from its first paragraph.
- Captions stay close to figures/tables.
- Page numbers, headers, and footers are consistent if used.
- A4 documents print correctly.
- 16:9 screen documents display correctly.
- Fonts are embedded or consistently available in the target environment where possible.

## Table Rules

For final PDFs:

- Prefer autofit columns.
- Use wrapping deliberately.
- Avoid tiny unreadable font just to fit too much content.
- If a table is too wide, consider landscape A4, splitting the table, or moving detailed columns to an appendix.
- For Thai text in tables, inspect line breaking visually.

## Build Discipline

Each document project should record:

- source Markdown path
- output PDF path
- build command
- style file used
- font assumptions
- page/screen target
- final QA status

Use `.ai/DOCUMENT_PIPELINE.md` and `.ai/DOCUMENT_QA.md` for this.

## Important WSL2 / shared/synced project storage Note

Source Markdown and styles should live in shared/synced project storage so they move across machines.

Large intermediate build folders, temporary images, OCR outputs, and cache files may live outside shared/synced project storage, but must be recorded in:

```text
.ai/LOCAL_RESOURCES.md
.ai/DOCUMENT_PIPELINE.md
```

Do not assume those local build/cache files exist on every machine.

## Do not scatter Markdown drafts

Document work must remain inside a document pipeline. Do not create loose files such as `draft.md`, `notes.md`, `plan.md`, or `final.md` in the project root.

Preferred structure:

```text
documents/<document-id>/content.md
.ai/DOCUMENT_PIPELINE.md
.ai/DOCUMENT_STYLE.md
.ai/DOCUMENT_QA.md
.ai/MARKDOWN_INVENTORY.md
```

If an older project already has many Markdown drafts, first apply `MARKDOWN_ORGANIZATION_POLICY.md` and create/update `.ai/MARKDOWN_INVENTORY.md`. Register active document sources in `.ai/DOCUMENT_PIPELINE.md` before producing PDF.

## Built-in Pandoc Thai A4 Template

This package includes a reusable template for Markdown-to-PDF formal Thai A4 documents:

```text
templates/pandoc-thai-a4/
```

Use it when a project needs a formal Thai PDF and does not already have a better project-specific style. The template is designed for Pandoc + XeLaTeX and assumes Google Fonts `Sarabun` is installed. For each project, prefer copying or referencing the same style consistently rather than making one-off formatting changes per document.

Example from a project folder:

```bash
.ai/agent-project-kit/templates/pandoc-thai-a4/build-thai-a4-pdf.sh documents/<document-id>/content.md output/<document-id>.pdf
```

For final PDFs, visually inspect the rendered PDF. Automated build success is not enough.
