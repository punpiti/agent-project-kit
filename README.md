# Agent Project Kit

Portable project instructions and `.ai/` state templates for AI coding agents.

Use it when you want a project folder to remember:

- what the project is
- which machine it is running on
- where local data/cache/resources live
- how much token/cost the agent should spend
- how Codex, Claude Code, Antigravity, or another agent should start work

The old package name was `computing-environment`. That name is still used for
the installed compatibility snapshot: `.ai/computing-environment/`.

## What This Project Does

Agent Project Kit installs a small AI working layer into any project folder.
That layer gives coding agents a consistent way to:

- resume work from project-local notes instead of rereading everything
- detect the current machine and avoid assuming local data/cache paths exist
- keep project, subproject, and parent/child boundaries explicit
- decide whether to work in quick, standard, deep, or agentic-run mode
- ask before spending high token cost when the user is in economy mode
- share one policy across Codex, Claude Code, Antigravity, and similar tools

It is not an app framework and does not change your source code. It adds
instructions, templates, and installer scripts so AI agents can operate more
consistently across machines and projects.

## Conceptual Background

Agent Project Kit is an original, practical workflow design built from repeated
use of AI coding agents across real project folders, machines, documents, and
research work. It is meant to solve operational problems: losing project
context, rerunning machine discovery, mixing parent/child project scope, and
spending token budget without a clear review gate.

Andrew Ng's discussion of agentic AI workflows helped frame some of the
language around reflection, tool use, planning, multi-agent collaboration, and
eval/error analysis. Those ideas are an influence, not the source design.

Agent Project Kit turns that general direction into project-folder mechanics:

- `Spec` and project state make planning explicit.
- `Eval` and review gates make reflection concrete.
- Installer scripts, runbooks, and local-resource manifests support tool use.
- Codex, Claude Code, Antigravity, and future agents share one project policy
  instead of each carrying separate instructions.

This project is independently designed and maintained. It is not affiliated
with or endorsed by Andrew Ng or DeepLearning.AI.

## Quick Start

Run the commands from the project folder you want the agent to work on.

Replace this placeholder with the real repository URL after publishing:

```text
https://github.com/<owner>/agent-project-kit.git
```

### macOS / Linux

```bash
mkdir -p .ai
git clone https://github.com/<owner>/agent-project-kit.git .ai/agent-project-kit
bash .ai/agent-project-kit/scripts/install-to-project.sh . .ai/agent-project-kit
code .
```

If `code .` is not available, open the folder manually in VS Code, Claude Code,
Antigravity, or another coding agent.

### Windows PowerShell

```powershell
New-Item -ItemType Directory -Force -Path ".ai" | Out-Null
git clone https://github.com/<owner>/agent-project-kit.git ".ai\agent-project-kit"
powershell -ExecutionPolicy Bypass -File ".ai\agent-project-kit\scripts\install-to-project.ps1" -ProjectPath . -SourcePath ".ai\agent-project-kit"
code .
```

PowerShell 7 also works:

```powershell
pwsh -ExecutionPolicy Bypass -File ".ai\agent-project-kit\scripts\install-to-project.ps1" -ProjectPath . -SourcePath ".ai\agent-project-kit"
```

### WSL2

From the WSL shell, run inside the project folder:

```bash
mkdir -p .ai
git clone https://github.com/<owner>/agent-project-kit.git .ai/agent-project-kit
bash .ai/agent-project-kit/scripts/install-to-project.sh . .ai/agent-project-kit
code .
```

If the project is on Windows OneDrive, WSL paths usually look like:

```text
/mnt/c/Users/<windows-user>/OneDrive/<project>
```

WSL can also call Windows PowerShell directly:

```bash
powershell.exe -ExecutionPolicy Bypass -File ".ai\\agent-project-kit\\scripts\\install-to-project.ps1" -ProjectPath . -SourcePath ".ai\\agent-project-kit"
```

## What Gets Installed

After install, the project root has:

```text
AGENTS.md
CLAUDE.md
ANTIGRAVITY.md
.ai/computing-environment/
.ai/PROJECT_STATE.md
.ai/PROJECT_HIERARCHY.md
.ai/COMPUTING_ENVIRONMENT_VERSION.md
.ai/MACHINE_PROFILE.md
.ai/LOCAL_RESOURCES.md
.ai/MACHINE_COMPATIBILITY.md
.ai/RUNBOOK.md
.ai/TOKEN_BUDGET.md
.ai/SESSION_LOG.md
```

The root adapter files tell AI clients where to start:

- `AGENTS.md` for Codex and generic agents
- `CLAUDE.md` for Claude Code
- `ANTIGRAVITY.md` for Antigravity-style agent IDEs

