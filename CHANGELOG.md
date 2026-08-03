# Changelog

All notable changes to Agent Project Kit are summarized here.

## 7.1-shared-runtime-canary — 2026-08-03

- Added an opt-in shared-runtime prototype with immutable side-by-side versions.
- Added exact project binding through `.ai/apk.json` and explicit resolver errors
  for missing or mismatched versions.
- Added a package file manifest and aggregate SHA-256 pinned in the project
  binding; the resolver now rejects missing, added, or modified runtime files.
- Kept the existing per-project snapshot installer as the unchanged default.
- Added isolated tests for install, resolve, context execution, missing-version
  failure, content tampering, snapshot rollback, and root non-recursion.
- Defined promotion gates and rollback as removing the binding while retaining
  the existing project snapshot.

## 7.0.2-onedrive-route-audit — 2026-08-03

- Audited all 47 discovered OneDrive `PROJECT_STATE.md` markers: 27 configured
  projects and 20 placeholder states.
- Reviewed configured routes across education, research, governance, software,
  administration, advising, presentations, and technical fallback work.
- Added regression coverage for seminars, course decks, IOI/POSN governance,
  research supervision, correspondence, nominations, and academic-rank files.
- Removed broad code signals such as generic `test`, `build`, and `package`
  mentions when they do not express a software deliverable.
- Kept clarification intentionally for a context-only parent workspace and a
  technical DIY project outside the core routes.

## 7.0.1-route-hardening — 2026-08-03

- Trialed structured routing read-only against six real downstream projects:
  educational policy, course development, research paper, software, compliance
  operations, and council presentation.
- Fixed `manuscript` being misclassified as software because it contains the
  substring `script`.
- Made explicit output forms such as presentation outrank subject terms such as
  policy when selecting the deliverable axis.
- Added real failure cases to bilingual routing fixtures.

## 7.0-structured-context — 2026-08-03

- Added structured four-axis routing: domain, deliverable, methods, and lifecycle.
- Added declarative route, workflow, and policy configuration under `config/`.
- Added `scripts/context.py` to compile a minimal auditable context bundle with
  source, byte, and estimated-token metrics.
- Added non-destructive `project.json`, `state.json`, and `local-resources.json`
  alongside Markdown compatibility state.
- Added bilingual routing fixtures and structured-context acceptance tests.
- Kept existing Markdown state and prompts as compatibility/human-readable
  interfaces during incremental downstream migration.

## 6.39-composable-prompt-catalog — 2026-08-03

- Added `prompts/catalog.json` as the machine-readable source of truth for
  prompt role, trigger, cadence, and composition.
- Enforced one primary route and at most two secondary workflows per request.
- Classified all 22 prompts as primary, secondary, one-time, or reference.
- Split Presentation from Course Material Development, converted the legacy
  policy prompt into a redirect, and reduced machine discovery to a conditional
  one-time workflow.
- Added prompt-catalog validation to the acceptance suite.

## 6.38-practical-route-coverage — 2026-08-03

- Added Software Development & Automation as a primary route; web development
  is now a focused subtype rather than a competing top-level category.
- Added Administrative & Professional Operations for compliance, deadlines,
  correspondence, dossiers, and professional case management.
- Added Strategy & Advisory as a secondary workflow for mixed deliverables.
- Added a Technical / Other fallback while keeping personal finance under its
  project-specific workflow.
- Extended doctor checks to flag placeholder and stale `PROJECT_STATE.md` files.

## 6.37-education-policy-route — 2026-08-03

- Added Educational Policy Development as a seventh primary work route for
  university governance, education agencies, curriculum policy, standards, and
  academic-competition governance.
- Clarified routing by deliverable: policy/decision work uses the policy route;
  studies and evidence synthesis use Research Activities.
- Defined Research Activities as a secondary evidence workflow when supporting
  an educational policy deliverable.

## 6.36-work-type-router — 2026-08-03

- Changed startup routing to six primary work types: Web Development, Research
  Activities, Content Analysis, Data Analytics, Presentation, and Course
  Material Development.
- Added focused route prompts for web development, content analysis, data
  analytics, and course material development.
- Reclassified resume, onboarding, reviewer response, document production, and
  package maintenance as secondary workflows rather than competing task types.

## 6.35-fast-start-router — 2026-08-03

- Added `STARTUP.md` as a three-file startup contract with task routing and
  conditional context loading.
- Added `scripts/run-once.py` to record successful project- or machine-scoped
  checks with optional expiry; failed commands are not recorded.
- Added read-only `scripts/apk_doctor.py` consistency checks.
- Made installer-managed `AGENTS.md` blocks upgradeable and concise while
  preserving user-authored content.
- Stopped repeated installs from appending duplicate installation log entries.
- Added repeatable fast-start acceptance tests.

## 6.34-readme-refresh — 2026-07-28

- Refreshed `README.md` and `README.th.md` so the repository README content
  matches the newer GitHub Pages positioning.
- Added clear current-path guidance for `.ai/agent-project-kit/` and
  `.ai/agent-project-kit-source/`.
- Documented where project-specific prompt packs should live so they are not
  placed inside the managed kit snapshot.

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
