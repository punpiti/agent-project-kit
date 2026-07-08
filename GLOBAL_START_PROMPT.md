# GLOBAL_START_PROMPT

Use this prompt when starting an AI session in a project that has Agent Project
Kit installed.

## General

```text
Read AGENTS.md and .ai/computing-environment first.

Then read these project-local state files if they exist:
- .ai/PROJECT_STATE.md
- .ai/PROJECT_HIERARCHY.md
- .ai/COMPUTING_ENVIRONMENT_VERSION.md
- .ai/MACHINE_PROFILE.md
- .ai/LOCAL_RESOURCES.md
- .ai/MACHINE_COMPATIBILITY.md
- .ai/RUNBOOK.md
- .ai/TOKEN_BUDGET.md
- .ai/SESSION_LOG.md

Use the Spec-Eval-Loop workflow:
1. Loop Diagnosis
2. Working Spec
3. Evals / Acceptance Criteria
4. Execution
5. Review Gate

Before heavy work, identify the current machine, storage/path assumptions,
missing local resources, and token/cost mode.

Do not claim L2 human judgment, L3 external feedback, or machine-local resource
availability has been solved by L1 agent execution alone.
```

## Cost-Sensitive

```text
Use C0 Economy unless I say otherwise.
If the task looks high-cost, ask me to choose:
1. Economy: read only core files and propose a plan.
2. Standard: implement the focused change and run smoke checks.
3. Deep: scan/test more broadly and update state/logs.
```

## After Meaningful Work

```text
Update or propose updates to:
- .ai/PROJECT_STATE.md
- .ai/SESSION_LOG.md
- .ai/LOCAL_RESOURCES.md, if new machine-local paths were discovered
- .ai/MACHINE_PROFILE.md, if the machine/storage profile changed
```
