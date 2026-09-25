---
title: Agent Project Kit
---

# Agent Project Kit

Agent Project Kit (APK) helps AI coding agents such as Claude Code, Codex, and
Antigravity work on the same project across many sessions. The agent resumes
from the project's own notes, picks a workflow that fits the request, and
checks its output before handing it over. Your files stay yours.

[README](README.md) | [ภาษาไทย](README.th.md) | [GitHub repository](https://github.com/punpiti/agent-project-kit) | [Changelog](CHANGELOG.md) | [Manifest](manifest.json)

## Current Release

- Current package version: `8.0.1-python-core-canary`
- Requires Git and Python 3.9 or newer on every platform
- Tested on Linux, WSL2, and Windows (canary; macOS hardware not yet tested)

## What It Does For You

- Resume in one line: "Read AGENTS.md and .ai/PROJECT_STATE.md, then continue
  with the next action."
- One request, one fitting workflow. Textbook chapters, thesis reviews, reviewer
  responses, policy drafts, official letters, teaching slides, and data
  analysis each get their own workflow and checks.
- Output is checked. Numbers come from result files, built documents and decks
  are opened, reader-facing prose goes through a style checker, and Thai Word
  files get their font and word breaking repaired.
- Install and update keep your notes and instructions unchanged. A failed
  update restores the previous copy.

| Task | Example request | Workflow the agent uses |
|---|---|---|
| Write a textbook | Write chapter 3 from the outline and evidence | Book writing with prose check |
| Build a book preview | Build the textbook as a PDF preview | Book writing with publication build and file check |
| Review a thesis | Review this thesis as an external examiner | Research with reviewer-style findings |
| Answer reviewers | Answer the journal reviewers point by point | Research with a response mapped to each change |
| Draft a policy | Draft an AI-in-teaching policy for the university council | Educational policy with prose check |
| Official letter | Write an official letter to the faculty | Administrative work with prose check |
| Teaching slides | Create slides to teach machine learning | Presentation with render and file check |
| Data analysis | Analyse rainfall from 130 stations and plot it | Data analytics |

## Install

Git and Python 3.9+ are required. On Windows, install the Python install manager
from <https://www.python.org/downloads/> (it provides `py`).

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

Then open the folder in your agent and say:

```text
Read AGENTS.md and .ai/PROJECT_STATE.md, then continue with the next action.
```

## Update

```bash
bash .ai/agent-project-kit/scripts/update-from-pages.sh --dry-run .
bash .ai/agent-project-kit/scripts/update-from-pages.sh .
```

On Windows, run `.ai\agent-project-kit\scripts\update-from-pages.ps1 -ProjectPath .`
with `-DryRun` first. The updater checks out the exact release named in this
site's manifest and refuses downgrades.

## Check A Project

```bash
python3 .ai/agent-project-kit/scripts/apk_doctor.py . --quick
python3 .ai/agent-project-kit/scripts/migrate_state.py --project .
```

The doctor reports stale or uninitialized project notes and malformed settings.
The migration command previews legacy `.ai/state.json` notes that agents no
longer read. Add `--write` to move them into `PROJECT_STATE.md` with a backup.

## More Docs

- [README](README.md) with requirements, troubleshooting, and the shared runtime
- [Install details](INSTALL_IN_PROJECT.md)
- [Update an existing project](UPDATE_EXISTING_PROJECT.md)
- [Git distribution](GIT_DISTRIBUTION.md)