The full installed kit lives under `.ai/computing-environment/`.
Project-specific state stays directly under `.ai/`.

The installer refreshes the package snapshot but does not overwrite existing
project state files such as `.ai/PROJECT_STATE.md`, `.ai/MACHINE_PROFILE.md`,
or `.ai/LOCAL_RESOURCES.md`.

## First Prompt For An Agent

After installing and opening the folder, tell the agent:

```text
Read AGENTS.md and .ai/computing-environment first.
Then read .ai/PROJECT_STATE.md, .ai/PROJECT_HIERARCHY.md,
.ai/COMPUTING_ENVIRONMENT_VERSION.md, .ai/MACHINE_PROFILE.md,
.ai/LOCAL_RESOURCES.md, .ai/MACHINE_COMPATIBILITY.md, .ai/RUNBOOK.md,
and .ai/TOKEN_BUDGET.md.
Summarize where this project is, what machine this is, what local resources are
missing, and what token/cost mode should be used before starting the task.
```

For Thai-speaking users:

```text
อ่าน AGENTS.md และ .ai/computing-environment ก่อน
จากนั้นอ่าน .ai/PROJECT_STATE.md, .ai/PROJECT_HIERARCHY.md,
.ai/COMPUTING_ENVIRONMENT_VERSION.md, .ai/MACHINE_PROFILE.md,
.ai/LOCAL_RESOURCES.md, .ai/MACHINE_COMPATIBILITY.md, .ai/RUNBOOK.md,
และ .ai/TOKEN_BUDGET.md
สรุปว่า project ค้างตรงไหน เครื่องนี้คือเครื่องอะไร มี local resource อะไรขาด
และควรใช้ token/cost mode แบบไหน ก่อนเริ่มทำงาน
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

For reproducible installs, use release tags instead of `main` after tags are
published.

## Token / Cost Modes

Agent Project Kit separates task depth from token-cost sensitivity:

```text
T0 Quick       small answer or one-file check
T1 Standard    normal focused work
T2 Deep        architecture, review, research, hard bugs
T3 Agentic Run code/test/debug loops

C0 Economy     ask before high-cost scans/research/test loops
C1 Normal      default balance
C2 Premium     prioritize completeness while keeping scope disciplined
```

Project defaults live in `.ai/TOKEN_BUDGET.md`.

## Machine And Local Resources

The kit is machine-aware. On first use, the agent should identify whether it is
on macOS, Windows, Linux, WSL2, or an unknown machine.

If a project uses local resources outside the repo, record them in:

```text
.ai/LOCAL_RESOURCES.md
.ai/MACHINE_COMPATIBILITY.md
.ai/RUNBOOK.md
```

Do not hardcode machine-specific paths into source code. Use environment
variables such as:

```bash
PROJECT_DATA_ROOT=/path/to/data
PROJECT_CACHE_ROOT=/path/to/cache
PROJECT_OUTPUT_ROOT=/path/to/output
```

## Project And Subproject Rules

Use `.ai/PROJECT_HIERARCHY.md` to say whether a folder is:

- a project
- a subproject
- a document package
- a data area
- a plain subdirectory

A subdirectory is not a subproject unless it is explicitly marked.

Child projects may read parent summaries as a read-only interface, but should
not edit parent files, parent `.ai/` state, parent logs, or sibling projects
unless explicitly asked.

## Documentation And Paper Work

For documents, papers, policy notes, and teaching material:

- draft Markdown first
- critique logic/evidence/audience before polishing language
- build PDF/DOCX/slides only after content is stable
- keep AI scratch Markdown under `.ai/`

Formal Thai A4 PDFs can use:

```text
templates/pandoc-thai-a4/
```

## More Docs

- `OPEN_WITH_AGENT.md` — short clone/install/open workflow
- `GIT_DISTRIBUTION.md` — clone/update details
- `INSTALL_IN_PROJECT.md` — fuller installation notes
- `AI_CLIENTS.md` — Codex / Claude / Antigravity adapter strategy
- `TOKEN_DISCIPLINE.md` — token and cost rules
- `MACHINE_PROFILES.md` — machine-aware workflow
- `DOCUMENT_PRODUCTION_POLICY.md` — document production rules
- `MARKDOWN_ORGANIZATION_POLICY.md` — safe Markdown classification

## Repository Notes

This repository intentionally ignores `.ai/` because that directory contains
local project state and installed snapshots. Do not commit project-specific
state into the Agent Project Kit repo.

The old `.p12` file found in the previous package was intentionally excluded.
See `SECURITY_EXCLUSIONS.md`.
