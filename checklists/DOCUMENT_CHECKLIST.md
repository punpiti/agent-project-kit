# Document Checklist

Use this for Markdown -> PDF/DOCX/HTML/document workflows.

## Content First

- [ ] Markdown source exists and is the source of truth.
- [ ] Audience is concrete enough to guide explanation depth: relevant education/domain, experience, reading goal, and use context are known or explicitly unresolved.
- [ ] Required prerequisite topics are listed as confirmed, uncertain, or missing; degree/title alone is not treated as proof of readiness.
- [ ] Uncertain readiness is checked with the author/learners or a short diagnostic, and each gap has an inline recap, appendix, or named pre-reading path.
- [ ] Books/textbooks include reader-facing pre-reading guidance and a prerequisite outline that states why each foundation matters and where it will be used.
- [ ] Purpose is clear: formal submission, public distribution, teaching handout, internal note, report, etc.
- [ ] Structure is logical before layout work starts.
- [ ] Claims are supported by evidence or marked as judgment/assumption.
- [ ] The document has been critiqued once before final formatting.

## Scientific Prose / Trust (when applicable)

- [ ] Every topic's prominence follows its relevance to the research questions, impact on conclusions, and evidence. Chat duration, repetition, recency, or repeated repairs do not promote minor details into main contributions, findings, or limitations; title, abstract, introduction, discussion, and conclusion retain proportionate emphasis after local edits.
- [ ] The manuscript does not disparage its own contribution; scope and limitations are stated as verifiable facts with their implications, without hiding unfavorable results or uncertainty.
- [ ] All compared methods, including the authors' method, use consistent reporting criteria and tone. Selective results, adjectives, ordering, detail, or visual emphasis do not privilege any comparator; actual differences are reported with their magnitude, conditions, and available uncertainty.
- [ ] After iterative edits, section structure and space still follow the research questions, method roles, and evidence. No comparator gains a dedicated section or extra prominence merely because it was discussed later or more often in chat; a separate section has a substantive rationale or an explicit author instruction and still meets fair-comparison criteria.
- [ ] Methods states the actual data, processing, parameters/criteria, justification, and outputs needed to understand the analysis.
- [ ] Internal artifacts such as notebooks, caches, archives, file layout, or workflow history do not substitute for research objects or method descriptions.
- [ ] Parameter provenance is not presented as scientific justification; operational or uncalibrated values are labeled accurately.
- [ ] Captions describe figures/tables while the necessary method remains self-contained in Methods.
- [ ] Reproducibility, methodological validity, and independent validation are evaluated separately.
- [ ] Any method/parameter change has a documented lineage and downstream impact/recomputation check before prose polishing.
- [ ] The same research object keeps the same term throughout the document.
- [ ] Experiment configurations have consistent, immediately meaningful names; no configuration codes or research-question codes (e.g. RQ1, RQ2) appear as labels or references in the article, figures, tables, captions, or reader-facing supplements. Defining a code once does not satisfy this gate; refer to the experiment or question by its substance.
- [ ] No term, abbreviation, or symbol is used before it is defined, and no ad hoc variable or label is introduced only for internal back-reference.
- [ ] Every reference has a PDF in the project or a DOI/URL that reaches the original; every cited claim is actually stated in that source, with the supporting page or section recorded.
- [ ] Every figure states what the reader should look at and where (panel, region, period, line), using callouts in the figure when needed.
- [ ] For a Thai review draft of an English manuscript: opening sentences are punch lines, the first paragraph leads to the problem statement and all others support it, technical terms carry the English term in parentheses at first use, and scope concerns go in a separate review note rather than the text. When translating the reviewed Thai draft back to English, sentence structure, word choice, and the order of paragraphs and reasoning are preserved; changes forced by grammar are reported separately.
- [ ] Operational grouping/definitions are distinguished from externally validated physical or predictive claims.
- [ ] AI disclosure names tool, purpose, scope, author review, and responsibility without serving as evidence that the method is valid.
- [ ] Editor statements, public reviewer comments, confidential comments, and author/agent inferences remain distinguishable; no source is credited with an AI-use claim it did not make.

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
- [ ] XeLaTeX log has zero `Missing character` lines; Greek letters and symbols the body font lacks (e.g. Sarabun: β λ φ ↔ ⇒ ∈) are written as TeX math (`$\beta$`) rather than pasted Unicode. See `DOCUMENT_PRODUCTION_POLICY.md`.
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
