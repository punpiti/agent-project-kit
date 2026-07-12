# Git Distribution

Recommended public/friends workflow:

```text
project/
  .ai/
    PROJECT_STATE.md
    PROJECT_HIERARCHY.md
    MACHINE_PROFILE.md
    LOCAL_RESOURCES.md
    ...
    agent-project-kit/        # git clone of the kit
    computing-environment/    # installed snapshot used by agents
```

Project-local state stays directly under `.ai/`. The Git clone is only the
package source. The installed snapshot remains `.ai/computing-environment/` for
compatibility.

## Install From Git

Agent-first flow from the target project:

```bash
mkdir -p .ai
git clone https://github.com/punpiti/agent-project-kit.git .ai/agent-project-kit
bash .ai/agent-project-kit/scripts/install-to-project.sh . .ai/agent-project-kit
code .
```

After install, open the project in VS Code, Claude Code, Antigravity, or another
agent. The root adapter files tell the agent to read `.ai/`.

From the target project:

```bash
bash /path/to/agent-project-kit/scripts/install-from-git.sh . https://github.com/punpiti/agent-project-kit.git v6.16.0
```

If the project already has `.ai/agent-project-kit`, the script fetches and checks
out the requested ref. If not, it clones first.

## Update

For the full existing-project update workflow, including preflight, dry run,
verification, and rollback, read `UPDATE_EXISTING_PROJECT.md`.

Pinned release update:

```bash
bash .ai/agent-project-kit/scripts/install-from-git.sh . https://github.com/punpiti/agent-project-kit.git v6.16.0
```

Latest `main` update:

```bash
bash .ai/agent-project-kit/scripts/install-from-git.sh . https://github.com/punpiti/agent-project-kit.git main
```

Pinned tags are better for reproducible work. `main` is convenient for trusted
friends who want the latest behavior.

## Windows PowerShell

```powershell
New-Item -ItemType Directory -Force -Path ".ai" | Out-Null
git clone https://github.com/punpiti/agent-project-kit.git ".ai\agent-project-kit"
powershell -ExecutionPolicy Bypass -File ".ai\agent-project-kit\scripts\install-to-project.ps1" -ProjectPath . -SourcePath ".ai\agent-project-kit"
```

## Rules

- Do not store project-specific state inside `.ai/agent-project-kit/`.
- Do not commit `.ai/` project state into the Agent Project Kit repository.
- Keep project state in the target project root `.ai/`.
- Record the installed ref/commit in `.ai/COMPUTING_ENVIRONMENT_VERSION.md`.
