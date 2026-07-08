# Cross-Project Environment Policy

Use machine-local shared environments for OneDrive projects. Do not keep Python
virtual environments, conda environments, Node dependencies, or large build
caches inside OneDrive project folders.

## Why

OneDrive should sync source files, documents, manifests, and small reproducible
assets. It should not sync installed binary packages. Project-local `.venv`
folders and `node_modules` trees make sync slow, machine-specific, and fragile
across Windows, WSL, and other machines.

## Python Environment Groups

Prefer a small number of shared local environments by work type.

| Group | Use For | Typical Env |
| --- | --- | --- |
| Teaching CV/ML | OpenCV, image processing, classroom demos | `opencv-demo` |
| Research Rain | rainfall data, feature analysis, notebooks, visualization | `rain` |
| Admin/Documents | pandas, openpyxl, plotly, document/report scripts | `admin-docs` or project-specific |
| Web/Viz | web dashboards and visualization tooling | project-specific Node/Python env |
| Heavy DL | PyTorch, TensorFlow, face recognition, GPU-heavy demos | separate heavy env |

Keep these environments under machine-local conda/micromamba locations such as
`~/.local/share/mamba/envs`, not under OneDrive.

## Repository Rules

Each active project should keep enough metadata to rebuild dependencies:

- Python: `requirements.txt`, `environment.yml`, or `pyproject.toml`.
- Node: `package.json` plus a lockfile such as `package-lock.json`.
- Agent guidance: `AGENTS.md` when the project has local rules.

Each active project should ignore local dependency folders:

```gitignore
.venv/
venv/
env/
.conda/
node_modules/
__pycache__/
*.py[cod]
.ipynb_checkpoints/
```

For LaTeX projects, ignore ordinary build intermediates when they are not
deliberate evidence artifacts:

```gitignore
*.aux
*.bbl
*.bcf
*.blg
*.fdb_latexmk
*.fls
*.log
*.out
*.synctex.gz
*.toc
```

## Current Cleanup Decisions

- `Class/Image Processing/.venv` was removed from OneDrive. Use `opencv-demo`.
- `KU/president/.venv` was removed from OneDrive. Recreate from
  `requirements.txt` in a machine-local environment.
- `imh/node_modules` was removed from OneDrive. Recreate with `npm ci`.
- `nowcast/ting67` is excluded from broad cleanup for now. It has provenance,
  revision, archive, and paper-build material that needs project-specific review.

## Restore Commands

OpenCV/image-processing teaching demos:

```bash
micromamba activate opencv-demo
```

KU president/admin document tools:

```bash
cd ~/OneDrive/KU/president
python -m pip install -r requirements.txt
```

Node/Vite apps:

```bash
cd ~/OneDrive/imh
npm ci
```


## Document Build and Cache Rules

For document projects, keep Markdown source, style sheets, templates, bibliography, and small source figures in OneDrive.

Do not put large generated/intermediate files in OneDrive when they are reproducible or machine-specific, such as:

- huge exported figure caches
- OCR scratch images
- PDF render screenshots
- LaTeX/Pandoc/Quarto build intermediates
- downloaded raw data used only to regenerate figures

If a document build requires files outside OneDrive, record them in:

- `.ai/LOCAL_RESOURCES.md`
- `.ai/DOCUMENT_PIPELINE.md`
- `PROJECT_RUNS.md` if the project has an active run/service/machine role

A final PDF may be synced in OneDrive when it is a deliverable, but temporary build caches should remain local.
