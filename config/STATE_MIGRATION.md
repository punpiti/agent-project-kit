# Legacy State Migration Contract

Agent Project Kit keeps project state in three files. This contract says which
one wins and how the legacy file is retired.

## Authority

1. `.ai/PROJECT_STATE.md` is the authoritative current narrative. Humans and
   agents update it after meaningful work.
2. `.ai/project.json` holds identity and configuration only (name, domain,
   owner, objective, hierarchy). It never overrides the Markdown narrative.
3. `.ai/state.json` is legacy. `scripts/context.py` reads it only when
   `PROJECT_STATE.md` is absent. When both exist, the JSON is ignored, which
   hides any state that was only recorded there. `apk_doctor.py` warns about
   this case.

Schemas: `config/schemas/project.schema.json` and
`config/schemas/legacy-state.schema.json`.

## Migration

Run from the project root:

```bash
python3 .ai/agent-project-kit/scripts/migrate_state.py --project .           # dry run
python3 .ai/agent-project-kit/scripts/migrate_state.py --project . --write   # apply
```

- Migration never happens automatically. Install and update do not run it.
- The dry run is the default and changes nothing. It prints the exact section
  that `--write` would append.
- `--write` appends one section, delimited by
  `<!-- BEGIN MIGRATED LEGACY STATE sha256=… -->` and
  `<!-- END MIGRATED LEGACY STATE -->`, to the end of `PROJECT_STATE.md`
  (creating the file when absent). Existing Markdown is never rewritten or
  merged. A person moves still-current items into the main sections.
- `state.json` is then renamed to `state.json.migrated-YYYYMMDD`. Nothing is
  deleted, and every field is kept, including unknown keys.
- A second run is a no-op. If the same `state.json` is restored, the recorded
  digest identifies it as already migrated.
- A placeholder `state.json` holds no state. `--write --retire-placeholder`
  renames it the same way.
- Installers do not recreate `state.json` once a `state.json.migrated-*`
  backup exists.

The command refuses and changes nothing when `state.json` is not a regular
file, is not UTF-8 JSON, fails the legacy schema, or when today's backup name
already exists.

## Rollback

Rename `state.json.migrated-YYYYMMDD` back to `state.json` and delete the
delimited section from `PROJECT_STATE.md`. No other file is touched by the
migration.

## Not yet decided

New installs still create a placeholder `state.json` for compatibility with
older tooling. Whether to stop creating it is an owner decision for a later
release, after downstream projects have migrated.
