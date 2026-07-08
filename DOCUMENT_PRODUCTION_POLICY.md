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

For official/formal Thai documents:

- Thai body text: `TH Sarabun New`.
- Thai headings: `TH Sarabun New`, using hierarchy by size/weight, not excessive decoration.
- English text: modern thin/light sans-serif where available.
- Avoid mixing many fonts.
- If the exact English font is unavailable, use a documented fallback.

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

Use it when a project needs a formal Thai PDF and does not already have a better project-specific style. The template is designed for Pandoc + XeLaTeX and assumes `TH Sarabun New` is installed. For each project, prefer copying or referencing the same style consistently rather than making one-off formatting changes per document.

Example from a project folder:

```bash
.ai/computing-environment/templates/pandoc-thai-a4/build-thai-a4-pdf.sh documents/<document-id>/content.md output/<document-id>.pdf
```

For final PDFs, visually inspect the rendered PDF. Automated build success is not enough.
