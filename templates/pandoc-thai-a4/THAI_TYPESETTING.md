# Thai Typesetting: Fonts, Glyphs, and Math

Rules for Thai books, papers, and reports that mix Thai text, Latin terms,
Greek symbols, and equations. Font installation and the per-toolchain font
choice are in `environments/font-requirements.md`; the symbol gate is in
`DOCUMENT_PRODUCTION_POLICY.md` (Symbols, Greek letters and math). This file
collects what has gone wrong in practice and how to prevent it.

Status labels: **verified** = reproduced with a build; **observed** = seen in a
real project, not re-tested here; **check** = not yet verified, test before
relying on it.

## Font coverage

- Sarabun (Google Fonts, for XeLaTeX/LuaLaTeX) lacks most Greek letters (it
  has only μ π Δ Ω) and lacks ↔ ⇒ ⇔ ∈ ≡. XeLaTeX logs `Missing character` and
  drops them without failing. **verified**
- Latin display fonts such as Inter have no Thai glyphs. Any element that may
  carry Thai — headings, TOC, running heads, captions, table headers — must stay
  on the Thai font; use a Latin font only for content known to be pure
  Latin/digits. **observed** (fluid-mechanics book)
- A glyph that renders in an editor or a matplotlib figure may still be absent
  from the PDF body font. Check the body font's cmap:
  `python -c "from fontTools.ttLib import TTFont; print(0x03B2 in TTFont('Sarabun-Regular.ttf').getBestCmap())"`.
- Sarabun renders the superscript/subscript digits `²` and `₂` in the kit's
  Thai A4 template. **verified** Prefer Pandoc `m^2^` / `H~2~O` or TeX math
  anyway, so units look the same everywhere.

## Math

- Write every symbol and equation as TeX math in Markdown (`$\beta$`,
  `$\tau = \mu \frac{du}{dy}$`), never as pasted Unicode Greek or arrows.
- Pandoc's XeLaTeX template loads `unicode-math`; with no `mathfont` set, math
  uses Latin Modern Math, which differs in look from Sarabun digits. A book
  should choose its math font explicitly (the fluid-mechanics book uses
  `\setmathfont{Latin Modern Math}`) and record it in its profile.
- Thai inside math goes in `\text{...}`, which uses the Thai text font:
  `$\text{ความเร็ว} = 5$` renders correctly. **verified** Bare Thai inside math
  mode would use the math font, which has no Thai.
- Keep `newunicodechar` math fallbacks (`templates/pandoc-thai-a4/thai-a4-header.tex`
  or the project header) as a safety net only.
- Keep one symbol table for the whole book (for example `VARIABLES.md`) and
  take symbols, units, and dimensions from it, so a symbol never changes form
  between chapters.

## Line breaking

- XeTeX breaks Thai with ICU word segmentation:
  `\XeTeXlinebreaklocale "th"` plus small `\XeTeXlinebreakskip` glue, as in the
  kit header.
- With polyglossia (`\setmainlanguage{thai}`), XeTeX marked mid-word Thai
  breaks with a hyphen (`ความ-` / `เค้น`), which reads as a typo. Setting
  `\defaulthyphenchar=-1` before any font loads removes the mark and keeps the
  breaks. **observed** (fluid-mechanics book) The kit's Thai A4 template, which
  does not use polyglossia, showed no hyphens at Thai line ends in a 40-line
  test. **verified**
- Under polyglossia with Thai as the main language, `\ttfamily` and `\sffamily`
  can abort for lack of Thai script coverage; give them Thai-capable
  fallbacks (`\newfontfamily\thaifonttt{Sarabun}`,
  `\newfontfamily\thaifontsf{...}`). **observed**

## Word / DOCX

- Body text uses `TH Sarabun New`, and every generated Thai DOCX must pass
  `scripts/repair_thai_wordbreak_docx.py` (the Thai DOCX gate in `AGENTS.md`).
- Equations exported to DOCX become Word equations, which use Word's math font
  rather than TH Sarabun New. **check** how Thai text inside equations and
  Greek symbols render in the target Word version before delivery.

## Figures

- Set the figure font explicitly (Sarabun or TH Sarabun New) in matplotlib or
  the drawing tool; a default Latin font drops Thai labels to boxes.
- Use TeX-style math in figure labels when the tool supports it, so symbols
  match the text.

## Build QA (every build)

1. `grep -ci "Missing character" <build>.log` must be 0.
2. `pdffonts <file>.pdf`: every font is embedded, and no unexpected fallback
   family appears.
3. Spot-check the page with the densest math and the page with the longest
   Thai paragraph by eye; `pdftotext` cannot show a missing glyph that was
   replaced by a box.
4. Record the font, size, leading, and math-font decisions in the project's
   `.ai/DOCUMENT_STYLE.md` or book profile, not here.
