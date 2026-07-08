# ANTIGRAVITY.md

This project uses Agent Project Kit.

Read these first:

1. `AGENTS.md`
2. `.ai/PROJECT_STATE.md`
3. `.ai/PROJECT_HIERARCHY.md`
4. `.ai/COMPUTING_ENVIRONMENT_VERSION.md`
5. `.ai/MACHINE_PROFILE.md`
6. `.ai/LOCAL_RESOURCES.md`
7. `.ai/MACHINE_COMPATIBILITY.md`
8. `.ai/RUNBOOK.md`
9. `.ai/TOKEN_BUDGET.md`

Follow the Spec-Eval-Loop workflow and machine-aware protocol in `AGENTS.md`.

Before running terminal commands or making broad edits, check machine suitability
and project hierarchy. Parent project files are read-only from child projects
unless explicitly asked for a parent-level or cross-project change.

Do not overwrite project-local `.ai/` state when updating Agent Project Kit.

<!-- BEGIN AGENT-PROJECT-KIT-ADAPTER -->
Agent Project Kit adapter: read `AGENTS.md` and project-local `.ai/` state
before acting. Do not overwrite project-local `.ai/` state when updating the
kit.
<!-- END AGENT-PROJECT-KIT-ADAPTER -->
