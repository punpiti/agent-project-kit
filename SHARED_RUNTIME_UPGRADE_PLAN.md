# Shared Runtime Upgrade Plan

Status: implementation preparation complete; real self-host migration pending
Scope: upgrade the existing `7.1-shared-runtime-canary` without migrating
project content into the shared installation
Primary route: Software Development & Automation
Secondary workflow: Strategy & Advisory

## 1. Decision and objective

Upgrade Agent Project Kit from an opt-in, per-machine shared-runtime canary to a
multi-machine architecture with explicit ownership boundaries:

1. Generic, versioned Agent Project Kit package content may be installed once
   in a shared location that several machines can read.
2. Machine-local launchers, caches, environments, credentials, and locks stay
   outside the shared package.
3. Every item that describes, configures, or records a project stays in that
   project's workspace.
4. Agent Project Kit's own source workspace is the first real upgrade target;
   it must retain an explicit source version, a recoverable Git revision/tag,
   and installed immutable versions for self-host testing.

The upgrade must not require moving project state out of the project, deleting
existing snapshots, or making a synced folder responsible for machine-specific
execution state.

## 2. Loop diagnosis

- **L1 — implementation:** define schemas, resolver precedence, installers,
  migration commands, tests, and documentation.
- **L2 — owner decision:** approve the preferred cross-machine shared location
  and decide when the canary has enough real use to become the default.
- **L3 — external evidence:** validate on WSL2, native Windows, and at least one
  additional machine; observe real sessions in the two existing canary projects.
- **Portability layer:** treat OneDrive as synced distribution/storage, not as a
  safe location for mutable caches, virtual environments, credentials, or locks.

## 3. Ownership boundary

### Shared generic package

The shared package may contain only reusable Agent Project Kit assets:

- generic scripts and command entry points;
- generic prompts, templates, checklists, and configuration;
- package manifest, version, checksums, and package documentation;
- immutable version directories.

It must not contain project names, project paths, project state, session logs,
project prompts, project resource paths, user content, secrets, or mutable
per-project indexes.

### Machine-local state

Each machine may keep the following under a machine-local application-data
directory:

- a small launcher or adapter;
- interpreter/virtual environment and dependency cache;
- lock files and temporary files;
- last verification result for shared package versions;
- credentials, if a future feature needs them;
- an optional cache of the immutable shared package for offline use.

This state must be disposable and reconstructable. It must not be the only copy
of project state.

### Project workspace

The project workspace remains authoritative for:

- `AGENTS.md` and client adapters;
- `.ai/apk.json` package binding;
- `.ai/PROJECT_STATE.md`, `.ai/PROJECT_HIERARCHY.md`, and `.ai/SESSION_LOG.md`;
- `.ai/MACHINE_PROFILE.md`, `.ai/LOCAL_RESOURCES.md`, and
  `.ai/MACHINE_COMPATIBILITY.md` when they express this project's observed
  compatibility and non-portable dependencies;
- project-local prompts, runbooks, document state, token policy, and overrides.

`MACHINE_PROFILE.md` and `LOCAL_RESOURCES.md` may include system facts, but their
current role is project-scoped: they record whether this project can run on a
machine and where this project's non-portable resources are found. A future
machine registry may reduce duplication, but project requirements and overrides
must remain in the workspace.

## 4. Target architecture

```text
Synced/shared package root (read-only during normal use)
└── agent-project-kit/
    └── versions/
        └── <version>/
            ├── manifest.json
            ├── PACKAGE_CHECKSUMS.json
            ├── scripts/
            ├── prompts/
            ├── templates/
            └── checklists/

Machine-local application data
└── agent-project-kit/
    ├── bin/apk
    ├── cache/
    ├── locks/
    └── verified/<version>.json

Project workspace
├── AGENTS.md
└── .ai/
    ├── apk.json
    ├── PROJECT_STATE.md
    ├── MACHINE_PROFILE.md
    ├── LOCAL_RESOURCES.md
    ├── SESSION_LOG.md
    └── prompts/
```

The resolver reads the project binding, locates an exact immutable shared
version, verifies its digest, and then loads project-local context. It must not
write to the shared package during resolve or context compilation.

### Version identity and self-hosting

Agent Project Kit keeps three related but distinct version identities:

1. **Source version:** `manifest.json`, package metadata, changelog, and a Git
   commit/tag identify the version being developed in this repository.
2. **Installed version:** each immutable directory under `versions/<version>/`
   is a verified build installed from a particular source version.
3. **Project binding version:** `.ai/apk.json` identifies the installed version
   that a workspace is exercising.

For the Agent Project Kit repository itself, root source files remain canonical.
The self-host binding is used to test the installed runtime, not to redefine the
root as a downstream snapshot or recurse into `.ai/agent-project-kit/`.

