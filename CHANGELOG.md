# Changelog

All notable changes to Agent Project Kit are summarized here.

## Unreleased

- One updater core: `scripts/apk_update.py` (`from-git`, `from-pages`).
  `install-from-git` and `update-from-pages` in Bash and PowerShell are now thin
  wrappers, sharing `scripts/apk-python.{sh,ps1}` to find Python. A parity
  harness against the previous Bash updater matched output, exit codes, and
  project files across 9 scenarios: dry run, apply, no newer, downgrade,
  git_ref/version mismatch, non-git clone path, branch ref, and missing repo URL.
  The one change is that an unreadable manifest now reports the kit's message
  first instead of curl's. The checked-out release still installs with its own
  installer, and manifests are read with urllib (https and file URLs).

- One installer core: `scripts/apk_install.py`. `install-to-project.sh` and
  `install-to-project.ps1` are now thin wrappers (12 and about 30 lines,
  replacing about 1,160 duplicated lines). A parity harness against the
  previous Bash installer matched byte-for-byte, including file modes, output,
  and exit codes, across 16 scenarios (fresh, user files, CRLF, managed block
  in the middle, malformed block, foreign snapshot/metadata/previous, migrated
  state, self-host, reinstall rotation, symlinked source, missing item). The
  only differences were test-folder paths in the error messages. Windows now
  gets the Bash behavior; the old PowerShell installer had drifted in five
  places.
- Python 3.8+ is now required to install on Windows (owner decision). The
  wrapper uses `py -3`, then `python3`, then `python`, and skips the Microsoft
  Store stub.
- Found on native Windows and fixed: renaming a just-renamed snapshot folder
  back during rollback could fail with `Access is denied`, leaving no active
  snapshot. Renames now retry sharing violations. Rollback continues past a
  failed step, never deletes `.previous` while it holds the only good copy,
  and prints manual recovery steps. The PowerShell wrapper no longer turns
  Python's stderr into a terminating error.

- `apk_doctor.py` no longer reads the next line as a field value when a field is
  empty. On an unfilled `PROJECT_STATE.md` template, it had reported the
  `Updated by` line as an invalid `Last updated` date. This affected 20 of 65
  local projects.

## 7.9.0-state-migration-canary — 2026-09-25

- Fixes from a read-only trial on real downstream projects (book, research
  data, policy). An initialized `PROJECT_STATE.md` now counts as onboarded
  even when `project.json` is still the placeholder template. Before, 38 of 40
  local projects were told to onboard again on every routed request. Survey
  analysis ("survey", "ผลสำรวจ", "แบบสอบถาม") now attaches the data-analytics
  method, matching the STARTUP example.

- `release_check.py` now runs the native-Windows shared-runtime test itself on
  a WSL host with the Windows `py` launcher. Without that host, or with
  `--skip-windows`, the result is never release-ready. Owner policy: every
  release runs it.
- The registry is now the only source of always-on policy text. New
  `policy_sources` point each policy to the heading that holds its full rule.
  `sync_workflow_registry.py` generates the "Always-On Policies" block in
  `STARTUP.md` and fails when that block is stale or a heading is missing.
- Added the legacy state migration contract (`config/STATE_MIGRATION.md`) and
  `scripts/migrate_state.py`. It runs as a dry run by default. `--write`
  appends a marked section to `PROJECT_STATE.md` and renames `state.json` to a
  dated backup, and a second run is a no-op. Installers no longer recreate
  `state.json` after migration. `apk_doctor.py` warns when a configured
  `state.json` is hidden by `PROJECT_STATE.md`. Added a legacy-state schema.

## 7.8.0-routing-schemas-canary — 2026-09-25

- Added JSON Schemas (draft 2020-12) in `config/schemas/` for the workflow
  registry, routing rules, the `.ai/apk.json` binding, and `.ai/project.json`.
  Kit-owned files reject unknown keys; `project.json` allows project keys.
  `scripts/validate_schemas.py` validates with the stdlib only, so native
  Windows needs no extra package, and it fails closed on unsupported keywords.
  It runs from `validate_prompt_catalog.py`. `apk_doctor.py` now reports schema
  errors in a project's binding and metadata. `tests/test-schemas.py` checks
  that 1,098 random mutations get the same verdict as the `jsonschema` library
  when it is installed.

- `route_task.py` and `context.py` write stdout as UTF-8. On native Windows,
  piping Thai routing output failed with a cp1252 `UnicodeEncodeError`. The
  Windows shared-runtime test now checks a Thai route through a pipe.

