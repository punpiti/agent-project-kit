# Shared Environment Requirements

These manifests capture the shared environments observed on `madlab-i9` on
2026-08-07. They are requirements for rebuilding shared Conda-family
environments, not instructions to create a `venv` inside each project.

## Environment Roles

| Manifest | Role |
|---|---|
| `text.yml` | Document processing/generation, text extraction, data/text utilities |
| `image.yml` | OpenCV, image/video processing, Tesseract, and OCR |
| `ml.yml` | Portable, non-CUDA baseline for machine learning |
| `ml-cuda118.yml` | Optional snapshot of the currently installed CUDA 11.8 PyTorch stack |
| `text-observed-20260807.yml` | Uncurated audit snapshot of the current `text` environment |
| `image-observed-20260807.yml` | Uncurated audit snapshot of the current `image` environment |

Choose the first available manager in this order: `micromamba`, `mamba`,
`microconda`, then `conda`. For example:

```bash
micromamba env create -f environments/text.yml
micromamba env create -f environments/image.yml
micromamba env create -f environments/ml.yml
```

Do not install `ml-cuda118.yml` by default. Use it only after confirming that
the target machine has a usable NVIDIA GPU, a working driver, and compatibility
with the recorded CUDA 11.8/PyTorch stack. If GPU availability or compatibility
is uncertain, use `ml.yml` and keep the environment non-CUDA.

Use `env update` rather than `env create` when an environment already exists.
Do not automatically add `--prune`; removing packages is a destructive change
and requires an explicit review of the current environment.

Do not create or update these environments until a task needs them. Before
running a solve or installation, warn the user that the download may be large.
On a metered network, estimate the download size when possible and obtain
approval before downloading; ML/CUDA and image/video stacks are likely to be
the largest.

## How These Files Were Captured

The dated observed YAML files were generated from the current environments with:

```bash
micromamba env export -n <name> --from-history
```

The undated `text.yml`, `image.yml`, and `ml.yml` files are curated common
baselines. They intentionally omit task-specific applications, notebooks,
finance packages, Transformers, CUDA, and transitive pins. Dated observed files
preserve audit evidence but are not default installation inputs.

## Important Audit Findings

- The observed `text` environment includes finance, dashboards, plotting,
  Google API, and Transformers packages plus many pip-pinned transitive
  dependencies. Severity: medium for rebuild size and dependency conflicts;
  these remain only in `text-observed-20260807.yml`.
- The observed `image` history includes JupyterLab, IPython, and ipywidgets.
  Severity: low-to-medium for download and disk size; they are omitted from the
  default image-processing/OCR baseline.
- `lxml` and `python-docx` are explicit common `text` requirements because the
  mandatory Thai DOCX repair/build workflow needs them. The live `text`
  environment observed on 2026-08-07 did not contain `lxml`; update it only
  when DOCX work is needed and after the normal network-cost check.
- The observed `ml` environment uses Python 3.10 and PyTorch 2.5.1 CUDA 11.8
  wheels; that snapshot is preserved as `ml-cuda118.yml`. Rebuilding it requires
  a compatible NVIDIA GPU, driver, platform, and wheel source.
- Pandoc, TeX Live/XeLaTeX, Latexmk, and Poppler are currently supplied by the
  WSL system, not by the `text` Conda environment. See
  `system-document-tools.txt`; installing `text.yml` alone does not install
  those system tools.
- Thai fonts are also machine-level requirements. Use `TH Sarabun New` for
  Microsoft Word/DOCX and Google Fonts `Sarabun` for LaTeX; see
  `font-requirements.md` and `scripts/install-thai-fonts.py` for the availability,
  licensing, and download gates.

## Refresh Procedure

Before refreshing a manifest, inspect the environment and confirm that newly
installed packages are intentional. Export into a dated `*-observed-YYYYMMDD.yml`
file, remove the machine-specific `prefix:` line, and do not copy the snapshot
into a common baseline automatically. Promote only stable, role-appropriate,
direct requirements after review, validate the YAML, and record the decision in
`.ai/SESSION_LOG.md`.
