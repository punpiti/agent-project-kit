# AI Client Adapters

Agent Project Kit keeps one canonical project protocol and exposes thin adapter
files for different AI coding tools.

Canonical files:

- `AGENTS.md`
- `.ai/PROJECT_STATE.md`
- `.ai/PROJECT_HIERARCHY.md`
- `.ai/COMPUTING_ENVIRONMENT_VERSION.md`
- `.ai/MACHINE_PROFILE.md`
- `.ai/LOCAL_RESOURCES.md`
- `.ai/MACHINE_COMPATIBILITY.md`
- `.ai/RUNBOOK.md`
- `.ai/TOKEN_BUDGET.md`

## Supported Adapters

| Tool / client | Adapter file | Role |
|---|---|---|
| Codex / generic agents | `AGENTS.md` | Main rules and workflow |
| Claude Code | `CLAUDE.md` | Thin pointer into Agent Project Kit |
| Google Antigravity / agent IDEs | `ANTIGRAVITY.md` | Thin pointer into Agent Project Kit |

## Adapter Rule

Adapter files should stay short. They should point the tool to `AGENTS.md` and
the `.ai/` state files instead of duplicating the full policy. This avoids drift.

If a tool has its own preferred rule system, keep the tool-specific file as an
adapter and keep the real project policy in Agent Project Kit state files.

## Safety

All adapters must preserve the same core rules:

- Do not overwrite project-local `.ai/` state during package updates.
- Read `.ai/PROJECT_HIERARCHY.md` before loading parent/child context.
- Treat parent project files as read-only from a child project unless explicitly
  asked for a parent-level or cross-project change.
- Record non-portable resources in `.ai/LOCAL_RESOURCES.md`.
- Record machine identity/storage assumptions in `.ai/MACHINE_PROFILE.md`.
- Do not claim L2/L3 work is solved by L1 execution.
