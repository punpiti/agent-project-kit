# Agent Project Kit

[ภาษาไทย](README.th.md)

Agent Project Kit (APK) installs a small set of instruction files and `.ai/`
project notes so AI coding agents such as Claude Code, Codex, and Antigravity
can pick up a project where the last session stopped, choose a way of working
that fits the task, and check their output before handing it over. Your code
and documents stay yours. The kit lives in `.ai/agent-project-kit/` and can be
refreshed without touching your notes.

Current release: `8.0.1-python-core-canary`

## What It Does For You

- Resume in one line. Tell the agent "read the md files and continue" and it
  starts from `.ai/PROJECT_STATE.md`: what was done, what was decided, and what
  comes next.
- Route each request to a fitting workflow. Writing a textbook chapter,
  reviewing a thesis, answering journal reviewers, drafting a policy, writing
  an official letter, building teaching slides, and analysing data each get
  their own workflow plus the quality checks that apply.
- Check the output. Numbers are read from result files, generated documents
  and decks are opened after they are built, reader-facing prose goes through a
  style checker, and Thai Word files get their font and word breaking repaired.
- Keep your files safe. Install and update keep project notes and your own
  instructions unchanged, and a failed update restores the previous copy.
- Work across machines. Linux, macOS, WSL2, and Windows use the same installer.

This is a canary release, tested on Linux, WSL2, and Windows. It has not yet
been tested on macOS hardware.

## Requirements

- Git
- Python 3.9 or newer
  - macOS / Linux / WSL2: usually present as `python3`.
  - Windows: install the Python install manager from
    <https://www.python.org/downloads/>, which provides `py`. The Microsoft
    Store `python` alias only opens the Store, so the installer skips it.
- Bash (macOS / Linux / WSL2) or PowerShell 5.1 / 7 (Windows)

After installing Git or Python, open a new terminal so it can see them. WSL2
keeps the Windows `PATH` it started with, so restart WSL2 (`wsl --shutdown`)
before calling newly installed Windows tools from it.

## Quick Start

Create or open the project folder first:

```bash
mkdir my-project
cd my-project
```

### macOS / Linux

```bash
mkdir -p .ai
git clone https://github.com/punpiti/agent-project-kit.git .ai/agent-project-kit-source
bash .ai/agent-project-kit-source/scripts/install-to-project.sh . .ai/agent-project-kit-source
```

### WSL2 with a Windows-synced project folder (OneDrive)

Keep the Git clone in a WSL-local cache and install only the snapshot into the
project. Git metadata inside a synced folder is slow and can break.

```bash
KIT="${XDG_CACHE_HOME:-$HOME/.cache}/agent-project-kit"
if [ -d "$KIT/.git" ]; then
  git -C "$KIT" pull --ff-only
else
  git clone https://github.com/punpiti/agent-project-kit.git "$KIT"
fi
bash "$KIT/scripts/install-to-project.sh" . "$KIT"
```

### Windows PowerShell

```powershell
New-Item -ItemType Directory -Force -Path ".ai" | Out-Null
git clone https://github.com/punpiti/agent-project-kit.git ".ai\agent-project-kit-source"
powershell -ExecutionPolicy Bypass -File ".ai\agent-project-kit-source\scripts\install-to-project.ps1" -ProjectPath . -SourcePath ".ai\agent-project-kit-source"
```

PowerShell 7 works the same way with `pwsh` in place of `powershell`.

## Start Working With An Agent

Open the folder in your coding agent and say:

```text
Read AGENTS.md and .ai/PROJECT_STATE.md, then continue with the next action.
```

On a new project the agent fills in `.ai/PROJECT_STATE.md` first. Later
sessions need only that sentence, or a request such as "write chapter 3 from
the outline" or "answer the reviewer comments one by one".

## What Gets Installed

```text
AGENTS.md, CLAUDE.md, ANTIGRAVITY.md  # where each agent starts; your text is kept
.ai/PROJECT_STATE.md                  # the project's current state (yours)
.ai/SESSION_LOG.md, .ai/RUNBOOK.md    # history and project commands (yours)
.ai/MACHINE_PROFILE.md                # what this machine can run (yours)
.ai/agent-project-kit/                # the kit itself, replaced on update
```

Keep your own prompt packs in `.ai/prompts/` or another folder named in
`.ai/PROJECT_STATE.md`. Anything inside `.ai/agent-project-kit/` is replaced
on update.

## Keep A Project Healthy

Check the installation and project notes:

```bash
python3 .ai/agent-project-kit/scripts/apk_doctor.py . --quick
```

The doctor reports an uninitialized or stale `PROJECT_STATE.md`, version drift,
malformed `.ai/project.json` or `.ai/apk.json`, and legacy state that is being
ignored.

Older projects may have notes in `.ai/state.json` that agents no longer read.
Preview, then move them into `PROJECT_STATE.md`:

```bash
python3 .ai/agent-project-kit/scripts/migrate_state.py --project .          # preview only
python3 .ai/agent-project-kit/scripts/migrate_state.py --project . --write  # append and back up
```

The move appends one marked section and renames `state.json` to a dated
backup. Nothing is deleted. On Windows use `py -3` in place of `python3`.

## Update An Existing Project

