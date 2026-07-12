# Update An Existing Project

Use this when a project already has Agent Project Kit installed and you want to
refresh it to a newer package version.

The update should refresh package files, not erase project memory. Treat the
target project's root `.ai/` files as project-local state.

## What Must Be Preserved

The installer may replace the package snapshot under:

```text
.ai/computing-environment/
```

It must preserve existing project-local files such as:

```text
.ai/PROJECT_STATE.md
.ai/PROJECT_HIERARCHY.md
.ai/MACHINE_PROFILE.md
.ai/LOCAL_RESOURCES.md
.ai/MACHINE_COMPATIBILITY.md
.ai/RUNBOOK.md
.ai/TOKEN_BUDGET.md
.ai/SESSION_LOG.md
```

`.ai/COMPUTING_ENVIRONMENT_VERSION.md` is package metadata and is expected to be
rewritten on update. It records the previous package version and schema version.

## Recommended Update Loop

1. Read the current version.

```bash
sed -n '1,80p' .ai/COMPUTING_ENVIRONMENT_VERSION.md
```

2. Confirm the current project state is worth preserving.

```bash
test -f .ai/PROJECT_STATE.md && sed -n '1,80p' .ai/PROJECT_STATE.md
test -f .ai/MACHINE_PROFILE.md && sed -n '1,80p' .ai/MACHINE_PROFILE.md
```

3. Preview the update.

```bash
bash .ai/agent-project-kit/scripts/install-from-git.sh --dry-run . https://github.com/punpiti/agent-project-kit.git main
```

For WSL2 projects under a Windows-synced folder, use a WSL-local kit cache:

```bash
KIT="${XDG_CACHE_HOME:-$HOME/.cache}/agent-project-kit"
bash "$KIT/scripts/install-from-git.sh" --dry-run . https://github.com/punpiti/agent-project-kit.git main
```

4. Apply the update.

```bash
bash .ai/agent-project-kit/scripts/install-from-git.sh . https://github.com/punpiti/agent-project-kit.git main
```

For WSL2 with a Windows-synced project folder:

```bash
KIT="${XDG_CACHE_HOME:-$HOME/.cache}/agent-project-kit"
bash "$KIT/scripts/install-from-git.sh" . https://github.com/punpiti/agent-project-kit.git main
```

5. Verify the result.

```bash
sed -n '1,120p' .ai/COMPUTING_ENVIRONMENT_VERSION.md
test -f .ai/PROJECT_STATE.md
test -f .ai/MACHINE_PROFILE.md
test -f AGENTS.md
```

6. Ask the agent to resume from the updated package.

```text
Read AGENTS.md and .ai/COMPUTING_ENVIRONMENT_VERSION.md.
Report the installed Agent Project Kit version, previous version, state schema,
and machine profile schema. Then read .ai/PROJECT_STATE.md and continue from
the current project state without rescanning broadly.
```

## Schema Decision

Use `.ai/COMPUTING_ENVIRONMENT_VERSION.md` after the update:

- If only `Package version` changed, reuse existing `.ai/` state.
- If `Machine profile schema version` changed, update missing machine-profile
  fields without deleting existing machine notes.
- If `State schema version` changed, compare templates in
  `.ai/computing-environment/templates/` and add missing fields to project-local
  files while preserving their content.
- If hostname, OS, path style, or storage layout changed, refresh
  `.ai/MACHINE_PROFILE.md` before heavy work.

## Rollback

Pinned tags are better than `main` when you need repeatability.

```bash
bash .ai/agent-project-kit/scripts/install-from-git.sh . https://github.com/punpiti/agent-project-kit.git v6.27.0
```

If the project keeps `.ai/` out of git, rollback depends on the previous package
tag and preserved project-local state. Do not delete `.ai/PROJECT_STATE.md`,
`.ai/MACHINE_PROFILE.md`, or `.ai/LOCAL_RESOURCES.md` as part of rollback.

## Trial Checklist

- The dry run reports current and target package versions.
- The dry run reports whether state or machine-profile schema changes.
- The real update rewrites `.ai/computing-environment/`.
- Existing project-local state files are still present after update.
- `.ai/COMPUTING_ENVIRONMENT_VERSION.md` records previous and current versions.
- `.ai/SESSION_LOG.md` has an update entry.
- The next agent session can report the installed version before starting work.
