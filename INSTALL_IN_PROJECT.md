# INSTALL_IN_PROJECT

This file explains how to attach Agent Project Kit to a new or existing project.

For most users, the README quick start is enough. Use this file when you need
more detail about update behavior and project-local state.

## Recommended Git Install

For a new project:

```bash
mkdir my-project
cd my-project
```

For an existing project, `cd` into that project folder first.

Then run:

```bash
mkdir -p .ai
git clone https://github.com/punpiti/agent-project-kit.git .ai/agent-project-kit-source
bash .ai/agent-project-kit-source/scripts/install-to-project.sh . .ai/agent-project-kit-source
```

Windows PowerShell:

```powershell
New-Item -ItemType Directory -Force -Path "my-project" | Out-Null
Set-Location "my-project"
New-Item -ItemType Directory -Force -Path ".ai" | Out-Null
git clone https://github.com/punpiti/agent-project-kit.git ".ai\agent-project-kit-source"
powershell -ExecutionPolicy Bypass -File ".ai\agent-project-kit-source\scripts\install-to-project.ps1" -ProjectPath . -SourcePath ".ai\agent-project-kit-source"
```

The project will have:

```text
.ai/agent-project-kit-source/ # git clone/source copy of the kit
.ai/agent-project-kit/        # installed snapshot read by agents
.ai/PROJECT_STATE.md         # project-local state, preserved on updates
```

## Local Folder Install

If you already have a local copy of Agent Project Kit:

```bash
bash /path/to/agent-project-kit/scripts/install-to-project.sh /path/to/project /path/to/agent-project-kit
```

PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File "C:\path\to\agent-project-kit\scripts\install-to-project.ps1" -ProjectPath "C:\path\to\project" -SourcePath "C:\path\to\agent-project-kit"
```

## Installed Files

The installer creates or updates:

```text
AGENTS.md
CLAUDE.md
ANTIGRAVITY.md
.ai/agent-project-kit/
```

It creates project-local files only if they do not already exist:

```text
.ai/PROJECT_STATE.md
.ai/PROJECT_HIERARCHY.md
.ai/COMPUTING_ENVIRONMENT_VERSION.md
.ai/MACHINE_PROFILE.md
.ai/LOCAL_RESOURCES.md
.ai/MACHINE_COMPATIBILITY.md
.ai/RUNBOOK.md
.ai/TOKEN_BUDGET.md
.ai/SESSION_LOG.md
.ai/ENVIRONMENT_VARIABLES.md
```

Project-local state is preserved when the package is updated. On first install,
root files such as `AGENTS.md`, `CLAUDE.md`, and `ANTIGRAVITY.md` are created
only if missing; otherwise the installer appends a managed block. If
`.ai/agent-project-kit/` or required metadata files already exist and do not
look like Agent Project Kit files, the installer stops instead of
overwriting them.

## Update An Existing Install

Use [UPDATE_EXISTING_PROJECT.md](UPDATE_EXISTING_PROJECT.md) for the full
preflight, dry-run, apply, verify, and rollback loop.

Preview first:

```bash
bash .ai/agent-project-kit/scripts/install-from-git.sh --dry-run . https://github.com/punpiti/agent-project-kit.git main
```

Then apply:

```bash
bash .ai/agent-project-kit/scripts/install-from-git.sh . https://github.com/punpiti/agent-project-kit.git main
```

For WSL2 projects under a Windows-synced folder, use the WSL-local clone path
shown in the README and pass the same `--dry-run` flag before applying.

## Use With Claude / Antigravity / Other Agents

The installer creates or appends these root adapter files without overwriting
existing user-authored content:

```text
CLAUDE.md
ANTIGRAVITY.md
```

These files point AI clients back to `AGENTS.md`,
`.ai/agent-project-kit/`, and project-local `.ai/` state. Keep canonical
policy in one place instead of maintaining separate rules for each AI client.

## After Install

Tell the agent:

```text
Read AGENTS.md and .ai/agent-project-kit first.
Then inspect .ai/PROJECT_STATE.md, .ai/PROJECT_HIERARCHY.md,
.ai/COMPUTING_ENVIRONMENT_VERSION.md, .ai/MACHINE_PROFILE.md,
.ai/LOCAL_RESOURCES.md, .ai/MACHINE_COMPATIBILITY.md, .ai/RUNBOOK.md,
and .ai/TOKEN_BUDGET.md before starting work.
```

For a new machine or a new storage layout, fill `.ai/MACHINE_PROFILE.md` before
running heavy work. On later sessions, do only the minimal resume check and
reuse the recorded profile unless hostname, platform, path style, or storage
layout changed.

## Token / Cost Control

Set project defaults in `.ai/TOKEN_BUDGET.md`.

For cost-sensitive work:

```text
Default token mode: T1 Standard
Default cost profile: C0 Economy
```

In `C0 Economy`, the agent should ask before broad scans, web research, long
test/debug loops, or large rewrites unless the user explicitly says to proceed.

## Local Resources

If a project uses local data, cache, intermediate files, model checkpoints, or
other resources outside the project folder, record them in:

```text
.ai/LOCAL_RESOURCES.md
.ai/MACHINE_COMPATIBILITY.md
.ai/RUNBOOK.md
```

Do not let agents guess machine-specific paths.

## Git Ignore

For many projects, `.ai/` is local state and should not be committed:

```gitignore
.ai/
```

If the project intentionally shares `.ai/` state across a private team, document
that choice in the project README.
