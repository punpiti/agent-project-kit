# Open With Agent

Goal: clone Agent Project Kit into a project, open the folder in VS Code,
Claude Code, Antigravity, or another coding agent, and let the agent continue
from project-local `.ai/` state.

## Existing Or New Project

From the project root:

```bash
mkdir -p .ai
git clone https://github.com/<owner>/agent-project-kit.git .ai/agent-project-kit
bash .ai/agent-project-kit/scripts/install-to-project.sh . .ai/agent-project-kit
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
.ai/computing-environment/
.ai/PROJECT_STATE.md
.ai/TOKEN_BUDGET.md
```

VS Code/Codex, Claude Code, Antigravity, and similar agents should start from
the root adapter files, then read `.ai/` state.

## Windows PowerShell

From the project root:

```powershell
New-Item -ItemType Directory -Force -Path ".ai" | Out-Null
git clone https://github.com/<owner>/agent-project-kit.git ".ai\agent-project-kit"
powershell -ExecutionPolicy Bypass -File ".ai\agent-project-kit\scripts\install-to-project.ps1" -ProjectPath . -SourcePath ".ai\agent-project-kit"
code .
```

## If The Agent Is Already Open

Tell the agent:

```text
If this project has `.ai/agent-project-kit/` but does not yet have root
`AGENTS.md`, `CLAUDE.md`, `ANTIGRAVITY.md`, and `.ai/computing-environment/`,
run the Agent Project Kit installer from `.ai/agent-project-kit/scripts/`.
Then read `AGENTS.md`, `.ai/computing-environment/`, and project-local `.ai/`
state before working.
```

## Update Later

```bash
git -C .ai/agent-project-kit pull --ff-only
bash .ai/agent-project-kit/scripts/install-to-project.sh . .ai/agent-project-kit
```

Windows:

```powershell
git -C ".ai\agent-project-kit" pull --ff-only
powershell -ExecutionPolicy Bypass -File ".ai\agent-project-kit\scripts\install-to-project.ps1" -ProjectPath . -SourcePath ".ai\agent-project-kit"
```

Project-local files under `.ai/` are preserved.
