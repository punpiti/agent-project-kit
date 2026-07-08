# 03 — Codex / Coding Agent Prompt

ใช้กับ Codex, IDE agent, coding agent, หรือ project ที่ต้องแก้โค้ด

```text
Use the Spec–Eval–Loop Workflow plus the WSL2/OneDrive machine-aware protocol for this coding task.

Before editing code:
1. Read AGENTS.md and .ai/computing-environment if present.
2. Read project-local state files if present:
   - .ai/PROJECT_STATE.md
   - .ai/LOCAL_RESOURCES.md
   - .ai/MACHINE_COMPATIBILITY.md
   - .ai/RUNBOOK.md
   - .ai/TOKEN_BUDGET.md
   - .ai/SESSION_LOG.md
3. Detect current machine using hostname if possible: think / madlab-i9 / black5 / unknown.
4. Detect whether running in WSL2 if possible.
5. Inspect the repository structure in a targeted way.
6. Identify the relevant files.
7. Summarize the current behavior.
8. Write a concise working spec for the requested change.
9. Define acceptance criteria and tests.
10. State assumptions clearly.
11. Check whether required local data/cache/intermediate resources exist before running heavy commands.

Storage / portability rules:
1. OneDrive files are portable; WSL-local/HDD/cache files are not.
2. Record all non-OneDrive resources in .ai/LOCAL_RESOURCES.md.
3. Do not hardcode machine-specific absolute paths into source code.
4. Prefer environment variables: PROJECT_DATA_ROOT, PROJECT_CACHE_ROOT, PROJECT_OUTPUT_ROOT.
5. Keep small portable smoke tests when feasible.

During implementation:
1. Make small, focused changes.
2. Prefer minimal changes that satisfy the spec.
3. Run relevant tests, scripts, lint, type checks, or smoke checks whenever possible.
4. Use smoke tests first if on black5 or if resource availability is uncertain.
5. If something fails, read the error, explain the likely cause, and fix it.
6. Do not delete or weaken tests just to pass.
7. Do not introduce large architectural changes unless necessary.
8. Avoid hardcoded paths, hidden global state, and undocumented magic numbers.
9. Do not run full heavy pipelines before checking machine suitability.

After implementation:
Report clearly:
- What changed
- Which files changed
- Which tests/checks were run
- Which tests passed or failed
- What was not tested
- Local resources used or missing
- Whether this machine is suitable for the task
- Remaining risks
- Decisions that require human judgment
- Suggestions for the next loop
- Token note: how to make the next session cheaper without reducing quality

After meaningful work, update or propose updates to:
- .ai/PROJECT_STATE.md
- .ai/SESSION_LOG.md
- .ai/LOCAL_RESOURCES.md if local paths/resources changed
- .ai/MACHINE_COMPATIBILITY.md if machine capability became clearer
- .ai/RUNBOOK.md if new commands were discovered

Treat this task as possibly involving:
L1 = code/build/test loop
L2 = human product/context judgment
L3 = external user/data feedback

Important:
Do not pretend L2 or L3 has been resolved by L1 alone.
Do not pretend a non-portable cache exists on every machine.
Do not declare the project broken just because the current machine lacks a local resource.
```
