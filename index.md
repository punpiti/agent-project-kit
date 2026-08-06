---
title: Agent Project Kit
---

# Agent Project Kit

Agent Project Kit is a portable starter kit for projects that are worked on
with AI coding agents. It gives Codex, Claude Code, Antigravity, and similar
tools a consistent way to start: read project state, understand the current
machine, preserve local notes, and update the kit without overwriting the
user's work.

[ภาษาไทย](README.th.md) | [GitHub repository](https://github.com/punpiti/agent-project-kit) | [Manifest](manifest.json)

## Current Release

- Package name: `agent-project-kit`
- Current package version: `7.2.2-shared-runtime-v2-canary`
- Installed snapshot path: `.ai/agent-project-kit/`
- Source clone path for new installs: `.ai/agent-project-kit-source/`
- Legacy path: `.ai/computing-environment/` is migration-only

## Install

macOS / Linux:

```bash
mkdir -p .ai
git clone https://github.com/punpiti/agent-project-kit.git .ai/agent-project-kit-source
bash .ai/agent-project-kit-source/scripts/install-to-project.sh . .ai/agent-project-kit-source
```

WSL2 with a Windows-synced project folder:

```bash
KIT="${XDG_CACHE_HOME:-$HOME/.cache}/agent-project-kit"
if [ -d "$KIT/.git" ]; then
  git -C "$KIT" pull --ff-only
else
  git clone https://github.com/punpiti/agent-project-kit.git "$KIT"
fi
bash "$KIT/scripts/install-to-project.sh" . "$KIT"
```

Windows PowerShell:

```powershell
New-Item -ItemType Directory -Force -Path ".ai" | Out-Null
git clone https://github.com/punpiti/agent-project-kit.git ".ai\agent-project-kit-source"
powershell -ExecutionPolicy Bypass -File ".ai\agent-project-kit-source\scripts\install-to-project.ps1" -ProjectPath . -SourcePath ".ai\agent-project-kit-source"
```

## What It Adds

- Root agent adapter files: `AGENTS.md`, `CLAUDE.md`, and `ANTIGRAVITY.md`
- Managed kit snapshot: `.ai/agent-project-kit/`
- Project-local state files: `.ai/PROJECT_STATE.md`, `.ai/MACHINE_PROFILE.md`,
  `.ai/LOCAL_RESOURCES.md`, `.ai/RUNBOOK.md`, `.ai/TOKEN_BUDGET.md`, and
  related templates
- Prompt packs for coding, project resume, machine-aware work, document
  production, markdown cleanup, and research projects
- Update scripts that check the GitHub Pages manifest before refreshing the
  local snapshot

## Safety Model

The installer is designed to preserve user work.

- It refreshes only the managed package snapshot under `.ai/agent-project-kit/`.
- It creates project-local `.ai/` state files only when they are missing.
- It appends managed blocks to existing root agent files instead of replacing
  them.
- If a first install finds a same-name directory or metadata file that does not
  look like Agent Project Kit content, it stops instead of overwriting or moving
  the user's file.
- The source clone and installed snapshot use different paths so a git clone
  does not collide with the managed snapshot.

## Project Prompt Packs

Kit prompts live in:

```text
.ai/agent-project-kit/prompts/
```

Project-specific or user prompt packs should live outside the managed snapshot,
for example:

```text
.ai/prompts/
.ai/prompt-packs/
.ai/custom-prompts/
```

Agents should treat `.ai/agent-project-kit/` as kit-owned and refreshable.
Project-owned prompts should be documented in `.ai/PROJECT_STATE.md` or
`.ai/RUNBOOK.md` so future sessions can find them without putting custom files
inside the managed snapshot.

## Update

Preview the GitHub Pages manifest first:

```bash
bash .ai/agent-project-kit/scripts/update-from-pages.sh --dry-run .
```

Apply the update:

```bash
bash .ai/agent-project-kit/scripts/update-from-pages.sh .
```

The update path reports current and upstream package/schema versions, then
refreshes the managed snapshot only when the GitHub Pages manifest shows a
newer or different package version.

## Start An Agent

After installing, open the project folder and tell the agent:

```text
Read AGENTS.md and .ai/agent-project-kit first.
Then read .ai/PROJECT_STATE.md, .ai/PROJECT_HIERARCHY.md,
.ai/COMPUTING_ENVIRONMENT_VERSION.md, .ai/MACHINE_PROFILE.md,
.ai/LOCAL_RESOURCES.md, .ai/RUNBOOK.md, and .ai/TOKEN_BUDGET.md.
Report the installed Agent Project Kit version before starting work.
```

## More Docs

- [README](README.md)
- [Thai README](README.th.md)
- [Install details](INSTALL_IN_PROJECT.md)
- [Update existing project](UPDATE_EXISTING_PROJECT.md)
- [Git distribution](GIT_DISTRIBUTION.md)
- [Changelog](CHANGELOG.md)
