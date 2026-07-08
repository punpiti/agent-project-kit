# Cross-Project Environment Policy

Use machine-local environments and caches for projects that live in Git
repositories, shared drives, or synced folders.

Do not keep Python virtual environments, conda environments, Node dependencies,
large build caches, or generated intermediates inside shared/synced project
folders unless there is a specific reason to do so.

## Why

Shared/synced storage and Git repositories should carry source files,
documents, manifests, small fixtures, and intentionally shared project state.
They should not carry installed binary packages or high-churn generated files.

Project-local `.venv` folders, conda environments, `node_modules` trees, build
caches, and exported intermediates make sync slow, machine-specific, and fragile
across Windows, WSL, macOS, Linux, and remote machines.

## Environment Strategy

Each project should keep enough metadata to rebuild dependencies:

- Python: `requirements.txt`, `environment.yml`, `pyproject.toml`, or similar
- Node: `package.json` plus a lockfile such as `package-lock.json` or `pnpm-lock.yaml`
- System tools: a short runbook or setup note
- Agent guidance: `AGENTS.md` and `.ai/RUNBOOK.md` when relevant

Use machine-local locations for installed dependencies and caches:

```text
~/.local/share/mamba/envs/<env>
~/.cache/<project>
/var/tmp/<project>
/mnt/data/<project>
C:\Users\<user>\AppData\Local\<project>
```

The exact paths are project and machine specific. Record them in
`.ai/LOCAL_RESOURCES.md` and use environment variables instead of hardcoding
absolute paths in source code.

## Ignore Local Dependency Folders

Most projects should ignore local dependency folders:

```gitignore
.venv/
venv/
env/
.conda/
node_modules/
__pycache__/
*.py[cod]
.ipynb_checkpoints/
.pytest_cache/
.mypy_cache/
.ruff_cache/
```

For LaTeX, Pandoc, Quarto, or report projects, ignore ordinary build
intermediates unless they are deliberate evidence artifacts:

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
_freeze/
_site/
```

## Cleanup Guidance

If a project already has large local dependency folders or generated caches in
the project tree, do not delete them blindly. First check whether they are
reproducible and whether the project has enough metadata to rebuild them.

Typical move/delete candidates:

- `.venv/`, `venv/`, `.conda/`
- `node_modules/`
- `__pycache__/`, `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`
- LaTeX/Pandoc/Quarto build intermediates
- generated figure caches and temporary export folders

Keep final deliverables and small reproducible fixtures in the project when
they are meant to be shared.

## Document Build And Cache Rules

For document projects, keep Markdown source, style sheets, templates,
bibliography, and small source figures in the project folder or shared/synced
source tree.

Do not put large generated/intermediate files in shared/synced storage when
they are reproducible or machine-specific, such as:

- huge exported figure caches
- OCR scratch images
- PDF render screenshots
- LaTeX/Pandoc/Quarto build intermediates
- downloaded raw data used only to regenerate figures

If a document build requires files outside the project/shared source tree,
record them in:

- `.ai/LOCAL_RESOURCES.md`
- `.ai/DOCUMENT_PIPELINE.md`
- `.ai/SESSION_LOG.md` or a project-specific private run log if the project has an active run/service/machine role

A final PDF may be committed or synced when it is a deliverable, but temporary
build caches should remain local.
