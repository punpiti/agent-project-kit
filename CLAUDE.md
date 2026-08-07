# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

This **is** Agent Project Kit itself (package name `agent-project-kit`, legacy
folder name `computing-environment`) — a portable starter kit of instruction
files, `.ai/` templates, and installer scripts that other projects install to
give AI coding agents (Claude Code, Codex, Antigravity, etc.) a consistent
starting point. You are working on the kit's source, not a downstream project
that consumes it.

Read `AGENTS.md` first — it defines the Spec-Eval-Loop workflow, the
Conda-family environment routing rules, machine/portability protocol, and
token-discipline modes that govern how work in this repo should be scoped.
Because this project is Agent Project Kit's own source, do **not** treat
`.ai/agent-project-kit/` as a second project to recurse into — it is only an
installed snapshot kept for downstream-install testing (see `START_HERE.md`
"Self-Hosting / Recursion Guard").

## Architecture

The kit has three cooperating layers:

1. **Root-level Markdown instruction files** (`AGENTS.md`, `START_HERE.md`,
   `STARTUP.md`, `CLAUDE.md`, `ANTIGRAVITY.md`, `SPEC_EVAL_LOOP_INSTRUCTION.md`,
   `MACHINE_PROFILES.md`, `TOKEN_DISCIPLINE.md`, policy/checklist docs) — these
   are the canonical source of truth and are what gets copied into a
   downstream project's root by the installer.
2. **`prompts/`** — numbered per-domain prompt packs (`19_SOFTWARE_...md`,
   `13_RESEARCH_...md`, `18_EDUCATIONAL_POLICY_...md`, etc.), routed by
   `prompts/catalog.json`. `STARTUP.md`'s routing table maps a task's primary
   type to exactly one prompt pack to load — agents should not load every pack.
3. **`config/` + `scripts/`** — a v7 structured routing/context layer that is
   the machine-readable counterpart to the Markdown routing table:
   - `scripts/route_task.py` classifies a free-text request into
     `domain`/`deliverable`/`methods` using keyword rules from `config/routes.json`.
   - `scripts/context.py` calls `route_task.classify()` and compiles a compact
     JSON context bundle (routed prompt + project state, capped in size —
     `secondary_modules <= 2`, `bytes <= 12000` in tests) for a target project.
   - `scripts/apk.py` resolves which installed shared-runtime version a bound
     project should use (see below), verifies its content digest against a
     pinned hash, and exposes `resolve`/`context`/`rollback` subcommands.
   - `config/policies.json` / `config/workflows.json` are the declarative
     policy/workflow definitions these scripts read.

`templates/` holds the files an install stamps into a downstream project's
`.ai/` (e.g. `PROJECT_STATE.md`, `MACHINE_PROFILE.md`, `RUNBOOK.md`,
`apk.json`, `project.json`, `state.json`) plus the Thai/A4 Pandoc document
pipeline template (`templates/pandoc-thai-a4/`).

### Installer / shared-runtime model

Two install paths exist, both driven by `scripts/install-to-project.sh` /
`.ps1`:

- **Per-project snapshot install** — copies the kit into the target project's
  `.ai/agent-project-kit/` and appends managed blocks to the project's
  `AGENTS.md`/`CLAUDE.md`/`ANTIGRAVITY.md` (existing content is preserved, not
  overwritten — see the "Safety Model" section of `README.md`).
- **Shared runtime (canary)** — `scripts/install-shared.py` installs one
  immutable, version-pinned copy under `APK_SHARED_ROOT`
  (`.agent-project-kit/versions/<version>/`) shared across several WSL2
  projects, plus machine-local launcher state under `APK_MACHINE_HOME`. Each
  project then gets a small binding file (`.ai/apk.json`) recording which
  pinned version + aggregate SHA-256 digest it resolves to.
  `scripts/apk.py resolve` verifies that digest before use and refuses to run
  against a tampered runtime; `apk.py rollback` disables the binding and falls
  back to the project's preserved per-project snapshot.

`scripts/check-update-notice.py` implements the 14-day, manifest-only update
check described in `AGENTS.md`/`README.md`: it never clones/pulls/installs on
its own, only reports whether a newer version exists.

`scripts/repair_thai_wordbreak_docx.py` is the mandatory post-processing step
for any generated Thai DOCX (see the "Mandatory Thai DOCX gate" in
`AGENTS.md`) — it normalizes Thai font references to `TH Sarabun New` and
fixes word-break behavior; a DOCX is never "done" until this has run.

## Commands

Run tests directly (there is no test-runner wrapper or CI config in-repo):

```bash
# Python unit-style tests (routing + compact context bundle)
python3 tests/test-v7-context.py

# Prompt catalog schema/consistency check
python3 scripts/validate_prompt_catalog.py

# Thai DOCX repair invariants
python3 tests/test-thai-docx-repair.py

# Shell integration tests (each runs installer(s) into a temp dir and asserts on the result)
bash tests/test-fast-start.sh
bash tests/test-shared-runtime.sh
bash tests/test-shared-runtime-v2.sh
```

There's no single "run everything" entry point — run the specific test file
relevant to what changed (e.g. touching `config/routes.json` or
`scripts/route_task.py`/`scripts/context.py` → `test-v7-context.py`; touching
`scripts/install-to-project.sh` or `prompts/` → `test-fast-start.sh`; touching
`scripts/install-shared.py`/`scripts/apk.py` → the `test-shared-runtime*.sh`
files).

Other scripts worth knowing when working in this area:

```bash
# Classify a single request the way STARTUP.md's routing table does
python3 scripts/route_task.py "fix the responsive website login bug"

# Doctor check on an installed project (staleness/placeholder detection)
python3 scripts/apk_doctor.py --project <path>

# Dry-run the GitHub Pages update flow
bash scripts/update-from-pages.sh --dry-run .
```

## Repo-specific conventions

- `.ai/` is gitignored in this repo (it holds this kit's *own* local
  agent-session state, not something to ship) — don't add tracked files there.
- Root Markdown files are copied verbatim into downstream projects by the
  installer; keep changes to them consistent with the append-only /
  preserve-existing-content safety model described in `README.md`.
- `environments/*.yml` are the canonical Conda-family environment manifests
  (`text`, `image`, `ml`); `*-observed-YYYYMMDD.yml` files are audit snapshots
  only — never install or promote packages from them without review (see
  `AGENTS.md` Conda-Family Environment Routing).
- Version string lives in `manifest.json` (`version`) and is referenced by
  path in the shared-runtime tests (`RUNTIME="$HOME_DIR/versions/<version>"`)
  — bumping it requires updating both together.