## 5. Configuration and resolution

Introduce two distinct locations instead of overloading `APK_HOME`:

- `APK_SHARED_ROOT`: optional synced/read-only generic package root;
- `APK_MACHINE_HOME`: machine-local launcher, cache, verification, and locks.

Keep `APK_HOME` temporarily as a compatibility alias with a deprecation notice.
Resolution precedence should be deterministic:

1. explicit CLI argument;
2. `APK_SHARED_ROOT`;
3. a machine-local configuration file pointing to the shared root;
4. existing `APK_HOME` compatibility behavior;
5. project snapshot fallback, only when the project has no active shared binding
   or when an explicit rollback command disables it.

Do not silently substitute a different shared version when an exact project
binding exists. A missing, modified, or mismatched version must fail with a
repair or rollback command.

## 6. Project binding schema v2

Evolve `.ai/apk.json` without storing an absolute shared path:

```json
{
  "schema_version": 2,
  "package": "agent-project-kit",
  "version": "<exact-version>",
  "version_policy": "exact",
  "content_sha256": "<aggregate-digest>",
  "profile": "standard",
  "local_prompt_dirs": [".ai/prompts"],
  "runtime_mode": "shared-with-snapshot-fallback"
}
```

The binding describes requirements, not physical installation paths. Therefore
the same committed/synced binding works on every machine while each machine
resolves its own configured shared root.

## 7. Upgrade phases

### Phase 0 — freeze and inventory

- Finish or isolate the current uncommitted Thai DOCX changes.
- Record the current canary version, digest, bindings, and fallback snapshots.
- Confirm that the two existing canaries still resolve and can roll back.
- Do not add new canary projects during this phase.

Exit gate: a trustworthy Git recovery point and a reproducible baseline test
result exist.

### Phase 1 — boundary and schema

- Add explicit ownership policy to package documentation.
- Add binding schema v2 while continuing to read schema v1.
- Split shared-root configuration from machine-local state.
- Ensure context compilation reads project-local prompts and state from the
  workspace, never from the shared package.

Exit gate: unit tests prove that no generated shared-runtime file contains the
test project's name, path, state, or prompt content.

### Phase 2 — installers and resolver

- Make shared installation transactional and immutable.
- Add a machine-local configuration/launcher setup command.
- Add `bind`, `resolve`, `doctor`, `rollback`, and `uninstall-version` flows.
- Refuse to delete a version still referenced by known bindings when that can be
  determined safely; otherwise require an explicit destructive confirmation.
- Preserve the current per-project installer and snapshot fallback.

Exit gate: interrupted installation leaves either the previous valid version or
no new version, never a partially active runtime.

### Phase 3 — migration canary

- Make the Agent Project Kit source repository the first real schema-v2 canary.
  Test its installed immutable version while preserving root source as canonical.
- Verify source version, installed manifest/digest, project binding, Git recovery
  revision, and self-host non-recursion before touching downstream projects.
- After the self-host gate passes, upgrade only `media_importer` and `ipst/ai`
  bindings to schema v2.
- Test from at least two machines using the same synced generic package root.
- Verify that each machine may use a different machine-local home.
- Run normal sessions and record routing correctness, startup latency, sync
  conflicts, and fallback behavior.

Exit gate: several real sessions complete without project-content leakage,
runtime mutation, unexplained resolver failure, or OneDrive conflict files.

The self-host canary must pass before either downstream canary is upgraded.

### Phase 4 — cross-platform acceptance

- Run Linux/WSL2 acceptance tests.
- Run native Windows PowerShell installation, resolution, context, and rollback.
- Test path aliases, spaces, Unicode paths, unavailable network/sync root, stale
  placeholders, and concurrent read access.
- Test one machine offline using either the existing project snapshot or an
  explicitly supported machine-local package cache.

Exit gate: all platform tests pass and the failure messages prescribe safe next
actions.

### Phase 5 — release and gradual adoption

- Bump package and schema versions; update manifest and changelog.
- Publish an upgrade guide and an explicit rollback guide.
- Keep migration opt-in for protected or high-risk projects.
- Expand in small batches only after checking the previous batch.
- Retain project snapshots until the owner approves a later cleanup policy.

Exit gate: release artifacts, public manifest, recovery tag, and downstream
install tests agree on version and schema.

## 8. Migration procedure per project

1. Read the project's state, hierarchy, compatibility, and current package
   version.
2. Verify or refresh its local snapshot before changing the binding.
3. Back up only the binding and installer metadata; do not copy project content
   into the runtime.
