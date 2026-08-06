# Agent Project Kit

[ภาษาไทย](README.th.md)

Agent Project Kit is a small starter kit for using AI coding agents inside a
project folder.

It installs a few instruction files and `.ai/` templates so tools such as
Codex, Claude Code, Antigravity, or similar agents have a clear place to start.
It is intentionally small: your application code stays yours, project-local
notes stay under `.ai/`, and the managed kit snapshot can be refreshed later.

Current release: `7.2-shared-runtime-v2-canary`

Use it when you want a project to keep simple notes about:

- what the project is
- how an AI agent should start work
- whether the current machine is suitable for the task
- how much local parallelism is reasonable for CPU, GPU, memory, and storage
- where project-local AI notes should live
- which prompt packs, local resources, and project constraints are specific to
  this project

It helps an AI assistant resume a real project without starting from scratch:
what happened last time, which machine and local resources matter, which parent
or child context applies, and what should happen next by priority or deadline.
For research projects, it also includes prompt templates for literature review,
source checking, counter-arguments, data interpretation, and research briefs.

The old package/path name was `computing-environment`. New installs use
`.ai/agent-project-kit/` as the installed snapshot path; old projects with
`.ai/computing-environment/` can still be migrated.

## Current Paths

```text
.ai/agent-project-kit/        # managed installed snapshot, refreshed by updates
.ai/agent-project-kit-source/ # optional git clone/source copy for new installs
.ai/PROJECT_STATE.md          # project-local state, preserved on updates
```

Do not put project-specific notes or custom prompt packs inside
`.ai/agent-project-kit/`. That directory is kit-owned and may be replaced during
an update. Put project-owned prompts under `.ai/prompts/`, `.ai/prompt-packs/`,
or another path documented in `.ai/PROJECT_STATE.md` or `.ai/RUNBOOK.md`.

## Why Install It?

Without a small project setup, every AI session often starts with the same basic
questions: what is this project, which files matter, and how should the agent
begin?

Agent Project Kit gives the agent a consistent starting point. It does not
change your application code. It only adds project instructions, starter notes,
and installer scripts.

For a one-time small task, you may not need it. For a project you will open
again with an AI assistant, it can make the next session easier.

## Quick Start

For a new project folder:

```bash
mkdir my-project
cd my-project
```

For an existing project, `cd` into that project folder first.

### macOS / Linux

```bash
mkdir -p .ai
git clone https://github.com/punpiti/agent-project-kit.git .ai/agent-project-kit-source
bash .ai/agent-project-kit-source/scripts/install-to-project.sh . .ai/agent-project-kit-source
code .
```

### WSL2 With A Windows-Synced Project Folder

If the project lives under a Windows-mounted folder such as OneDrive, keep the
Git clone in WSL-local cache and install only the project snapshot into `.ai/`.
This avoids Windows permission/sync issues with `.git/config`.

```bash
KIT="${XDG_CACHE_HOME:-$HOME/.cache}/agent-project-kit"
if [ -d "$KIT/.git" ]; then
  git -C "$KIT" pull --ff-only
else
  git clone https://github.com/punpiti/agent-project-kit.git "$KIT"
fi
bash "$KIT/scripts/install-to-project.sh" . "$KIT"
code .
```

If `code .` is not available, open the folder manually in VS Code, Claude Code,
Antigravity, or another coding agent.

### Windows PowerShell

```powershell
New-Item -ItemType Directory -Force -Path "my-project" | Out-Null
Set-Location "my-project"
New-Item -ItemType Directory -Force -Path ".ai" | Out-Null
git clone https://github.com/punpiti/agent-project-kit.git ".ai\agent-project-kit-source"
powershell -ExecutionPolicy Bypass -File ".ai\agent-project-kit-source\scripts\install-to-project.ps1" -ProjectPath . -SourcePath ".ai\agent-project-kit-source"
code .
```

PowerShell 7 also works:

```powershell
pwsh -ExecutionPolicy Bypass -File ".ai\agent-project-kit-source\scripts\install-to-project.ps1" -ProjectPath . -SourcePath ".ai\agent-project-kit-source"
```

