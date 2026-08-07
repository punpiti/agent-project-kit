# Document Checklist

Use this for Markdown -> PDF/DOCX/HTML/document workflows.

## Content First

- [ ] Markdown source exists and is the source of truth.
- [ ] Audience is clear.
- [ ] Purpose is clear: formal submission, public distribution, teaching handout, internal note, report, etc.
- [ ] Structure is logical before layout work starts.
- [ ] Claims are supported by evidence or marked as judgment/assumption.
- [ ] The document has been critiqued once before final formatting.

## PDF References

- [ ] Reference PDFs were converted to reusable text/Markdown before in-depth reading.
- [ ] Two-column sources were normalized to a single-column reading order.
- [ ] Scanned PDFs were disclosed to the user and OCR was not run without their decision.
- [ ] Approved OCR used Tesseract first; any AI-based OCR fallback records why Tesseract was inadequate.
- [ ] Large-PDF partial caches identify the extracted pages/sections and do not claim full coverage.
- [ ] Source PDF, extraction tool, cache path, page/section scope, and OCR status were recorded.

## Style

- [ ] Project has one shared style sheet/template.
- [ ] Paper target uses A4.
- [ ] Screen target uses 16:9.
- [ ] Formal Thai documents use TH Sarabun New for Thai text.
- [ ] Word/DOCX uses TH Sarabun New; LaTeX uses Google Fonts Sarabun unless an approved style specifies otherwise.
- [ ] Required font family and weights are installed and verified on the build machine.
- [ ] English text uses a modern thin/light sans-serif or documented fallback.
- [ ] Public documents use a modern minimal readable font set.
- [ ] Color palette is minimal and consistent.

## PDF QA

- [ ] Thai spelling/typos checked.
- [ ] Thai line breaks/word breaks inspected.
- [ ] Tables are autofit or manually adjusted to fit.
- [ ] No unreadably small table text.
- [ ] No hanging title at bottom of page.
- [ ] No bad orphan/widow/hanging line.
- [ ] Captions stay close to figures/tables.
- [ ] Page numbers/header/footer consistent where used.
- [ ] PDF opens correctly.
- [ ] Final output path recorded in `.ai/DOCUMENT_PIPELINE.md`.

## Editable Thai DOCX QA

- [ ] TH Sarabun New was available before generating the Word/DOCX file.
- [ ] The delivered file is the post-repair output, not the original generated intermediate.
- [ ] TH Sarabun ๙ / TH Sarabun IT๙ / TH SarabunPSK references were normalized to TH Sarabun New.
- [ ] Thai runs contain complex-script font/language metadata, not only a visible font name.
- [ ] Latin runs use an English/Latin proofing language.
- [ ] Mixed Thai/Latin runs were finalized with `scripts/repair_thai_wordbreak_docx.py`.
- [ ] Extracted text is identical before and after repair.
- [ ] Embedded images and hyperlinks are preserved.
- [ ] Thai line wrapping and Thai/English spell checking were sampled in Microsoft Word.