- Moved the router's bilingual vocabulary out of `scripts/route_task.py` into
  `config/routing-rules.json`. Priority, word boundaries, and combination logic
  stay in Python. Routing is unchanged: 4,998 requests in 3 project contexts
  gave output identical to before. `route_task.py --validate` (also run by
  `validate_prompt_catalog.py`) rejects malformed, duplicate, colliding,
  unregistered, or unused vocabulary. New `tests/test-routing-rules.py`.

- Installing the kit into its own source tree no longer appends the managed
  block to the canonical `AGENTS.md` or touches `CLAUDE.md`/`ANTIGRAVITY.md`.
  The check compares physical paths, so a symlinked path is also recognized.
  Bash and PowerShell behave the same, and normal project installs are
  unchanged.

## 7.7.1-windows-runtime-canary — 2026-09-25

- Fixed a shared-runtime defect found by the first native-Windows run. Without
  `PYTHONDONTWRITEBYTECODE`, `apk context` wrote `__pycache__` into the
  checksum-verified runtime, so every later `apk resolve` failed.
  `context.py` and the launcher now keep bytecode out of the runtime.
  Verification still rejects cache files, since a planted `.pyc` could
  bypass it, and the error now names the cache files and the fix.
- Native Windows shared-runtime v2 test passes with the Python install manager
  (`py`, Python 3.14).

- Routing fixes from a self-hosted v2 trial on this kit's own roadmap. File
  names such as `project.json` no longer match phrases like "new project".
  CI, GitHub Actions, JSON Schema, installer, PowerShell, wrapper, and source
  file names now signal software work. Software requests without a named
  output default to code. Bare "data" no longer selects data analytics in
  software work. Package releases count as software. Secret and credential
  checks attach the release-boundary gate.

- Corrected the benchmark fixture for official letters: drafting one must not
  select publication production, matching the routing contract test.
- Added `scripts/release_check.py`, one read-only release gate that checks
  version consistency across manifest/README/index/template/changelog, registry
  projections, the prompt catalog, the clean-tree and Git-history boundary, the
  full acceptance suite in parallel, and prints the shared-runtime content
  digest. `--tagged` also requires an annotated tag on HEAD.

## 7.7.0-workflow-architecture-canary — 2026-09-25

- Replaced the flat primary/secondary model with Workflow Architecture v2:
  one outcome owner plus bounded methods, lifecycle stages, quality gates, and
  state actions. The canonical registry now generates compatibility views.
- Corrected adversarial English/Thai routing, stage priority, ambiguity,
  project-state actions, Markdown state authority, and exact UTF-8 byte caps.
- Hardened shared runtime identity, binding path confinement, source-content
  drift detection, downgrade prevention, and transactional snapshot rollback.
- Made Bash installer updates same-filesystem atomic and permission-preserving;
  malformed markers, source symlinks, and transient caches now fail or stay out.
  Added equivalent PowerShell guards and the missing document-state templates.
- Added a public/private release boundary with dirty/untracked release gates,
  personal-path checks, forced `.env` blocking, broader token signatures, and
  fail-closed handling for large or non-UTF-8 release candidates.
- Reconciled dependency remediation: use the narrowest compatible shared or
  project-declared environment, respect explicit isolation/pinning contracts,
  inspect risky transactions, and require approval above 250 MB or for
  metered, GPU/CUDA, privileged, destructive, or uncertain changes.
- Corrected environment manifests: removed the non-standard `microconda` command,
  separated `ml-cuda118`, declared its PyTorch wheel index, and added PyMuPDF to
  the text baseline used by the book workflow.
- Made Git dry-runs use disposable clones, rejected failed fast-forward pulls,
  and replaced line-oriented JSON parsing with a real JSON parser.
- Reworked Markdown separator detection in the prose checker to avoid
  catastrophic backtracking and cover `***`, `___`, and spaced rules.
- Removed self-recursion from canonical `AGENTS.md`; APK doctor now treats the
  source root as authoritative over its downstream-package test snapshot.

## 7.6.0-prose-style-canary — 2026-09-25

- Added the Prose Style secondary workflow (`prompts/24_PROSE_STYLE.md`): write
  direct, evidence-backed prose and avoid formulaic AI-style patterns such as
  "not X, but Y", question-and-answer framing, slogan endings, signposting
  topic sentences, rhetorical bold, and dense semicolons, colons and dashes.
- Added `scripts/check_prose_style.py`, which counts those patterns in LaTeX,
  Markdown or text files, lists zero-tolerance hits by line, and flags rates
  above review thresholds.
- The router adds `prose-style` when a paper, book, document, course-material
  or policy request asks for writing, drafting, revising or polishing prose.

## 7.5.1-project-radar-canary — 2026-08-16

