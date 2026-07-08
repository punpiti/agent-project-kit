# AGENTS.md

This repository or project should be handled using the **Spec–Eval–Loop Workflow** plus the portable machine/profile protocol.

Package identity: Agent Project Kit (`agent-project-kit`). Legacy-compatible
folder/path name: `computing-environment`.

Before doing substantial work, read:

1. `START_HERE.md`
2. `SPEC_EVAL_LOOP_INSTRUCTION.md`
3. `MACHINE_PROFILES.md`
4. `TOKEN_DISCIPLINE.md`
5. Relevant files under `prompts/`, `templates/`, and `checklists/`

If these files are copied into a project under `.ai/computing-environment/`, read that folder first.

When this repository is Agent Project Kit itself, including the legacy
`computing-environment` folder, do not treat
`.ai/computing-environment/` as a second project to recurse into. The root-level
files are canonical; `.ai/computing-environment/` is only an installed snapshot
used to verify downstream packaging unless the user explicitly asks to inspect
that packaged copy.

---

## Core Loop Model

Classify every task into one or more loops:

- **L1 = Agentic Execution**  
  Code, test, debug, draft, summarize, analyze, generate, refactor.

- **L2 = Human Context / Developer Feedback**  
  Product direction, user context, tone, UX, academic judgment, institutional constraints, stakeholder risk.

- **L3 = External Feedback**  
  Reviewer feedback, student feedback, users, stakeholders, data, logs, surveys, experiments, deployment results.

Do not treat an L1 output as proof that L2 or L3 has been solved.

---

## Machine / Portability Protocol

Projects may be opened on macOS, Windows, Linux, WSL2, containers, remote
servers, or synced folders. Do not assume that local data/cache paths or runtime
environments exist on every machine.

At the start of non-trivial coding/data sessions:

1. Detect current machine if possible using `hostname`.
2. Detect whether running in WSL2 if possible.
3. Read project-local state files if they exist:
   - `.ai/PROJECT_STATE.md`
   - `.ai/PROJECT_HIERARCHY.md`
   - `.ai/COMPUTING_ENVIRONMENT_VERSION.md`
   - `.ai/MACHINE_PROFILE.md`
   - `.ai/LOCAL_RESOURCES.md`
   - `.ai/MACHINE_COMPATIBILITY.md`
   - `.ai/RUNBOOK.md`
   - `.ai/TOKEN_BUDGET.md`
   - `.ai/SESSION_LOG.md`
4. Read `.ai/PROJECT_HIERARCHY.md` to know whether this directory is a project, subproject, component, document package, data area, or plain subdirectory.
5. Read `.ai/COMPUTING_ENVIRONMENT_VERSION.md` to know installed package/schema versions.
6. If `.ai/MACHINE_PROFILE.md` has a fresh entry for the current machine and the machine-profile schema is unchanged, do only a minimal resume check before reusing it.
7. If the machine, OS, path style, sync/storage layout, or machine-profile schema is new or stale, update `.ai/MACHINE_PROFILE.md` before heavy work.
8. Check whether required local data/cache/intermediate files exist on this machine before running heavy commands.
9. If local resources are missing, do not declare the project broken. State what is missing and propose a light/smoke path, resource setup step, or compatible machine.
10. Do not hardcode machine-specific paths in source code. Use environment variables or config.
11. Record hierarchy declarations in `.ai/PROJECT_HIERARCHY.md`, machine identity/storage assumptions in `.ai/MACHINE_PROFILE.md`, and non-portable resources in `.ai/LOCAL_RESOURCES.md`.

---

## Required Workflow for Non-Trivial Tasks

1. **Loop Diagnosis**
2. **Working Spec**
3. **Evals / Acceptance Criteria**
4. **Execution**
5. **Review Gate**

Include local resource and machine suitability issues in the Review Gate when relevant.

For nested workspaces, do not infer that every subdirectory is a subproject.
Use `.ai/PROJECT_HIERARCHY.md` or another explicit marker. Parent projects may
read child summaries; child projects should only read parent summaries for broad
framing unless the task explicitly needs parent context.

Parent project files are a read-only interface for child projects by default.
When working from a child project, do not edit parent files, parent `.ai/` state,
parent session logs, parent resource manifests, or sibling projects unless the
user explicitly asks for a parent-level or cross-project change.

---

## Coding Rules

Before editing:

- Inspect repository structure.
- Identify relevant files.
- State the working spec.
- Define acceptance criteria and tests.
- State assumptions.
- Check project-local state and local resource manifests.

During implementation:

- Make small, focused changes.
- Prefer minimal edits that satisfy the spec.
- Run relevant tests, scripts, lint, type checks, or smoke checks whenever possible.
- Use smoke tests first if local cache/resource availability is uncertain.
- If a check fails, read the error and fix the cause.
- Do not delete or weaken tests to pass.
- Do not introduce broad architectural changes without explaining why.
- Avoid hardcoded paths, hidden global state, and undocumented magic numbers.

After implementation, report:

