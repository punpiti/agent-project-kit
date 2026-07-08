# 09 — Machine-Aware Codex Prompt

ใช้กับ Codex ใน WSL2 เมื่อ project มีข้อมูล/cache/intermediate ใหญ่หรือทำงานข้ามหลายเครื่อง

```text
Use the Spec–Eval–Loop Workflow and the machine-aware machine-aware protocol.

Before editing or running heavy commands:
1. Read AGENTS.md and .ai/computing-environment if present.
2. Read:
   - .ai/PROJECT_STATE.md
   - .ai/PROJECT_HIERARCHY.md
   - .ai/COMPUTING_ENVIRONMENT_VERSION.md
   - .ai/MACHINE_PROFILE.md
   - .ai/LOCAL_RESOURCES.md
   - .ai/MACHINE_COMPATIBILITY.md
   - .ai/RUNBOOK.md
   - .ai/TOKEN_BUDGET.md
3. Detect current machine using hostname if possible.
4. Detect whether this is WSL2 if possible.
5. If this machine already has a fresh profile in .ai/MACHINE_PROFILE.md and the
   machine profile schema in .ai/COMPUTING_ENVIRONMENT_VERSION.md is unchanged,
   do only a minimal resume check: hostname, platform, current path style, and
   required task-local paths.
6. If this is a new/stale machine or the project is on Windows-native, macOS,
   Linux server, container, or a non-shared/synced project storage sync folder, do first-use discovery
   and update .ai/MACHINE_PROFILE.md before heavy work.
7. Check whether required local resources exist.
8. State whether this machine is suitable for the requested task.

Nested project rule:
- A child project may read parent project summaries as a read-only interface.
- Do not edit parent files, parent .ai state, parent logs, parent resource
  manifests, or sibling projects unless explicitly asked for a parent-level or
  cross-project change.

Storage rules:
- shared/synced project storage-synced files are portable.
- Files outside shared/synced project storage are non-portable and must be recorded in .ai/LOCAL_RESOURCES.md.
- Machine identity and storage assumptions must be recorded in .ai/MACHINE_PROFILE.md.
- Installed package and schema versions are recorded in .ai/COMPUTING_ENVIRONMENT_VERSION.md.
- Do not hardcode machine-specific absolute paths into source code.
- Prefer environment variables such as PROJECT_DATA_ROOT, PROJECT_CACHE_ROOT, PROJECT_OUTPUT_ROOT.
- Keep small sample/smoke-test data portable when feasible.

Execution rules:
- Use the smallest test that proves the change first.
- Do not run full heavy pipelines unless the current machine is suitable.
- If local resources are missing, explain what is missing and suggest: smoke test, regenerate cache, set env var, mount HDD, or run on primary-heavy.

After work:
- Report files changed.
- Report tests/checks run.
- Report local resources used.
- Update or propose updates to .ai/PROJECT_STATE.md, .ai/LOCAL_RESOURCES.md, .ai/MACHINE_COMPATIBILITY.md, and .ai/SESSION_LOG.md.
- Do not rerun first-use discovery just because the package version changed; rerun only when machine profile schema or actual machine/path identity changed.
- Include a token note if the next session can be made cheaper.

Important:
Do not pretend a project is broken just because this machine lacks a non-portable cache.
Do not pretend L2 or L3 has been solved by L1 alone.
```