## What Gets Installed

After install, the project root has files like:

```text
AGENTS.md
CLAUDE.md
ANTIGRAVITY.md
.ai/agent-project-kit/
.ai/PROJECT_STATE.md
.ai/MACHINE_PROFILE.md
.ai/LOCAL_RESOURCES.md
.ai/RUNBOOK.md
.ai/TOKEN_BUDGET.md
.ai/SESSION_LOG.md
```

The root files tell AI clients where to start. Project-specific notes stay under
`.ai/`.

## Safety Model

The installer refreshes the package snapshot but does not overwrite existing
project notes such as `.ai/PROJECT_STATE.md`, `.ai/MACHINE_PROFILE.md`, or
`.ai/LOCAL_RESOURCES.md`. If a first install finds an existing
`.ai/agent-project-kit/` directory or metadata file with the same name that
does not look like Agent Project Kit, it stops instead of overwriting the user
file. Existing `AGENTS.md`,
`CLAUDE.md`, and `ANTIGRAVITY.md` files are appended to, not replaced.

The source clone and installed snapshot use different paths so `git clone`
cannot accidentally become the same directory that the installer refreshes.

## Prompt Packs

Kit prompts live in:

```text
.ai/agent-project-kit/prompts/
```

Project-specific prompt packs should live outside the managed snapshot, for
example:

```text
.ai/prompts/
.ai/prompt-packs/
.ai/custom-prompts/
```

Tell future agents where those project prompt packs are by documenting them in
`.ai/PROJECT_STATE.md` or `.ai/RUNBOOK.md`.

For research projects, see:

```text
.ai/agent-project-kit/prompts/13_RESEARCH_PROJECT_PROMPTS.md
```

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for package changes.

## First Prompt For An Agent

After installing and opening the folder, tell the agent:

```text
Read AGENTS.md and .ai/agent-project-kit first.
Then read the project notes under .ai/.
Summarize what this project appears to be, what machine this is, and what you
need before starting the task.
Report the installed Agent Project Kit version from
.ai/COMPUTING_ENVIRONMENT_VERSION.md.
If this project sits inside a parent project that was already scanned, reuse
the parent summary and machine profile instead of rescanning broadly. Treat the
parent as broad context only; the child project must keep the sharper
task-specific state in its own .ai/ notes.
If the project has statuses or deadlines, start with what happened last time and
the next actions ordered by priority and due date.
If a task could benefit from parallel execution, first decide whether this
machine is suitable: check available CPU cores, GPU/accelerator type, memory,
storage pressure, and any project resource limits, then choose a conservative
parallelism level and report it before running heavy parallel work.
If the kit has not been checked for updates recently, say so before doing
package-level work.
```

## Update An Existing Project

For a full update checklist, see
[UPDATE_EXISTING_PROJECT.md](UPDATE_EXISTING_PROJECT.md).

The short version is: read the current version, check the GitHub Pages manifest
with a dry run, then apply the update. Existing project-local `.ai/` state is
preserved; package concepts are refreshed under `.ai/agent-project-kit/`.

Normal agent startup uses a persisted 14-day manifest-only check. It reports
when a newer version is available but never clones, pulls, or installs by
itself. Repeated startups within the 14-day window do not contact the network.

Dry run:

```bash
bash .ai/agent-project-kit/scripts/update-from-pages.sh --dry-run .
```

macOS / Linux:

```bash
bash .ai/agent-project-kit/scripts/update-from-pages.sh .
```

WSL2 with a Windows-synced project folder:

```bash
KIT="${XDG_CACHE_HOME:-$HOME/.cache}/agent-project-kit"
bash "$KIT/scripts/update-from-pages.sh" --dry-run .
bash "$KIT/scripts/update-from-pages.sh" .
```

Windows PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File ".ai\agent-project-kit\scripts\update-from-pages.ps1" -ProjectPath . -DryRun
powershell -ExecutionPolicy Bypass -File ".ai\agent-project-kit\scripts\update-from-pages.ps1" -ProjectPath .
```

## Repository Notes

This repository intentionally ignores `.ai/` because that directory contains
local project state and installed snapshots.