- Files changed
- What changed logically
- Tests/checks run
- Passing/failing results
- What was not tested
- Local resources used or missing
- Current machine suitability
- Remaining risks
- Decisions requiring human judgment
- Suggested next loop
- Token note for the next session

Update or propose updates to `.ai/PROJECT_STATE.md` and `.ai/SESSION_LOG.md` after meaningful work.

---

## Documentation / Paper Rules

When editing academic, proposal, policy, or technical documents:

- Identify whether the problem is language, logic, evidence, positioning, audience, or trust.
- Do not only polish wording if the argument is weak.
- Claims must not exceed evidence.
- Limitations should be honest but not self-destructive.
- Reviewer responses should answer the real concern, not only sound polite.
- For important revisions, create a mapping from concern to change to evidence.

---

## Slides / Teaching Rules

When creating slides or teaching material:

- Identify audience and learning outcome first.
- Prefer clear flow over dense content.
- Watch visual load.
- Use examples where possible.
- Make the intended takeaway explicit.
- Do not make slides merely pretty; make them teach or persuade.

---

## Policy / Governance Rules

When working on institutional documents, curriculum, governance, or executive communication:

- Identify stakeholder risks.
- Avoid wording that creates unnecessary attack surfaces.
- Check feasibility and defensibility.
- Separate ambition from evidence.
- Make implementation path and decision points clear.

---

## Token Discipline

Default mode is `T1 Standard`.

- Use `T0 Quick` for small edits or direct answers.
- Use `T2 Deep` for reviewer, architecture, research, policy, or hard bug analysis.
- Use `T3 Agentic Run` for coding loops with tests.

Cost profile defaults to `C1 Normal`.

- Use `C0 Economy` when the user mentions token/cost pressure, appears to be on a cheap/limited model, or asks for a minimal pass.
- Use `C1 Normal` for balanced focused work.
- Use `C2 Premium` when the user explicitly prioritizes completeness or is already using a high-capacity setup.

Before high-cost work such as broad repo scans, long web research, full builds,
large rewrites, or repeated test/debug loops, state the expected token cost. If
the profile is `C0 Economy` or unclear, ask whether the user wants Economy,
Standard, or Deep mode. If the user explicitly says to proceed, continue with the
narrowest mode that can finish safely.

If the user is spending tokens inefficiently, say so directly and suggest a cheaper context strategy. Do not reduce quality by skipping evals/tests/review gates.

---

## Output Style

Be direct. Do not flatter.  
Be explicit about uncertainty, assumptions, missing tests, missing local resources, and missing external feedback.


## Document Production Addendum

For document-producing work, also read:

- `DOCUMENT_PRODUCTION_POLICY.md`
- `checklists/DOCUMENT_CHECKLIST.md`
- `prompts/10_DOCUMENT_PRODUCTION.md`
- `templates/DOCUMENT_PIPELINE.md`
- `templates/DOCUMENT_STYLE.md`
- `templates/DOCUMENT_QA.md`

Default document workflow: Markdown first, content critique/revision second, final PDF/build last. Formal Thai documents use TH Sarabun New for Thai text; public documents use modern minimal readable fonts. Paper output defaults to A4; screen output defaults to 16:9. Final PDFs must pass table, Thai word-break, spelling, hanging title, and hanging line checks before being called final.

<!-- BEGIN COMPUTING-ENVIRONMENT -->

## Agent Project Kit Rules

Self-hosting guard: this repository is the canonical Agent Project Kit source,
using the legacy-compatible `computing-environment` path. For normal work here,
read root-level governance files and root `.ai/` state files. Do not recurse into
`.ai/computing-environment/` unless the task is specifically about the packaged
downstream copy.

Before working on this project, read:

- `.ai/computing-environment/START_HERE.md`
- `.ai/computing-environment/SPEC_EVAL_LOOP_INSTRUCTION.md`
- `.ai/computing-environment/AGENTS.md`
- `.ai/computing-environment/MACHINE_PROFILES.md`
- `.ai/computing-environment/TOKEN_DISCIPLINE.md`
- `.ai/computing-environment/DOCUMENT_PRODUCTION_POLICY.md`
- `.ai/computing-environment/MARKDOWN_ORGANIZATION_POLICY.md`
- `.ai/computing-environment/ENVIRONMENT_POLICY.md`
- `.ai/computing-environment/MARKDOWN_ORGANIZATION_POLICY.md`
- `.ai/PROJECT_STATE.md`
- `.ai/PROJECT_HIERARCHY.md`
- `.ai/COMPUTING_ENVIRONMENT_VERSION.md`
- `.ai/MACHINE_PROFILE.md`
- `.ai/LOCAL_RESOURCES.md`
- `.ai/MACHINE_COMPATIBILITY.md`
- `.ai/RUNBOOK.md`
- `.ai/TOKEN_BUDGET.md`

Use Spec–Eval–Loop Workflow, check project hierarchy and installed package/schema version before rerunning discovery, record machine identity/storage assumptions, record non-portable local resources, and keep AI Markdown in the `.ai/` pipeline.
Do not pretend L2/L3 or non-portable resources are solved by L1 alone.

<!-- END COMPUTING-ENVIRONMENT -->
