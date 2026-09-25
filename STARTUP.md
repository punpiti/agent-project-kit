# Fast Startup Contract

This is the minimal startup path. Do not load the whole managed snapshot at
the beginning of every session.

## Read Every Session

1. Project `AGENTS.md`
2. `.ai/PROJECT_STATE.md`
3. This file

Stop there unless the current task triggers a conditional read.

## Route The Task Before Loading More Context

Classify the request first, then load only the matching route. If the request is
clear, state the route briefly and proceed. Do not ask the user to confirm an
obvious classification. If two interpretations would produce materially
different work, ask one concise question: what outcome should be produced?

| Primary task type | Load next | Typical action |
|---|---|---|
| Software Development & Automation | `prompts/19_SOFTWARE_DEVELOPMENT_AUTOMATION.md` | build/debug/test web, CLI, desktop, automation, and data-pipeline software |
| Research Activities | `prompts/13_RESEARCH_PROJECT_PROMPTS.md` | select literature, evidence, review, or research-planning mode |
| Book Writing | `prompts/22_BOOK_WRITING.md` + a resolved copy of `templates/BOOK_WRITING_PROFILE.md` | write from the full evidence-first method; infer profile values from the current book only, ask when unresolved, and validate with `scripts/check_book_writing_split.py` |
| Content Analysis | `prompts/15_CONTENT_ANALYSIS.md` | define corpus, coding frame, evidence, and interpretation |
| Data Analytics | `prompts/16_DATA_ANALYTICS.md` | validate data, analyze, visualize, and state decision implications |
| Presentation | `prompts/05_SLIDES_TEACHING.md` | define audience/outcome and build the story |
| Course Material Development | `prompts/17_COURSE_MATERIAL_DEVELOPMENT.md` | align outcomes, activities, assessment, and teaching assets |
| Educational Policy Development | `prompts/18_EDUCATIONAL_POLICY_DEVELOPMENT.md` | develop defensible, feasible policy and governance decisions |
| Administrative & Professional Operations | `prompts/20_ADMINISTRATIVE_PROFESSIONAL_OPERATIONS.md` | manage deadlines, compliance, correspondence, dossiers, and follow-up |

Choose Educational Policy Development when the requested deliverable is a
policy, regulation, governance decision, institutional proposal, standard, or
stakeholder-facing recommendation—even when research supplies its evidence.
Choose Research Activities when the deliverable is primarily a study, evidence
synthesis, analysis, or research output rather than an institutional decision.

Quick answers need no route file. For other work, use Workflow Architecture v2:

1. Select exactly one **primary pipeline** that owns the requested outcome.
2. Add bounded **method modules** such as Web Development, Data Analytics,
   Content Analysis, Research Synthesis, or Strategy only when needed.
3. Add the current **lifecycle stage** such as implementation, reviewer
   response, production, external feedback, Markdown cleanup, or package release.
4. Apply every triggered **quality gate**; gates do not compete with methods.
5. Run **state actions** such as resume, onboarding, or machine discovery only
   when project state requires them.

One orchestrator remains responsible for the final result. A module should be
separate only when its instructions, tools, evidence contract, or approval
boundary materially differs from the primary pipeline. Never drop a triggered
module silently; report any omitted module and the composition limit that caused
the omission.

Use Prose Style (`prompts/24_PROSE_STYLE.md`) as a quality gate whenever
reader-facing prose is drafted, revised, edited, or polished. It does not own
the deliverable and must not replace evidence, publication, or domain checks.

Use Publication Production (`prompts/10_DOCUMENT_PRODUCTION.md`) only when a
written/reflowable artifact must be built, converted, exported, or final-QA'd.
Use Presentation Production (`prompts/23_PRESENTATION_PRODUCTION.md`) only when
an actual deck must be created, edited, rendered, exported, or final-QA'd.
Planning book prose or a presentation storyline alone does not trigger either
production workflow.

Personal finance should use its project-local finance workflow rather than a
generic core route. Rare technical/DIY work uses a `Technical / Other Project`
fallback: identify the concrete outcome and load no broad prompt pack by default.

For mixed requests, choose one primary pipeline by requested deliverable. A
specialist method can become primary only when the deliverable itself is that
method's analysis. For example, survey analysis supports a policy pipeline;
dashboard analysis selects Data Analytics. Never load every prompt “just in
case.” Onboarding and discovery still obey the cadence below.

The machine-readable source of truth is `config/workflow-registry.json`.
`prompts/catalog.json`, `config/routes.json`, `config/workflows.json`, and
`config/policies.json` are generated compatibility views. Do not edit those
views directly; use `scripts/sync_workflow_registry.py --write`. Normal task
startup does not need to read the registry.

When deterministic routing is useful, run:

```bash
python3 .ai/agent-project-kit/scripts/context.py --project . "<request>"
```