4. Generate schema-v2 `.ai/apk.json` with exact version and digest.
5. Resolve and run one representative context request.
6. Temporarily disable the binding and test snapshot fallback.
7. Restore the binding and record the result in the project's session log.
8. Stop and roll back on any unexplained routing difference or missing resource.

Bulk migration is not allowed until the canary promotion gates pass.

For the Agent Project Kit repository, perform an additional preflight before
step 1: commit the intended source, create or verify a recovery tag, build the
immutable runtime from that exact revision, and prove that removing the
self-host binding returns operation to root-canonical source behavior.

## 9. Rollback

Rollback must be project-local and reversible:

- disable or rename `.ai/apk.json` through a guarded command;
- use the preserved `.ai/agent-project-kit/` project snapshot;
- leave the shared runtime untouched for other projects;
- restore the binding only after shared resolution and checksum verification
  pass again.

No rollback command may delete project state, project prompts, or content. Shared
version cleanup is a separate maintenance operation.

## 10. Acceptance criteria

### Ownership and privacy

- Shared runtime contains no project content, state, absolute project paths,
  secrets, or project-specific prompts.
- Project-local files remain authoritative and unchanged by package updates.
- Resolver and context commands do not write into an immutable shared version.

### Multi-machine portability

- The same project binding resolves on multiple machines without editing the
  project file.
- Each machine may use a different launcher/cache location.
- Missing machine configuration gives an actionable error and does not modify
  the project.

### Integrity and compatibility

- Exact-version and aggregate-digest checks reject tampering.
- Schema v1 remains readable during the migration window.
- Missing or wrong versions never fall forward silently.
- Existing snapshot installs continue to work.

### Safety and operations

- Install, upgrade, and rollback are transactional or recoverable.
- Native Windows and WSL2 acceptance tests pass.
- Synced-folder conflict files cannot become active package versions.
- The release can be reconstructed from Git and its published manifest.
- If WSL2 cannot operate on a Windows-backed file because a path is too long or
  returns an I/O error, recovery uses Windows PowerShell with an exact
  `-LiteralPath`; Linux-side retries must not be treated as proof of corruption.

## 11. Required tests

- shared package allowlist and project-content leakage test;
- read-only runtime test;
- schema-v1 to schema-v2 compatibility test;
- same binding with two different machine configurations;
- exact-version, missing-version, and checksum-tampering tests;
- project-local prompt precedence test;
- project snapshot rollback test;
- interrupted install and concurrent resolver test;
- OneDrive path alias, spaces, Unicode, and conflict-copy tests;
- native Windows PowerShell parity test;
- downstream installer preservation test for every project-state file.

## 12. Human decisions before implementation

1. Choose the default shared package root convention. Recommendation: a stable
   folder under the user's OneDrive root, containing generic immutable package
   versions only.
2. Choose whether offline behavior defaults to project snapshot or a verified
   machine-local package cache. Recommendation: retain project snapshot during
   the first promoted release.
3. Decide whether machine-profile deduplication belongs in this upgrade.
   Recommendation: defer it; first establish ownership and runtime boundaries,
   then design an optional system inventory without weakening project-local
   compatibility records.
4. Approve the point at which snapshots may be removed. Recommendation: no
   automatic removal in the first stable shared-runtime release.
5. Confirm the first real migration target. Decision: Agent Project Kit itself,
   followed by `media_importer` and `ipst/ai` only after the self-host gate passes.

## 13. Review gate and next loop

This document is an L1 architecture and migration plan. It does not prove L2
approval of the shared-root convention or L3 cross-machine reliability.

The smallest safe next loop is Phase 0 followed by a focused Phase 1 prototype:
add schema-v2 parsing and separate `APK_SHARED_ROOT` from `APK_MACHINE_HOME`,
validate it in temporary directories, and then upgrade Agent Project Kit itself
as the first real canary. Do not migrate a downstream project until the
self-host tests and rollback gate pass.

### Preparation result — 2026-08-06

- Schema-v2 generation and schema-v1 reading are implemented.
- `APK_SHARED_ROOT` and `APK_MACHINE_HOME` are separated; `APK_HOME` remains a
  compatibility path.
- The machine-local launcher stores its shared-root pointer outside the shared
  immutable package.
- Guarded `apk rollback` disables the project binding without deleting project
  state or the installed runtime.
- Temporary tests cover two machine homes sharing one package root, leakage,
  read-only resolution, source preservation, compatibility, and rollback.
- Existing fast-start, v7 context, shared-runtime, and prompt-catalog checks pass.

Readiness decision: **Ready to create a recovery commit/tag and begin the real
self-host canary; the repository has not yet been bound or migrated.** Native
Windows remains a promotion gate, not a prerequisite for the first reversible
WSL2 self-host canary.
