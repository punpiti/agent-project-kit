# TOKEN_BUDGET

ใช้กำกับว่า project นี้ควรใช้ AI แบบไหนเพื่อไม่เปลือง token โดยยังรักษาคุณภาพ

## Default Mode

- Default token mode: T1 Standard
- Default cost profile: C1 Normal
- Use T0 for:
- Use T2 for:
- Use T3 for:

## Cost Profiles

| Profile | Meaning | Agent behavior |
|---|---|---|
| `C0 Economy` | User wants to save tokens/cost, uses a cheaper model, or has a tight quota | Ask before broad scans, long test loops, web research, or large rewrites |
| `C1 Normal` | Default balance | Do focused work; warn before obvious high-cost expansion |
| `C2 Premium` | User prioritizes completeness over token cost | Do necessary deep work without repeated cost prompts, but keep scope disciplined |

## Heavy-Work Consent Rule

If estimated token cost is `High` and cost profile is `C0 Economy` or unknown,
pause and offer:

1. `Economy`: read only core files and propose a plan.
2. `Standard`: implement the focused change and run smoke checks.
3. `Deep`: scan/test more broadly and update state/logs.

If the user explicitly says `ทำเลย`, `รันให้เลย`, `เอาให้จบ`, or equivalent,
continue with the narrowest mode that can finish the task safely.

## High-Value Context Files

ให้ AI อ่านไฟล์เหล่านี้ก่อน ไม่ต้อง scan ทั้ง project ทุกครั้ง:

1. `AGENTS.md`
2. `.ai/PROJECT_STATE.md`
3. `.ai/PROJECT_HIERARCHY.md`
4. `.ai/COMPUTING_ENVIRONMENT_VERSION.md`
5. `.ai/MACHINE_PROFILE.md`
6. `.ai/LOCAL_RESOURCES.md`
7. `.ai/RUNBOOK.md`

## Files Usually Relevant

| Task type | Read these first | Avoid reading unless needed |
|---|---|---|
| | | |

## Token-Saving Notes

- For known machines, run only the minimal resume check (`hostname`, platform, `pwd`) and reuse `.ai/MACHINE_PROFILE.md` instead of rescanning hardware/storage.
- If only the package version changed and machine profile schema is unchanged, update package metadata/snapshot without rerunning first-use discovery.
- For unknown machines, fill `.ai/MACHINE_PROFILE.md` once before heavy work.
- For nested folders, read `.ai/PROJECT_HIERARCHY.md` before deciding whether to load parent/child context.
- When a task starts looking like a broad agentic run, state the likely token cost and ask for confirmation if the user appears to be in `C0 Economy`.

## Compression Summary

สรุป project ใน 10–20 บรรทัด สำหรับ paste เข้า ChatGPT เมื่อ tool อ่านไฟล์ไม่ได้:

```text
[เติมสรุปสั้นของ project]
```
