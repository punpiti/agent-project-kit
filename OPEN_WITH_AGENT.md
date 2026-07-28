# Open With Agent

Goal: clone Agent Project Kit into a project, open the folder in VS Code,
Claude Code, Antigravity, or another coding agent, and let the agent continue
from project-local `.ai/` state.

## New Project

Create and enter the project folder first:

```bash
mkdir my-project
cd my-project
mkdir -p .ai
git clone https://github.com/punpiti/agent-project-kit.git .ai/agent-project-kit-source
bash .ai/agent-project-kit-source/scripts/install-to-project.sh . .ai/agent-project-kit-source
code .
```

Windows PowerShell:

```powershell
New-Item -ItemType Directory -Force -Path "my-project" | Out-Null
Set-Location "my-project"
New-Item -ItemType Directory -Force -Path ".ai" | Out-Null
git clone https://github.com/punpiti/agent-project-kit.git ".ai\agent-project-kit-source"
powershell -ExecutionPolicy Bypass -File ".ai\agent-project-kit-source\scripts\install-to-project.ps1" -ProjectPath . -SourcePath ".ai\agent-project-kit-source"
code .
```

## Existing Project

From the existing project root:

```bash
mkdir -p .ai
git clone https://github.com/punpiti/agent-project-kit.git .ai/agent-project-kit-source
bash .ai/agent-project-kit-source/scripts/install-to-project.sh . .ai/agent-project-kit-source
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
New-Item -ItemType Directory -Force -Path ".ai" | Out-Null
git clone https://github.com/punpiti/agent-project-kit.git ".ai\agent-project-kit-source"
powershell -ExecutionPolicy Bypass -File ".ai\agent-project-kit-source\scripts\install-to-project.ps1" -ProjectPath . -SourcePath ".ai\agent-project-kit-source"
code .
```

## If The Agent Is Already Open

Tell the agent:

```text
If this project has `.ai/agent-project-kit/` but does not yet have root
`AGENTS.md`, `CLAUDE.md`, `ANTIGRAVITY.md`, and `.ai/agent-project-kit/`,
run the Agent Project Kit installer from `.ai/agent-project-kit-source/scripts/`
or run the updater from `.ai/agent-project-kit/scripts/`.
Then read `AGENTS.md`, `.ai/agent-project-kit/`, and project-local `.ai/`
state before working.
```

## Update Later

```bash
git -C .ai/agent-project-kit-source pull --ff-only
bash .ai/agent-project-kit-source/scripts/install-to-project.sh . .ai/agent-project-kit-source
```

Windows:

```powershell
git -C ".ai\agent-project-kit-source" pull --ff-only
powershell -ExecutionPolicy Bypass -File ".ai\agent-project-kit-source\scripts\install-to-project.ps1" -ProjectPath . -SourcePath ".ai\agent-project-kit-source"
```

Project-local files under `.ai/` are preserved.
