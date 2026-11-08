# Open With Agent

Goal: clone Agent Project Kit into a project, open the folder in VS Code,
Claude Code, Antigravity, or another coding agent, and let the agent continue
from project-local `.ai/` state.

## New Project

Create and enter the project folder first:

```bash
mkdir my-project
cd my-project
KIT="${APK_GIT_ROOT:-${XDG_CACHE_HOME:-$HOME/.cache}/agent-project-kit}"
git clone https://github.com/punpiti/agent-project-kit.git "$KIT"
bash "$KIT/scripts/install-to-project.sh" . "$KIT"
code .
```

Windows PowerShell:

```powershell
New-Item -ItemType Directory -Force -Path "my-project" | Out-Null
Set-Location "my-project"
$kit = if ($env:APK_GIT_ROOT) { $env:APK_GIT_ROOT } else { Join-Path $env:LOCALAPPDATA "agent-project-kit" }
git clone https://github.com/punpiti/agent-project-kit.git $kit
powershell -ExecutionPolicy Bypass -File (Join-Path $kit "scripts\install-to-project.ps1") -ProjectPath . -SourcePath $kit
code .
```

## Existing Project

From the existing project root:

```bash
KIT="${APK_GIT_ROOT:-${XDG_CACHE_HOME:-$HOME/.cache}/agent-project-kit}"
git clone https://github.com/punpiti/agent-project-kit.git "$KIT"
bash "$KIT/scripts/install-to-project.sh" . "$KIT"
```

Then open the project folder:

```bash
code .
```

After install, the project root has:

```text
AGENTS.md
CLAUDE.md
ANTIGRAVITY.md
.ai/agent-project-kit/
.ai/PROJECT_STATE.md
.ai/TOKEN_BUDGET.md
```

VS Code/Codex, Claude Code, Antigravity, and similar agents should start from
the root adapter files, then read `.ai/` state.

## Existing Project On Windows PowerShell

From the project root:

```powershell
$kit = if ($env:APK_GIT_ROOT) { $env:APK_GIT_ROOT } else { Join-Path $env:LOCALAPPDATA "agent-project-kit" }
git clone https://github.com/punpiti/agent-project-kit.git $kit
powershell -ExecutionPolicy Bypass -File (Join-Path $kit "scripts\install-to-project.ps1") -ProjectPath . -SourcePath $kit
code .
```

## If The Agent Is Already Open

Tell the agent:

```text
If this project has `.ai/agent-project-kit/` but does not yet have root
`AGENTS.md`, `CLAUDE.md`, `ANTIGRAVITY.md`, and `.ai/agent-project-kit/`,
run the Agent Project Kit installer from `$APK_GIT_ROOT/scripts/` (or its
platform-local default) or run the updater from `.ai/agent-project-kit/scripts/`.
Then read `AGENTS.md`, `.ai/agent-project-kit/`, and project-local `.ai/`
state before working.
```

## Update Later

```bash
(
set -e
KIT="${APK_GIT_ROOT:-${XDG_CACHE_HOME:-$HOME/.cache}/agent-project-kit}"
git -C "$KIT" pull --ff-only origin main
bash "$KIT/scripts/install-to-project.sh" . "$KIT"
)
```

Windows:

```powershell
$kit = if ($env:APK_GIT_ROOT) { $env:APK_GIT_ROOT } else { Join-Path $env:LOCALAPPDATA "agent-project-kit" }
git -C $kit pull --ff-only origin main
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
powershell -ExecutionPolicy Bypass -File (Join-Path $kit "scripts\install-to-project.ps1") -ProjectPath . -SourcePath $kit
```

Project-local files under `.ai/` are preserved.
