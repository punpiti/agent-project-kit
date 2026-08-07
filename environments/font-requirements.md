# Thai Font Requirements for `text`

Fonts are machine-level resources used by the shared `text` environment and its
document toolchain; they are not Conda packages and should not be copied into a
per-project virtual environment.

## Required Families and Routing

| Output/toolchain | Preferred Thai font |
|---|---|
| Microsoft Word / DOCX | `TH Sarabun New` |
| LaTeX / XeLaTeX / LuaLaTeX | Google Fonts `Sarabun` |

Before building a document, verify the required family and weights with
`fc-list` or the platform's font manager. Install/download a missing family only
when the current task needs that output. Follow the environment network policy:
warn the user before downloading and obtain approval first on a metered network.

Do not silently substitute `TH SarabunPSK` for `TH Sarabun New`, or another font
for Google Sarabun, when layout fidelity matters. If the preferred font cannot
be installed, report the fallback and expect page flow and line breaks to change.

## Installer

Use the packaged helper after reviewing network conditions:

```bash
# Check current availability; no download is allowed by default.
python scripts/install-thai-fonts.py --font all

# Download Google Sarabun from the pinned Google Fonts revision.
python scripts/install-thai-fonts.py --font sarabun --allow-download

# Install legally obtained TH Sarabun New files without bundling them here.
python scripts/install-thai-fonts.py --font th-sarabun-new \
  --th-sarabun-source /path/to/font-files
```

Google Sarabun is fetched from the Google Fonts repository at an immutable
revision and retains its SIL Open Font License file. TH Sarabun New is not
bundled or automatically downloaded because the package does not yet record a
stable authoritative download URL and redistribution terms for that exact
family. On WSL2, Windows-installed TH Sarabun New may already be visible through
fontconfig and require no copy.

## Observed on `madlab-i9`

Checked on 2026-08-07:

- `TH Sarabun New`: available through Windows fonts visible to WSL2, including
  regular, bold, italic, and bold italic.
- Google Fonts `Sarabun`: available in the Linux user font directory with the
  regular, italic, thin, extra-light, light, medium, semi-bold, bold, and
  extra-bold families/weights observed.

These paths are machine-specific. Recheck availability on every new machine;
do not hardcode the observed paths in document source.
