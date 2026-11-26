# Extract-first brief (paste into any subagent brief that touches PDFs or citations)

Subagents do not receive AGENTS.md. Copy the block below into the brief verbatim,
filling in the kit path.

```text
Reference files: extract once, read small.
- Cached text lives under ${APK_CACHE_ROOT:-~/.cache/agent-project-kit-cache}/extract/<stem>-<sha12>/text.md
  (one "<!-- page N -->" marker per page). Get the directory for any PDF with:
    python3 <KIT>/scripts/apk.py extract FILE.pdf [--pages A-B]
  It reuses an existing cache by SHA-256 or creates one. Grep text.md; never run
  pdftotext/pdfplumber on the PDF yourself and never write caches elsewhere.
- Open PDF pages as images only for figures, tables, equations or layout:
  python3 <KIT>/scripts/reference_extract/pdf_render_pages.py, then read the PNG.
- No text layer: report the pages; local Tesseract comes before any AI OCR.
- Before verifying citations, read the project's evidence/citation-audit-*.md and
  re-check only keys whose PDF hash or citing sentence changed.
- Return verdicts in the citation-audit table format (key, citing sentence,
  verdict SUPPORTED/PARTLY/NOT/CANNOT CHECK, quote + page, accurate rewording)
  so the caller can save them to evidence/; do not return prose summaries only.
```
