# Changelog

All notable changes to Agent Project Kit are summarized here.

## 6.28-existing-project-update — 2026-07-12

- Added `UPDATE_EXISTING_PROJECT.md` with a preflight, dry-run, apply, verify,
  schema-decision, and rollback loop for projects that already have the kit.
- Added `--dry-run` support to `scripts/install-from-git.sh` and `-DryRun` to
  `scripts/install-from-git.ps1`.
- Updated README and install docs so existing-project updates use
  `install-from-git` and preserve project-local `.ai/` state.

## 6.27-readme-changelog — 2026-07-11

- Added this changelog and included it in the installed package snapshot.
- Updated the English and Thai README files with a concise benefit statement.
- Kept public README wording lightweight while pointing agents to project-local
  state, machine/version metadata, hierarchy context, and deadline-aware resume.

## 6.26-version-update-check — 2026-07-11

- Added startup reporting of the installed Agent Project Kit package name and
  version from `.ai/COMPUTING_ENVIRONMENT_VERSION.md`.
- Added periodic update-check guidance: check upstream when no prior check
  exists, after 14 days, before package-level/release work, or when requested.
- Updated installers and metadata templates to record update-check cadence.

## 6.25-status-deadline-dashboard — 2026-07-11

- Added status/deadline dashboard fields to project state and review templates.
- Updated resume prompts so projects with deadlines start from last-session
  status and next actions ordered by priority and due date.

## 6.24-project-local-loops — 2026-07-11

- Clarified that L1/L2/L3 loop diagnosis is local to the current project or
  hierarchy level before using parent context.

## 6.23-hierarchy-resume — 2026-07-11

- Clarified hierarchical resume behavior: reuse known parent summaries and
  compatible machine profiles, but keep child/subproject state sharper and local.

## 6.22-public-readme-trim — 2026-07-08

- Simplified public README pages into a lighter install-and-test introduction.
- Kept deeper workflow and storage policy in internal package files instead of
  the public landing pages.
