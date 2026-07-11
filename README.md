# Agent Project Kit

[ภาษาไทย](README.th.md)

Agent Project Kit is a small starter kit for using AI coding agents inside a
project folder.

It installs a few instruction files and `.ai/` templates so tools such as
Codex, Claude Code, Antigravity, or similar agents have a clear place to start.

Use it when you want a project to keep simple notes about:

- what the project is
- how an AI agent should start work
- whether the current machine is suitable for the task
- where project-local AI notes should live

It helps an AI assistant resume a real project without starting from scratch:
what happened last time, which machine and local resources matter, which parent
or child context applies, and what should happen next by priority or deadline.

The old package name was `computing-environment`. Installed projects still use
`.ai/computing-environment/` as the compatibility snapshot path.

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

### macOS / Linux / WSL2

```bash
mkdir -p .ai
git clone https://github.com/punpiti/agent-project-kit.git .ai/agent-project-kit
bash .ai/agent-project-kit/scripts/install-to-project.sh . .ai/agent-project-kit
code .
```

If `code .` is not available, open the folder manually in VS Code, Claude Code,
Antigravity, or another coding agent.

### Windows PowerShell

```powershell
New-Item -ItemType Directory -Force -Path "my-project" | Out-Null
Set-Location "my-project"
New-Item -ItemType Directory -Force -Path ".ai" | Out-Null
git clone https://github.com/punpiti/agent-project-kit.git ".ai\agent-project-kit"
powershell -ExecutionPolicy Bypass -File ".ai\agent-project-kit\scripts\install-to-project.ps1" -ProjectPath . -SourcePath ".ai\agent-project-kit"
code .
```

PowerShell 7 also works:

```powershell
pwsh -ExecutionPolicy Bypass -File ".ai\agent-project-kit\scripts\install-to-project.ps1" -ProjectPath . -SourcePath ".ai\agent-project-kit"
```

## What Gets Installed

After install, the project root has files like:

```text
AGENTS.md
CLAUDE.md
ANTIGRAVITY.md
.ai/computing-environment/
.ai/PROJECT_STATE.md
.ai/MACHINE_PROFILE.md
.ai/LOCAL_RESOURCES.md
.ai/RUNBOOK.md
.ai/TOKEN_BUDGET.md
.ai/SESSION_LOG.md
```

The root files tell AI clients where to start. Project-specific notes stay under
`.ai/`.

The installer refreshes the package snapshot but does not overwrite existing
project notes such as `.ai/PROJECT_STATE.md`, `.ai/MACHINE_PROFILE.md`, or
`.ai/LOCAL_RESOURCES.md`.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for package changes.

## First Prompt For An Agent

After installing and opening the folder, tell the agent:

```text
Read AGENTS.md and .ai/computing-environment first.
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
If the kit has not been checked for updates recently, say so before doing
package-level work.
```

## Update

Update the cloned kit and reinstall the snapshot.

macOS / Linux / WSL2:

```bash
git -C .ai/agent-project-kit pull --ff-only
bash .ai/agent-project-kit/scripts/install-to-project.sh . .ai/agent-project-kit
```

Windows PowerShell:

```powershell
git -C ".ai\agent-project-kit" pull --ff-only
powershell -ExecutionPolicy Bypass -File ".ai\agent-project-kit\scripts\install-to-project.ps1" -ProjectPath . -SourcePath ".ai\agent-project-kit"
```

## Repository Notes

This repository intentionally ignores `.ai/` because that directory contains
local project state and installed snapshots.
