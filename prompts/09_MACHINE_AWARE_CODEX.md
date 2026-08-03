# 09 — Machine Discovery / Revalidation (One-Time)

This is a conditional environment check, not a task route.

Run only when the current machine is missing/stale, the OS/path/storage layout
changed, or a heavy/resource-dependent task needs capability not already verified.

1. Read `.ai/MACHINE_PROFILE.md`, `.ai/LOCAL_RESOURCES.md`, and version metadata.
2. If the current host has a compatible entry less than 30 days old, verify only
   hostname, platform/path style, and task-required resource paths.
3. Otherwise inspect OS/WSL/container context, CPU, memory, storage pressure,
   accelerator, runtimes, and required non-portable resources.
4. Record stable facts and task suitability in `.ai/MACHINE_PROFILE.md`; record
   non-portable paths in `.ai/LOCAL_RESOURCES.md`.
5. Use `run-once.py --scope machine --ttl-days 30` for repeatable discovery.

Do not scan parent projects, reinstall runtimes, benchmark hardware, or run a
full pipeline unless the current task specifically requires it.
