# Shared Runtime Canary

This is an opt-in experiment. The existing per-project managed snapshot remains
the default and must not be removed during the canary.

## Safety Boundaries

- No downstream project is migrated automatically.
- No `.ai/agent-project-kit/` snapshot is deleted.
- Shared versions are immutable and installed side by side.
- Projects pin an exact version in `.ai/apk.json`.
- Projects pin the installed package content SHA-256 outside the shared runtime.
- Missing/mismatched runtimes fail explicitly; they do not silently use another version.
- Rollback is deleting `.ai/apk.json`; the existing snapshot path continues to work.

## Canary Commands

```bash
python3 scripts/install-shared.py \
  --shared-root /path/to/synced/agent-project-kit \
  --machine-home /path/to/machine-local/agent-project-kit \
  --bind-project /path/to/canary-project
python3 scripts/apk.py --project /path/to/canary-project resolve
python3 scripts/apk.py --project /path/to/canary-project context "<request>"
python3 scripts/apk.py --project /path/to/canary-project rollback
```

`APK_SHARED_ROOT` locates immutable generic package versions.
`APK_MACHINE_HOME` locates the disposable launcher/config/cache area for the
current machine. `APK_HOME` and `--home` remain compatibility aliases during the
schema-v1 migration window.

## Promotion Gates

Do not change the default installer until all are true:

1. Temp-directory acceptance tests pass on Linux/WSL and native Windows.
2. At least two real projects run shared context for several sessions.
3. Route/context output matches snapshot behavior.
4. Missing-runtime and wrong-version failures are understandable and safe.
5. Rollback to the project snapshot is tested.
6. Project-specific prompts remain project-local.
7. Content tampering fails before shared code is invoked.