- Added an optional minimal Project Radar for cross-project status: one short
  row per active, waiting, blocked, or parked project, with a review date, one
  open loop, and one next action.
- Weekly review flags rows not reviewed for 14+ days so intentionally parked,
  blocked, and forgotten work are distinguished without duplicating project
  task lists, journals, calendars, time logs, or AI-use records.

## 7.5.0-book-writing-framework-canary — 2026-08-14

- Added reusable Book Writing profile contracts for book architecture, research
  integration, reference corpus, figure extraction, book graphics, and
  publication packaging.
- Added a user-visible profile/meta resolution report requirement with explicit
  `confirmed`, `inferred`, `N/A`, and `needs-user` states.
- Added reusable PDF reference extraction tools for bounded text/cache output,
  embedded raster images, and vector/full-page figure rendering.
- Added transactional updater infrastructure and clean benchmark evidence for
  selective context, cadence avoidance, and covered state-preservation safety.

## 7.4.0-transactional-update-canary — 2026-08-13

- Build and validate updates in a same-filesystem staging directory before
  switching the installed snapshot into place.
- Compare SHA-256 for every copied package file before allowing the snapshot
  switch.
- Retain the prior snapshot at `.ai/agent-project-kit.previous`; automatically
  restore it and installer-managed control files if a post-switch step fails.
- Treat missing package items as preflight failures instead of leaving a mixed
  or partial snapshot.
- Pin Pages-driven updates to the manifest `git_ref` and reject a checked-out
  ref whose package version differs from the advertised manifest version.
- Add Bash and PowerShell regression coverage for incomplete sources,
  successful swaps, post-switch failures, rollback cleanup, state preservation,
  exact-ref selection, and version-mismatch rejection.

## 7.3.0-book-writing-canary — 2026-08-13

- Added Book Writing as a full evidence-first primary route with a reusable,
  project-resolved profile and split validator; retained the complete sharp
  method rather than replacing it with an abbreviated generic prompt.
- Recast Document Production as the secondary Publication Production workflow
  for written/reflowable build, conversion, export, and final QA without
  imposing its fallback frame on book projects.
- Added Presentation Production as a secondary workflow with project-contract,
  master/layout, accessibility, media/motion, render/export, target-viewer, and
  final-artifact gates plus pipeline/style/QA templates.
- Production routing is lifecycle-sensitive: prose/story planning does not load
  production; real publication/deck creation, rendering, export, and final QA do.
- Fixed structured context so a presentation deliverable loads the Presentation
  primary even when its surrounding subject domain is education or governance.

## 7.2.3-shared-runtime-v2-canary — 2026-08-06

- Prepared shared-runtime binding schema v2 with separate synced package and
  machine-local homes through `APK_SHARED_ROOT` and `APK_MACHINE_HOME`.
- Kept `APK_HOME`/`--home` compatibility, added guarded project-binding
  rollback, and retained schema-v1 resolution during migration.
- Added temporary multi-machine, project-content leakage, read-only runtime,
  self-host source-preservation, and rollback acceptance coverage.
- Canonicalized aggregate checksum ordering by relative path so one shared
  artifact verifies consistently from WSL/Linux and native Windows.
- Documented Windows PowerShell recovery for WSL2/OneDrive long-path I/O errors.
- Added opt-in, idempotent POSIX shell configuration for shared/machine roots
  and launcher `PATH`, with existing rc content preserved.
- Made normal upgrades discover shared/machine paths from environment variables
  or the existing machine-local config instead of requiring repeated CLI paths.

- Added `scripts/repair_thai_wordbreak_docx.py` as the standard post-build
  finalizer for AI-generated Thai DOCX files.
- Documented explicit Thai complex-script and English proofing-language markup,
  mixed-run splitting, text-preservation checks, and Word visual QA.
- Applied repair across the document body, headers, footers, footnotes,
  endnotes, and comments rather than only the main document story.
- Corrected Thai runs to use `w:lang/@w:val="th-TH"` as well as Thai
  East-Asian/bidirectional metadata; Latin segments use `en-US`. This fixes the
  prior behavior where Word could still apply English space-only wrapping and
  proofing rules to Thai text.
- Added a mixed Thai/English regression test using a real clause-style sentence.
- Made Thai DOCX repair an explicit Agent Project Kit instruction in `AGENTS.md`,
  `START_HERE.md`, and the routed document-production prompt, including required
  invariant checks and pipeline/QA recording.
- Added downstream-install coverage so project snapshots receive the repair tool.

## 7.1-shared-runtime-canary — 2026-08-03

- Added a persisted 14-day update notice that checks only the published
  manifest, reports a newer version, and never installs automatically.
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
