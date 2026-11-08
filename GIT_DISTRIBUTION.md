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
    agent-project-kit/        # installed snapshot used by agents

machine-local hot tier/
  agent-project-kit/          # git clone/source cache; never cloud-synced
```

Project-local state stays directly under `.ai/`. The Git clone is only the
package source and must stay outside every cloud-synced tree. The installed
snapshot is `.ai/agent-project-kit/`. The old `.ai/computing-environment/` path
is legacy-only.

## Install From Git

Agent-first flow from the target project:

```bash
KIT="${APK_GIT_ROOT:-${XDG_CACHE_HOME:-$HOME/.cache}/agent-project-kit}"
git clone https://github.com/punpiti/agent-project-kit.git "$KIT"
bash "$KIT/scripts/install-to-project.sh" . "$KIT"
code .
```

After install, open the project in VS Code, Claude Code, Antigravity, or another
agent. The root adapter files tell the agent to read `.ai/`.

From the target project:

```bash
bash /path/to/agent-project-kit/scripts/install-from-git.sh . https://github.com/punpiti/agent-project-kit.git v6.16.0
```

The updater reuses `APK_GIT_ROOT` (or the platform's machine-local default),
fetches and checks out the requested ref, and refuses a clone path detected
inside OneDrive, Dropbox, Google Drive, or iCloud Drive.

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
$kit = if ($env:APK_GIT_ROOT) { $env:APK_GIT_ROOT } else { Join-Path $env:LOCALAPPDATA "agent-project-kit" }
git clone https://github.com/punpiti/agent-project-kit.git $kit
powershell -ExecutionPolicy Bypass -File (Join-Path $kit "scripts\install-to-project.ps1") -ProjectPath . -SourcePath $kit
```

## Rules

- Do not store project-specific state inside `.ai/agent-project-kit/`.
- Do not commit `.ai/` project state into the Agent Project Kit repository.
- Keep project state in the target project root `.ai/`.
- Record the installed ref/commit in `.ai/COMPUTING_ENVIRONMENT_VERSION.md`.
- Never create or update Git metadata in a cloud-synced folder. This covers
  clones, worktrees, bare/mirror repos, submodules, LFS objects, and Git caches.
