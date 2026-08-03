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

Quick answers need no route file. Web development is a subtype of Software
Development & Automation and may load `14_WEB_DEVELOPMENT.md` secondarily.
Project resume, onboarding, reviewer response, document production, external
feedback, Markdown cleanup, package release, and Strategy & Advisory
(`21_STRATEGY_ADVISORY.md`) are secondary workflows: load one only when that
activity is explicitly needed inside a primary route.

Personal finance should use its project-local finance workflow rather than a
generic core route. Rare technical/DIY work uses a `Technical / Other Project`
fallback: identify the concrete outcome and load no broad prompt pack by default.

For mixed requests, choose one primary route based on the requested deliverable
and add only one secondary workflow when necessary. Never load every prompt pack
“just in case.” Classification itself is per request; onboarding and discovery
actions inside a route must still obey the check cadence below.

The machine-readable source of truth for prompt role, trigger, and cadence is
`prompts/catalog.json`. Normal task startup does not need to read the catalog;
it exists for validation, maintenance, and ambiguous routing audits.

When deterministic routing is useful, run:

```bash
python3 .ai/agent-project-kit/scripts/context.py --project . "<request>"
```

The compiled bundle reports four independent axes (`domain`, `deliverable`,
`methods`, `lifecycle`), selected modules/policies, sources, bytes, and estimated
tokens. Exit status 2 means the outcome is materially ambiguous and one concise
clarifying question is appropriate. Markdown routing remains the compatibility
fallback when the structured tool is unavailable.

## Read Only When Triggered

| Trigger | Read / run |
|---|---|
| Project boundary or parent/child scope is unclear | `.ai/PROJECT_HIERARCHY.md` |
| New/stale machine, heavy command, or missing local data | `.ai/MACHINE_PROFILE.md`, then `.ai/LOCAL_RESOURCES.md` |
| A command, setup step, or failure needs project knowledge | `.ai/RUNBOOK.md` |
| Package install, update, release, or schema work | `.ai/COMPUTING_ENVIRONMENT_VERSION.md` |
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
