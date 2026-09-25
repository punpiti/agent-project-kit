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

Prefer the shared Conda-family environments `text`, `image`, and `ml`. Select
the first available manager in this order: `micromamba`, `mamba`,
then `conda`. Do not create a per-project `venv` or `.venv` when these shared
environments cover the task; duplicated environments consume unnecessary disk.
Honor a project that explicitly requires an isolated or tightly pinned runtime,
but place that environment in machine-local storage outside a synced project
tree when practical. Do not mutate a shared environment when doing so would
create cross-project version conflicts.

The package's current rebuild requirements are stored under `environments/`:

- `text.yml`: document processing and generation, including text/PDF tools;
- `image.yml`: OpenCV, image/video processing, Tesseract, and OCR;
- `ml.yml`: portable non-CUDA machine-learning baseline;
- `ml-cuda118.yml`: optional GPU-specific snapshot, used only after compatible
  NVIDIA GPU and driver verification;
- `system-document-tools.txt`: document tools currently supplied by the OS
  rather than the `text` Conda environment.
- `font-requirements.md`: machine-level Thai font requirements for Word and
  LaTeX document production.

Undated environment manifests are curated common baselines. Dated
`*-observed-YYYYMMDD.yml` files are audit snapshots only and must not be used as
default installation inputs. Do not promote task-specific applications,
notebook stacks, CUDA packages, or transitive pip pins into a common baseline
without a separate role-level justification.

CUDA and other GPU runtimes must never be installed merely because an ML task
was requested. First verify that the current machine has a usable target GPU,
working driver, and a compatible framework/runtime combination. When the check
cannot be completed or no compatible GPU exists, use the non-CUDA `ml.yml`.

## Demand-Driven Installation and Network Cost

Do not create, solve, update, or preload an environment merely because its
manifest exists or a session has started. First confirm that the current task
needs that environment and check whether the required tools are already
available. A missing task-required library is a repair trigger, not a reason to
create a project-local virtual environment or abandon the task.

Use this remediation order:

1. Honor a shared environment named by the project runbook or dependency
   manifest. Otherwise select `text`, `image`, or `ml` by the work type.
2. Reproduce the missing import or command inside that environment.
3. Install the smallest compatible direct dependency there, preferring Conda
   and falling back to pip inside the same environment only when necessary.
4. If a standard environment itself is absent, create it from its undated
   manifest, without `--prune`, then add the task-required direct dependency.
5. Verify the import/command and focused task check after installation. Record
   the environment, package, reason, and verification when the change is
   meaningful; do not promote task-specific packages to the baseline silently.

For ordinary scoped repairs, announce the selected environment and package,
then proceed when the estimated download is at most 250 MB and the transaction
does not remove, replace, or downgrade existing packages. Ask for explicit
approval when the estimate exceeds 250 MB, the connection may be metered,
GPU/CUDA or root/admin operations are involved, or the transaction is uncertain
or may remove, replace, or downgrade packages. Use the manager's supported
dry-run mode first for uncertain or high-impact transactions and inspect the
proposed plan before asking for approval.

ML/CUDA stacks, OpenCV/video packages, OCR, LaTeX, and document toolchains can
be especially large. If the connection may be metered, estimate the download
size when practical and obtain explicit user approval before starting the
download. If approval is unavailable, use an existing environment, a smaller
smoke path, or report the missing dependency.

## First-Install Privilege Gate

On the first Agent Project Kit installation on a project/machine, check for an
environment manager in priority order: `micromamba`, `mamba`, then
`conda`, and record the result in `.ai/INSTALLATION_INFO.md`.

If no manager exists and the preferred manager can be installed user-locally
without root/admin privileges, defer its installation until a task actually
needs one of the shared environments. If a declared prerequisite genuinely
requires root/admin privileges, handle it during the explicit first-install
bootstrap rather than invoking privilege escalation unexpectedly in a later
task. Before that privileged installation, tell the user what will be installed,
why it needs elevated privileges, and the expected network cost; obtain approval
before continuing. Never run `sudo` or an administrator install silently.

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
