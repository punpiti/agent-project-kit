# Changelog

All notable changes to Agent Project Kit are summarized here.

## 6.33-gh-pages-content — 2026-07-28

- Added `index.md` as the GitHub Pages landing page instead of relying on the
  repository README rendering alone.
- Summarized current install paths, update checks, first-install conflict
  behavior, and project prompt-pack placement for readers arriving from Pages.
- Included `index.md` in package contents and installer snapshots.

## 6.32-agent-project-kit-path — 2026-07-28

- Changed the canonical installed snapshot path to `.ai/agent-project-kit/`.
- Kept `.ai/computing-environment/` as a legacy migration path only.
- Changed local git clone/source examples to `.ai/agent-project-kit-source/` so
  the source clone does not collide with the installed snapshot.

## 6.31-first-install-conflict-guard — 2026-07-28

- Added first-install conflict guards for `.ai/agent-project-kit/`,
  `.ai/COMPUTING_ENVIRONMENT_VERSION.md`, and
  `.ai/INSTALLATION_INFO.md`.
- Installers now stop on same-name non-kit files or directories instead of
  overwriting or moving existing user content.
- Root client files such as `AGENTS.md`, `CLAUDE.md`, and `ANTIGRAVITY.md` keep
  the existing append-managed-block behavior.

## 6.30-gh-pages-update-check — 2026-07-28

- Added `scripts/update-from-pages.sh` and `scripts/update-from-pages.ps1`.
- The new update path checks the GitHub Pages `manifest.json` first, reports
  package/schema differences, and only calls the existing git updater when a
  newer or different package version is found.
- Existing project-local `.ai/` state is still preserved; updated package
  concepts are refreshed under `.ai/agent-project-kit/`.

## 6.29-research-project-prompts — 2026-07-12

- Added `prompts/13_RESEARCH_PROJECT_PROMPTS.md` for research-oriented projects.
- The prompt pack covers deep dives, recent literature reviews,
  counter-argument checks, source credibility verification, competitive or
  alternative analysis, trend scans, data interpretation, expert breakdowns,
  and concise research briefs.
- Added a research-project startup prompt that routes agents to the right
  research mode before scanning or browsing broadly.

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