The compiled bundle reports classification axes plus the primary pipeline,
methods, stages, gates, state actions, omissions, policies, sources, bytes, and
estimated tokens. Exit status 2 means the outcome is materially ambiguous and
one concise clarifying question is appropriate. Markdown routing remains the
compatibility fallback when the structured tool is unavailable.

## Always-On Policies

These apply to every task. Follow the linked section only when a policy is in
play and the one-line rule is not enough.

<!-- BEGIN GENERATED: always-on policies from config/workflow-registry.json -->
<!-- Edit config/workflow-registry.json, then run scripts/sync_workflow_registry.py --write. -->
- `evidence-boundary`: Do not make claims stronger than available evidence; distinguish observation, inference, judgment, and external validation. Details: `AGENTS.md` › Output Style.
- `loop-boundary`: Do not present L1 execution as resolution of L2 human judgment or L3 external feedback. Details: `AGENTS.md` › Core Loop Model.
- `context-minimization`: Load only context required by the current deliverable; do not scan files merely because they exist. Details: `STARTUP.md` › Read Only When Triggered; `TOKEN_DISCIPLINE.md` › Default Principle.
- `idempotent-checks`: Reuse successful valid discovery/check results; rerun only after expiry, relevant change, failure, or explicit request. Details: `STARTUP.md` › Check Cadence.
- `user-file-safety`: Preserve user-authored files and project-local state; do not overwrite or delete them implicitly. Details: `README.md` › Safety Model.
- `dependency-remediation`: When a task-required library is missing, select the project-declared environment or the narrowest text/image/ml environment, install and verify the smallest compatible direct dependency, and avoid cross-project conflicts. Honor explicit isolation or pinning contracts outside synced trees when practical. Announce ordinary repairs and proceed only at or below 250 MB without removal, replacement, or downgrade; otherwise inspect a supported dry run and obtain approval. Details: `AGENTS.md` › Conda-Family Environment Routing; `ENVIRONMENT_POLICY.md` › Demand-Driven Installation and Network Cost.
- `confidentiality-boundary`: Keep project-local state, private product intelligence, credentials, and restricted source material outside public package and trace surfaces unless explicitly approved. Details: `config/SECURITY_BOUNDARY.md` › Classification; `SECURITY_EXCLUSIONS.md` › Private product intelligence.
<!-- END GENERATED: always-on policies -->

## Read Only When Triggered

| Trigger | Read / run |
|---|---|
| Project boundary or parent/child scope is unclear | `.ai/PROJECT_HIERARCHY.md` |
| New/stale machine, heavy command, or missing local data | `.ai/MACHINE_PROFILE.md`, then `.ai/LOCAL_RESOURCES.md` |
| Required library/command is missing | select the project-declared shared environment or `text`/`image`/`ml`, install the smallest direct dependency there, then verify; do not create `.venv` |
| A command, setup step, or failure needs project knowledge | `.ai/RUNBOOK.md` |
| Package install, update, release, or schema work | `.ai/COMPUTING_ENVIRONMENT_VERSION.md` |
| Workflow architecture or routing changes | `config/WORKFLOW_ARCHITECTURE.md`, then the registry and scenario tests |
| Commit or package | run `scripts/check_release_boundary.py`; keep private product intelligence outside public paths |
| Tag or public release | run `scripts/check_release_boundary.py --release --history`; stop on untracked release candidates |
| Explicit token/cost concern or high-cost work | `.ai/TOKEN_BUDGET.md` |
| Document, slide, research, or Markdown-maintenance task | the relevant prompt/checklist only |
| Last state summary is insufficient | the newest relevant `.ai/SESSION_LOG.md` entry |

Do not read a file merely because it exists.

## Check Cadence

- Per session: read the three startup files and inspect task-relevant code.
- Once per project: bootstrap, hierarchy declaration, initial repository scan.
- Once per machine or after material change: machine discovery.
- Periodic: update check (14 days) and machine revalidation (30 days).
- Per task: tests, resource checks, and deeper policy only when triggered.

Use `scripts/run-once.py` for commands that must not repeat unnecessarily. It
records successful runs in `.ai/AGENT_PROJECT_KIT_STATE.json`; failed commands
are never marked complete.

At startup, run the lightweight update notice through the persisted cadence:

```bash
python3 .ai/agent-project-kit/scripts/run-once.py --project . \
  --key update-notice --ttl-days 14 --quiet-valid -- \
  python3 .ai/agent-project-kit/scripts/check-update-notice.py --project .
```

This command reads the published manifest, reports availability, and records
only check metadata/cadence in `.ai/`. It must never clone, pull, install, or
replace package or project content. A failed network check is not recorded and
may be retried in a later session. On Windows, use
`python` instead of `python3` when that is the configured Python command.

Run `python3 .ai/agent-project-kit/scripts/apk_doctor.py . --quick` when startup
state appears stale or contradictory, not automatically every session.