Preview first, then apply:

```bash
bash .ai/agent-project-kit/scripts/update-from-pages.sh --dry-run .
bash .ai/agent-project-kit/scripts/update-from-pages.sh .
```

WSL2 with a Windows-synced folder:

```bash
KIT="${XDG_CACHE_HOME:-$HOME/.cache}/agent-project-kit"
bash "$KIT/scripts/update-from-pages.sh" --dry-run .
bash "$KIT/scripts/update-from-pages.sh" .
```

Windows PowerShell (needs Git and Python 3.9+):

```powershell
powershell -ExecutionPolicy Bypass -File ".ai\agent-project-kit\scripts\update-from-pages.ps1" -ProjectPath . -DryRun
powershell -ExecutionPolicy Bypass -File ".ai\agent-project-kit\scripts\update-from-pages.ps1" -ProjectPath .
```

The updater reads the published manifest, checks out the exact release tag,
and refuses downgrades and version mismatches. Agents check for a newer release
at most once every 14 days and only report it. They never update on their own.
See [UPDATE_EXISTING_PROJECT.md](UPDATE_EXISTING_PROJECT.md) for the full
checklist.

## Safety Model

- Project notes under `.ai/` are created only when missing and are never
  overwritten.
- `AGENTS.md`, `CLAUDE.md`, and `ANTIGRAVITY.md` keep your text. The kit
  maintains one marked block in `AGENTS.md` and adds a short adapter note to
  the other two.
- A new snapshot is staged and SHA-256 verified before it replaces the old one.
  The old one stays as `.ai/agent-project-kit.previous`. If any step fails,
  the previous snapshot and every file the installer touched are restored.
- A same-name folder or metadata file that does not look like the kit stops
  the install before anything is written.
- The source clone and the installed snapshot use different paths.

## Workflows And Prompt Packs

You do not pick prompt packs by hand. The agent reads
`.ai/agent-project-kit/STARTUP.md`, classifies the request, and loads one
workflow plus the checks it needs. To see the routing decision for a request:

```bash
python3 .ai/agent-project-kit/scripts/route_task.py "write chapter 3 of the textbook"
```

The workflows cover software, research, book writing, presentations, content
analysis, data analytics, course material, educational policy, and
administrative work. Each has a prompt pack under
`.ai/agent-project-kit/prompts/`.

## Shared Runtime For Several WSL2 Projects (Canary)

Several WSL2 projects can share one verified, versioned copy of the kit under
the OneDrive root. Each project keeps its own notes and a fallback snapshot.

```bash
PROJECT="/home/<user>/OneDrive/path/to/project"
KIT="${XDG_CACHE_HOME:-$HOME/.cache}/agent-project-kit"
APK_SHARED_ROOT="/home/<user>/OneDrive/.agent-project-kit"
APK_MACHINE_HOME="$HOME/.local/share/agent-project-kit"

# once per machine: install the shared version and set up the shell
python3 "$KIT/scripts/install-shared.py" --source "$KIT" \
  --shared-root "$APK_SHARED_ROOT" --machine-home "$APK_MACHINE_HOME" --configure-shell

# per project: install the fallback snapshot, back up any old binding, bind
bash "$KIT/scripts/install-to-project.sh" "$PROJECT" "$KIT"
[ -f "$PROJECT/.ai/apk.json" ] && cp -p "$PROJECT/.ai/apk.json" "$PROJECT/.ai/apk.json.backup-$(date +%Y%m%d)"
python3 "$KIT/scripts/install-shared.py" --source "$KIT" --bind-project "$PROJECT"

# verify
"$APK_MACHINE_HOME/bin/apk" --project "$PROJECT" resolve
```

`--configure-shell` writes one managed block to `~/.bashrc`. Open a new shell
afterwards. `resolve` checks the shared copy against its pinned SHA-256 digest
and refuses a modified runtime. To fall back to the project snapshot, run
`python3 "$KIT/scripts/apk.py" --project "$PROJECT" rollback`. To undo it, move
`.ai/apk.json.disabled` back to `.ai/apk.json`. Try a few projects
before binding many.

## Troubleshooting

- `Agent Project Kit needs Python 3.9 or newer`: install Python (see
  Requirements) and open a new terminal.
- `git not found` on Windows: install Git for Windows and open a new terminal.
  From WSL2, restart WSL2 first.
- `Input/output error` from WSL2 inside OneDrive: the file is usually
  online-only. Open it once from Windows, or mark the folder "Always keep on
  this device", then retry. A Windows path longer than 260 characters causes
  the same error. Shorten or move it from PowerShell with `-LiteralPath`.
- `Refusing to overwrite existing ...`: a folder or file with a kit name holds
  your content. Rename it, then rerun the installer.

## More

- [CHANGELOG.md](CHANGELOG.md)
- [INSTALL_IN_PROJECT.md](INSTALL_IN_PROJECT.md)
- [UPDATE_EXISTING_PROJECT.md](UPDATE_EXISTING_PROJECT.md)
- [GIT_DISTRIBUTION.md](GIT_DISTRIBUTION.md)

This repository ignores `.ai/`, which holds local project state and installed
snapshots. The old package name `computing-environment` and path
`.ai/computing-environment/` are kept for migration only.
