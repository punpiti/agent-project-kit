# VS Code Marketplace Extension Development Plan

Status: proposed implementation plan  
Package: Agent Project Kit (`agent-project-kit`)  
Prepared: 2026-08-13  
Primary route: Software Development & Automation  
Loops: L1 implementation, L2 product/IP decisions, L3 Marketplace and real-user evidence

## 1. Outcome

Build a VS Code Marketplace extension that makes Agent Project Kit easy to
initialize, inspect, update, repair, and roll back without creating a second,
conflicting APK installation system.

The extension must behave as a thin control plane over the same APK package,
transaction rules, receipt, and project-owned state used by the GitHub install
path.

```text
GitHub installer ───────┐
                       ├── one install contract ──> .ai/agent-project-kit/
Marketplace extension ─┘                            .ai/APK_INSTALLATION.json
                                                    project-owned .ai/ state
```

The extension is not a second copy of APK and must never silently replace
project content merely because VS Code auto-updated the extension.

## 2. Product Position

Marketplace provides:

- discovery and installation through VS Code;
- commands and status UI;
- preview, conflict explanation, and explicit confirmation;
- a signed distribution of the same APK release payload;
- workspace-aware execution in local, WSL, SSH, and container contexts.

GitHub remains:

- the source and release history for the public APK runtime;
- the direct CLI/manual installation channel;
- the fallback channel when Marketplace is unavailable;
- the source of tagged release identity and public checksums.

Neither channel owns an installed project. The common receipt describes which
tool performed the most recent transaction, but ownership remains with the APK
installation protocol.

## 3. Non-goals for the First Marketplace Release

- Do not rewrite the full APK runtime in TypeScript.
- Do not silently initialize or update a workspace on extension activation.
- Do not delete APK files when the VS Code extension is uninstalled.
- Do not automatically migrate every workspace after an extension update.
- Do not support VS Code for the Web in v1; filesystem/script execution needs a
  desktop or remote Node extension host.
- Do not claim general model-accuracy, productivity, time, or API-cost gains.
- Do not place private development rationale, holdout evaluations, machine
  state, release credentials, or internal roadmap files in the VSIX.

## 4. Ownership Boundaries

| Asset | Owner | Update rule |
|---|---|---|
| VS Code extension directory | VS Code / Marketplace | Managed by VS Code; never used as project state |
| Bundled APK release payload | Extension package | Immutable input to an explicit project transaction |
| `.ai/agent-project-kit/` | APK installer | Transactional replacement with checksum verification |
| `.ai/agent-project-kit.previous/` | APK installer | One recoverable previous managed snapshot |
| `.ai/agent-project-kit-source/` | User/GitHub channel | Optional clone; Marketplace never edits or deletes it |
| `.ai/APK_INSTALLATION.json` | APK installer | Machine-readable common receipt, atomically replaced |
| `.ai/APK_VALUE_METRICS.json` | APK measurement protocol | Content-free local aggregates; preserved, exportable, resettable, never uploaded in v1 |
| `.ai/COMPUTING_ENVIRONMENT_VERSION.md` | APK installer | Human-readable compatibility metadata |
| `.ai/PROJECT_STATE.md` and project state files | Project/user | Preserve across install, update, rollback, and extension removal |
| Extension `workspaceState` | Extension | UI acknowledgement only; never authoritative package state |
| Extension `globalState`/storage | Extension | Extension preferences/cache only; never authoritative project state |

Project truth must remain in the workspace so GitHub, Marketplace, Codex,
Claude Code, and other clients observe the same installed state.

## 5. Common Installation Receipt

Add `.ai/APK_INSTALLATION.json` as the channel-neutral source of installed
package identity. Keep the existing Markdown version record for humans and
legacy compatibility.

Proposed schema:

```json
{
  "schema_version": 1,
  "package_id": "agent-project-kit",
  "package_version": "7.4.0-transactional-update-canary",
  "payload_sha256": "<aggregate managed-payload digest>",
  "installed_at": "2026-08-13T12:00:00+07:00",
  "installed_by": {
    "channel": "marketplace",
    "tool_version": "0.1.0"
  },
  "release": {
    "git_ref": "v7.4.0-transactional-update-canary",
    "release_id": "apk-7.4.0-transactional-update-canary"
  },
  "state_schema_version": 1,
  "machine_profile_schema_version": 1
}
```

Rules:

1. `installed_by.channel` is diagnostic provenance, not ownership.
2. The aggregate digest is calculated from a canonical relative-path order.
3. The receipt is written only after the new snapshot and managed control files
   pass validation.
4. Receipt replacement participates in rollback.
5. A legacy installation without the JSON receipt is inspected from manifest
   and version metadata, then adopted only after its digest is computed.

## 6. Version and Conflict Protocol

Every install entry point must produce the same decision for the same current
and candidate states.

| Current versus candidate | Required decision |
|---|---|
| No installation | Offer initialize; write only after explicit command |
| Same package ID, version, and digest | No-op; optionally adopt channel metadata |
| Candidate version newer | Preview changes, then explicit transactional update |
| Candidate version older | Refuse by default; require an explicit downgrade command and warning |
| Same version, different digest | Stop with integrity conflict; never overwrite |
| Different package ID in managed target | Stop; do not adopt or overwrite |
| Missing/incomplete active snapshot | Offer doctor/repair from a verified payload |
| State schema migration required | Preview migration and rollback limits before update |
| Active install lock | Wait briefly or report the other transaction; never run concurrently |

Add an atomic project lock such as `.ai/.agent-project-kit-install.lock`.
Record host, process ID, command, channel, and start time for diagnosis. Define a
tested stale-lock recovery path; do not delete an apparently live lock merely
because a timeout elapsed.

## 7. Shared Transaction Engine

For v1, reuse the existing signed/bundled APK Bash and PowerShell installers
rather than implementing a third file-copy engine inside the extension:

- Linux, macOS, WSL, SSH Linux, containers: invoke the bundled
  `scripts/install-to-project.sh`.
- Windows workspace host: invoke the bundled
  `scripts/install-to-project.ps1` with PowerShell.
- Pass the extension's immutable bundled payload as `SourcePath` and the active
  workspace folder as `ProjectPath`.
- Pass channel and tool-version metadata so both scripts write the common
  receipt.

Before exposing Marketplace update commands, refactor the duplicated policy in
the Bash and PowerShell paths into a documented transaction contract with
shared fixtures. Byte-for-byte implementation identity is not required, but
decision, checksum, state-preservation, and rollback behavior must be identical.

The transaction remains:

```text
inspect -> decide -> lock -> stage -> hash -> validate -> preserve controls
        -> switch -> write receipt -> verify -> unlock
                    \-> restore everything on failure
```

## 8. Marketplace UX Contract

### Commands for v1

1. `APK: Initialize This Project`
2. `APK: Show Project Status`
3. `APK: Preview Update`
4. `APK: Update Project`
5. `APK: Roll Back Project`
6. `APK: Repair or Diagnose Installation`
7. `APK: Show My Project Benefits`
8. `APK: Copy Shareable Benefit Summary`

### Startup behavior

Activation and workspace opening are read-only. Detect state lazily and show at
most one unobtrusive status item. Do not clone, fetch, install, update, or run
project code automatically.

| Detected state | UX |
|---|---|
| APK absent | `APK: Not initialized` with an explicit Initialize action |
| Installed through GitHub, same bundled release | `APK: Installed` and offer non-destructive Adopt/Manage |
| Installed release older than bundled payload | `APK: Update available`; offer Preview first |
| Installed release newer than bundled payload | `APK: Project is newer`; do not downgrade |
| Same version, different digest | `APK: Integrity conflict`; provide details and Doctor only |
| Broken or incomplete snapshot | `APK: Repair required`; preserve state and show proposed repair |
| Untrusted workspace | Read-only status only; hide/block write and script commands |
| Multi-root workspace | Show status and request a target folder per project operation |

### Confirmation model

Preview must show:

- target workspace folder;
- current and candidate APK versions;
- source channel and release identity;
- payload digest status;
- state/machine schema change;
- files owned by APK that will be replaced;
- project-owned state that will be preserved;
- rollback snapshot behavior;
- downgrade or repair warning when applicable.

Normal same-version no-op status checks require no confirmation. Initialize,
update, rollback, repair, and downgrade require an explicit user command.

### Extension update versus project update

Maintain two visible versions:

```text
Extension 0.2.0 contains APK 7.5.0
This project currently uses APK 7.4.0
```

VS Code may auto-update the extension. That event must not update the project.
The extension only reports that a newer bundled APK payload is available.

## 9. User Benefit Measurement and Shareability

Marketplace install count is a distribution metric, not proof that APK helped
anyone. The extension must make locally verifiable benefits visible to the user
and keep product-health metrics separate from user outcomes.

### Measurement principles

1. Prefer observed events over inferred savings.
2. Show the user the denominator, time window, APK version, and comparison
   condition for every percentage.
3. Never translate bytes into money, billed tokens, or hours saved without a
   separately validated source.
4. Never call a configured state file a successful resume unless the state was
   actually loaded; never call a load helpful unless the user confirms it or a
   defined task outcome supports it.
5. Keep fixture benchmarks, local project evidence, and user survey evidence
   visibly separate.
6. Collect no request text, source code, file contents, personal paths, project
   names, or state contents for metrics.
7. Store v1 benefit evidence locally. Sharing and any future aggregate
   telemetry are explicit opt-in actions.
8. Every shareable claim must be reproducible from a local metric record or a
   linked public benchmark result.

### KPI hierarchy

Use three primary product KPIs. Targets remain provisional until pre-release
cohort data exists; reliability guardrails can have hard release thresholds
immediately.

| KPI | Definition | Decision supported | Main limitation |
|---|---|---|---|
| Value activation rate | Initialized projects that become healthy and record at least one verified benefit event within 7 days / initialized projects in the reviewed cohort | Whether onboarding reaches actual use rather than stopping at install | Requires an observed cohort; Marketplace install count alone is not the denominator |
| Repeat value rate | Activated projects with verified benefit events on at least two distinct weeks in their first 30 days / activated projects reaching 30-day maturity | Whether APK remains useful after first setup | Slow-moving and affected by projects that naturally pause |
| User-verified benefit rate | Respondents confirming at least one named benefit—less re-explanation, clearer next action, reduced repeated checks, or safer update / valid respondents | Whether technical events correspond to perceived user value | Voluntary responses have selection bias; always report response count |

Driver metrics used to diagnose the primary KPIs:

| Driver | Definition | Why it helps |
|---|---|---|
| Initialize completion | Successful verified initialization / explicit initialization attempts | Detects setup friction |
| Time to healthy project | Elapsed time from explicit Initialize to a healthy receipt/snapshot/state check | Detects slow or confusing onboarding; do not call it time saved |
| Context focus | `1 - selected serialized guidance bytes / disclosed eager-reference bytes`, reported as median, minimum, p95, and case count | Quantifies instruction-volume reduction while preserving its comparison basis |
| Resume-ready state load | Returning task compilations that successfully load configured project state / returning task compilations | Shows continuity machinery was available and used, not that it improved the answer |
| Cadence executions avoided | Valid cached successful actions skipped inside their TTL / eligible cadence checks | Counts deterministic repetition avoided |
| Verified safe lifecycle | Install/update/rollback transactions completing checksum, state-preservation, receipt, and post-switch checks / lifecycle attempts | Shows whether safety behavior works in real projects |
| Share action rate | Users copying/exporting a benefit summary / users viewing the benefit view | Indicates whether evidence is understandable enough to communicate; not itself product value |

Operational definitions:

- **Initialized project:** one workspace folder with a verified current receipt
  and snapshot; reinstalling or switching channels does not create a new
  project in the cohort.
- **Healthy project:** receipt, package identity, active snapshot digest, state
  schema, and required control files pass Doctor without repair-required or
  integrity-conflict status.
- **Activation window:** the first seven complete 24-hour periods after the
  verified initial installation timestamp.
- **30-day maturity:** 30 complete 24-hour periods have elapsed since verified
  initialization; immature projects are excluded from the repeat-value
  denominator rather than counted as failures.
- **Distinct week:** a local-calendar ISO week recorded without timezone or
  location details in exported aggregates.
- **Returning task compilation:** a context compilation after initialization
  that occurs in a later recorded work period and has configured state
  available. Until a cross-agent session boundary is implemented reliably,
  report raw configured-state loads and do not publish a resume-rate headline.
- **Valid respondent:** one voluntary response with the survey version and
  completion status recorded; no identity, prompt, or project content.
- **Verified benefit event:** only the objective events defined below. Command
  invocations and extension activations alone never count.

Do not combine these measures into a single “APK score.” A composite would hide
whether the observed value came from context focus, continuity, cadence, or
safety and would be easy to improve without improving the user's outcome.

Guardrails:

| Guardrail | Release expectation |
|---|---|
| Project-state loss | Zero accepted cases; any confirmed loss blocks release |
| Silent workspace mutation | Zero; activation and extension auto-update remain read-only |
| Integrity conflict overwritten | Zero; same-version/different-digest always fails closed |
| Unsupported claim in generated summary | Zero across golden/share snapshot tests |
| Metric privacy violation | Zero prompt text, source content, personal path, project name, or state content in the metric ledger/export |
| Native/remote parity | All supported hosts pass the same conflict and rollback decision fixtures |

### Advocacy and word-of-mouth indicators

Helping users explain APK is a product requirement, but sharing activity must
not replace actual benefit. Track this as a secondary funnel:

| Stage | Metric | Interpretation |
|---|---|---|
| Evidence ready | Active projects with at least two benefit families supported by valid local evidence / active projects reviewed | Enough substance exists for a useful summary |
| Evidence understood | Benefit views reaching the methodology/details action / benefit views | Users inspected what the numbers mean; diagnostic only |
| Summary copied | Previewed summaries copied or exported / benefit views | Users found the evidence communicable |
| Recommendation intent | Valid respondents answering that they would recommend APK / valid respondents | Direct but self-reported advocacy signal |
| Referred activation | Not collected in v1 | Requires a separate privacy decision; never infer it from Marketplace installs |

Do not generate unique referral identifiers, append project/user identifiers to
links, post automatically, or prompt for sharing after every task. Offer the
share action when enough evidence exists and let the user initiate it.

### What counts as a verified benefit event

A project records a benefit event only when an objective condition is met:

| Event | Evidence required | User-facing wording allowed |
|---|---|---|
| `context_compiled` | Selected and eager-reference byte counts, route count, versions, and calculation complete | “Focused guidance by X% versus the documented eager reference” |
| `project_state_loaded` | Configured state was parsed and included in a task context | “Loaded project memory for this task” |
| `cadence_action_skipped` | A prior successful action is still valid within the declared TTL | “Skipped one repeated check” |
| `install_verified` | Snapshot, receipt, digest, and preserved-state checks pass | “Verified installation without changing project-owned state” |
| `update_verified` | New snapshot passes and declared project-state files remain byte-identical or an approved migration is verified | “Preserved N project-state files during this update” |
| `rollback_verified` | Prior snapshot and control files are restored and verified | “Recovered the previous APK snapshot” |
| `user_benefit_confirmed` | User explicitly selects one or more named benefits | “You marked project resume as helpful” |

Do not record an event for a command that failed before its defining condition.
Retry attempts, previews, and status views are diagnostic activity, not benefit
events.

### Local metric ledger

Add an optional, tool-owned file such as `.ai/APK_VALUE_METRICS.json`. It is
preserved by installers but is not part of project-authored memory. GitHub CLI
and Marketplace must write the same schema so benefits remain continuous when
channels change.

Example aggregate-first schema:

```json
{
  "schema_version": 1,
  "package_id": "agent-project-kit",
  "period_start": "2026-08-01T00:00:00Z",
  "updated_at": "2026-08-13T05:00:00Z",
  "context": {
    "compilations": 12,
    "reference_policy": "all-primary-secondary-v1",
    "median_reduction_percent": 91.4,
    "minimum_reduction_percent": 42.8,
    "p95_selected_bytes": 48200
  },
  "continuity": {
    "configured_state_loads": 8,
    "returning_task_compilations": 9
  },
  "cadence": {
    "eligible_checks": 10,
    "executions_avoided": 9
  },
  "lifecycle": {
    "verified_installs": 1,
    "verified_updates": 2,
    "verified_rollbacks": 0,
    "state_files_preserved": 34,
    "failed_transactions": 0
  }
}
```

Default to aggregates rather than a permanent event-by-event history. If a
short diagnostic event buffer is needed, retain at most 90 days, omit user
content, make retention configurable, and provide `View`, `Export`, `Reset`,
and `Delete Local Metrics` actions. Package and schema versions may be stored;
workspace path, project name, raw request, route text, filenames, file hashes,
Git remote, user identity, and machine hostname may not be stored in this
ledger.

The ledger is not sent to the publisher in v1. A future telemetry proposal
requires a separate privacy review, explicit opt-in, documented endpoint,
retention policy, deletion path, and proof that the product decision cannot be
answered with less data.

### User-facing benefit view

`APK: Show My Project Benefits` should answer four plain-language questions:

1. **Did APK keep guidance focused?** Show median/minimum context reduction,
   comparison policy, compilation count, and byte-based caveat.
2. **Did APK help the project resume?** Show successful configured-state loads
   and state freshness; label these “memory loaded,” not “time saved.”
3. **Did APK avoid repeated work?** Show actual cadence executions avoided and
   eligible checks within the displayed period.
4. **Did APK protect the project?** Show verified installs/updates/rollbacks,
   state-file preservation count, current recovery snapshot, and failures.

The view must distinguish:

- **Your project evidence** — locally observed events for this workspace;
- **APK public benchmark** — controlled fixture evidence linked to method/raw
  results;
- **Not measured yet** — answer quality, developer hours, billed token cost,
  and unseen-prompt accuracy.

If the local denominator is too small, show the raw count instead of a
percentage. Empty states should say “not measured yet,” never zero benefit.

### Shareable benefit summary

`APK: Copy Shareable Benefit Summary` generates Markdown locally and copies it
only after preview. Provide short and evidence-detail variants.

Example short form:

```markdown
APK benefit snapshot for this project (1–31 Aug 2026)

- Focused task guidance by a median 91.4% versus APK's documented eager-loading reference across 12 compilations.
- Loaded configured project memory for 8 of 9 returning task compilations.
- Skipped 9 repeated cadence-controlled checks out of 10 eligible checks.
- Verified 2 updates while preserving 34 declared project-state file instances; a previous snapshot is available.

Generated locally by Agent Project Kit. No prompt text, source code, project path, or personal data is included. Context percentages measure serialized guidance bytes, not billed tokens or answer quality.
```

Rules for generated sharing copy:

- Include the period, denominator, APK version range, reference-policy version,
  and local/public evidence label.
- Use counts instead of percentages below the configured minimum denominator.
- Omit any metric with missing or failed evidence; never substitute a fixture
  benchmark as if it were the user's result.
- Never include project name/path, prompt text, repository URL, machine name,
  filenames, or user identity unless the user manually adds them afterward.
- Offer “Copy short summary,” “Copy evidence detail,” and “Open methodology.”
- Add a stable methodology link and a machine-readable JSON export.
- Mark user-confirmed statements separately from automatically observed facts.
- Never generate “APK saved me X hours/tokens/money” from proxy metrics.
- Never rank users or projects, and never use a vague composite benefit score.

Provide a third copy option, `Explain what APK does`, for users who have too
little local evidence. It should describe the product contract without
pretending to be a personal result:

```markdown
Agent Project Kit gives AI coding agents persistent project context, selective
task workflows, machine-aware setup, acceptance checks, and recoverable
updates. It keeps project-owned state separate from the managed kit so work can
resume across sessions, agents, and supported machines.

This describes APK's design. See the linked benchmark and methodology for
controlled evidence; it is not a measurement of this project's outcome.
```

### Public proof people can cite

The Marketplace README should provide a compact evidence kit:

- one stable benchmark landing page;
- human-readable result and methodology;
- case-level JSON and fixture version;
- clean Git tag, package version, host scope, and generation date;
- exact supported claims and prohibited interpretations;
- a copyable citation block;
- badges only for binary, reproducible release gates—not for subjective value.

Public benchmark numbers must be regenerated from the clean Marketplace tag.
The current development result—29/29 controlled fixture assertions, 95.2%
median context reduction versus the disclosed eager reference, 9/10 repeated
cadence actions avoided, and passing local WSL safety suites—may be used as
development evidence only while the tree is dirty. It must not be presented as
the final Marketplace release result.

### Measurement cadence and ownership

| Review | Cadence | Decision | Owner/source |
|---|---|---|---|
| Release reliability | Every build/release | Block or approve release | CI plus cross-platform transaction tests |
| Onboarding/value activation | Weekly during pre-release | Fix initialization or first-value friction | Reviewed cohort; local exports with consent |
| Repeat value | Monthly after 30-day maturity | Improve ongoing workflows or cadence | Reviewed cohort; opt-in aggregates |
| User-verified benefit | At pre-release milestones, not every session | Validate whether technical events feel useful | Short voluntary survey with response count |
| Public benchmark | Every clean tagged release that changes routing/runtime | Refresh or retain claims | Reproducible repository benchmark |

Do not set public improvement targets from the current controlled fixture.
During pre-release, establish baselines first. Initial hard targets apply only
to safety and measurement correctness: zero state loss, zero silent mutation,
zero overwritten integrity conflicts, and zero unsupported generated claims.

After the first reviewed cohort, set targets using both bottom-up observed
conversion and the minimum level that would justify continued investment. Do
not choose a target solely because it sounds impressive. Report confidence,
cohort size, maturity exclusions, missing exports, and survey response rate
alongside every target review.

## 10. VS Code Runtime and Security

Proposed manifest behavior:

```json
{
  "extensionKind": ["workspace"],
  "capabilities": {
    "untrustedWorkspaces": {
      "supported": "limited",
      "description": "Status inspection is available; install, update, repair, rollback, and script execution require a trusted workspace."
    },
    "virtualWorkspaces": {
      "supported": false
    }
  }
}
```

Requirements:

- Run beside the workspace in WSL, SSH, containers, and Codespaces where a
  Node workspace extension host exists.
- Use VS Code workspace URIs rather than assuming local UI-machine paths.
- Require `vscode.workspace.isTrusted` before any write or subprocess.
- Never execute scripts from the target workspace; execute the verified scripts
  bundled with the extension payload.
- Pass subprocess arguments as arrays without shell interpolation.
- Redact local paths and environment data from telemetry and error reports.
- Ship with telemetry disabled unless a separate explicit policy and opt-in are
  approved.
- Do not support virtual/web-only workspaces in v1.

## 11. Build Once, Publish Twice

Create one canonical release payload from a clean APK tag:

```text
clean Git tag
    -> canonical file inventory
    -> per-file SHA-256 manifest
    -> aggregate payload SHA-256
    -> GitHub release asset
    -> identical payload embedded in VSIX
```

Release CI must fail unless:

- Git tag, `manifest.json.git_ref`, and package version agree;
- working tree is clean;
- every inventory file exists;
- per-file and aggregate checksums reproduce;
- GitHub release payload and VSIX payload have the same aggregate digest;
- VSIX contains no disallowed development/private files;
- extension version and bundled APK version are recorded separately;
- benchmark headline values were regenerated from the clean tag.

## 12. Intellectual-Property and Packaging Boundary

The runtime contract and any instruction that an agent must read in a user
workspace are inspectable and must not be treated as secrets. Protect the
development advantage by controlling what is published, not by claiming that
client-side bundling is confidential.

### Ship publicly

- documented APK behavior and schemas;
- install/update/rollback runtime required for operation;
- user-facing prompt/runtime content required by agents;
- public reproducible benchmark cases and results;
- security and state-preservation contract;
- license, changelog, support, and privacy documentation.

### Keep out of the VSIX and optionally move to a private development repo

- private prompt-design rationale and experiment history;
- rejected approaches and competitive analysis;
- unpublished roadmap and product strategy;
- private/holdout benchmark cases and evaluator notes;
- local `.ai/` state, machine profiles, and project logs;
- release credentials, signing configuration, and private CI variables;
- internal incident notes and unpublished security test cases;
- raw TypeScript source maps when not required for support.

Before Marketplace publication, add an allowlist-oriented `.vscodeignore` and
run `vsce ls` plus an unpacked-VSIX audit. Bundling/minification may reduce
package size but must not be described as secrecy or security. Do not add
obfuscation that weakens auditability and trust.

Deleting already-public Git history does not make it secret. Any material that
requires confidentiality must be newly separated and never committed to the
public repository or packaged artifact.

## 13. Proposed Repository Shape

Keep extension code isolated from the installable APK root so `.vscodeignore`
and release inventory can be audited deliberately:

```text
extension/
├── package.json
├── package.nls.json
├── src/
│   ├── extension.ts
│   ├── inspect.ts
│   ├── commands.ts
│   ├── transaction.ts
│   └── ui.ts
├── test/
├── esbuild.mjs
├── tsconfig.json
└── .vscodeignore

dist/
└── extension.js

release-payload/
├── manifest.json
├── checksums.json
└── agent-project-kit/
```

The `release-payload/` directory is generated from a clean tag and must not be
hand-edited. Development source and private material are never copied into it.

## 14. Implementation Phases

### Phase 0 — Product and IP boundary

- Inventory current public runtime versus development-only material.
- Decide whether private development intelligence remains in a private sibling
  repository or is generated in private CI.
- Approve the public license, privacy statement, support policy, and publisher
  identity.
- Freeze the v1 non-goals and supported platforms.

Exit gate: a reviewed ship/do-not-ship inventory exists before scaffolding the
Marketplace package.

### Phase 1 — Channel-neutral install protocol

- Add `APK_INSTALLATION.json` schema and compatibility reader.
- Add aggregate payload digest and canonical ordering.
- Add channel/tool provenance inputs to Bash and PowerShell installers.
- Add install lock and stale-lock diagnostics.
- Implement the version/conflict decision table.
- Preserve receipt and lock correctness through rollback.

Exit gate: GitHub install/update behavior passes old tests plus cross-channel
fixture tests without any extension code.

### Phase 2 — Canonical release payload

- Generate an immutable payload from a clean tag.
- Generate per-file and aggregate checksum manifests.
- Add CI comparison between GitHub release and VSIX payloads.
- Add disallowed-file and secret scans.

Exit gate: one payload can be independently verified and embedded unchanged in
both release channels.

### Phase 3 — Minimal VS Code extension

- Scaffold a workspace extension with lazy command activation.
- Implement read-only installation inspection.
- Add multi-root folder selection.
- Add status item and Show Project Status.
- Add trusted-workspace gating and virtual-workspace rejection.
- Add the local aggregate metric schema with collection disabled for any field
  that could contain user content.

Exit gate: installing or opening the extension causes no workspace mutation or
network request.

### Phase 4 — Explicit lifecycle commands

- Implement Initialize, Preview Update, Update, Roll Back, and Repair.
- Invoke verified bundled Bash/PowerShell scripts by platform.
- Stream concise progress and preserve detailed logs for diagnosis.
- Translate transaction outcomes into clear user actions.
- Add Show My Project Benefits, metric reset/export, previewed share summary,
  and methodology links.

Exit gate: every command satisfies the UX and conflict table, including cancel
and failure paths.

### Phase 5 — Cross-channel and remote validation

- GitHub first -> Marketplace adopt.
- Marketplace first -> GitHub no-op/update.
- Same version/different digest conflict.
- Older candidate downgrade refusal.
- Concurrent GitHub/Marketplace transaction locking.
- WSL, native Windows, macOS/Linux, SSH, and container workspace runs.
- Trusted and untrusted workspace test runs.
- Multi-root selection and rollback.
- Metric continuity across channel changes, privacy-field rejection, minimum-
  denominator wording, and golden share-summary snapshots.

Exit gate: no channel can corrupt, duplicate, silently downgrade, or take
ownership of project state.

### Phase 6 — Marketplace release preparation

- Add icon, Marketplace README, changelog, license, support, privacy, and
  security documentation.
- Include the clean-tag benchmark copy and evidence links.
- Run `vsce ls`, build VSIX, unpack it, and audit every shipped file.
- Install the VSIX into a clean VS Code profile and run the end-to-end matrix.
- Publish a pre-release channel before stable.
- Run a small consented cohort to establish activation, repeat-value, and
  user-verified-benefit baselines without treating install count as value.

Exit gate: signed/pre-release artifact passes package, UX, state-preservation,
remote, trust, and content-boundary review.

## 15. Acceptance Criteria

### Installation and conflict safety

- [ ] GitHub and Marketplace use the same package identity, digest algorithm,
  receipt, and transaction rules.
- [ ] A same-version/same-digest install is a no-op.
- [ ] A same-version/different-digest install fails closed.
- [ ] Downgrade requires a separate explicit command and warning.
- [ ] Concurrent installation is rejected or serialized by an atomic lock.
- [ ] Project-owned state survives initialize, update, rollback, repair, channel
  switch, extension update, and extension uninstall.
- [ ] Extension uninstall leaves the project installation untouched.

### UX

- [ ] Opening a workspace never installs or updates APK.
- [ ] Every mutating command identifies its target workspace.
- [ ] Preview distinguishes extension version from project APK version.
- [ ] GitHub installations can be adopted without reinstalling.
- [ ] Integrity conflicts explain the mismatch and provide a safe next action.
- [ ] Multi-root workspaces never mutate an implicitly selected folder.
- [ ] Benefit view separates local evidence, public fixture evidence, and
  unmeasured outcomes.
- [ ] Share copy includes period, denominator, comparison basis, scope, and
  caveat and is previewed before copying.

### Benefit measurement

- [ ] Verified benefit events are recorded only after their defining checks
  pass; preview, retry, and failed commands do not inflate them.
- [ ] Context focus reports median, minimum, p95, case count, and reference
  policy rather than a context-free percentage.
- [ ] Resume metrics say state was loaded and never infer answer quality or time
  saved without separate evidence.
- [ ] Cadence avoidance counts only valid cached successful actions.
- [ ] State preservation counts only files checked successfully after a real
  lifecycle transaction.
- [ ] Empty or insufficient samples display “not measured yet” or raw counts.
- [ ] Local metrics survive GitHub/Marketplace channel changes but are untouched
  by package snapshot replacement.
- [ ] Users can view, export, reset, and delete local benefit metrics.
- [ ] v1 sends no metric ledger or user data to the publisher.
- [ ] Short and detailed share outputs pass golden tests for every supported
  metric combination and never include disallowed fields.

### Platform and trust

- [ ] The extension runs as a workspace extension in WSL/remote contexts.
- [ ] Untrusted workspaces expose read-only status and block all writes/scripts.
- [ ] Native Windows PowerShell and POSIX installer paths have equivalent
  decision and rollback results.
- [ ] v1 rejects unsupported virtual/web workspaces clearly.

### Packaging and IP boundary

- [ ] GitHub and VSIX payload digests match.
- [ ] The VSIX contains no `.ai/` developer state, private cases, credentials,
  internal roadmap, development notes, test output, or source maps.
- [ ] Public runtime behavior remains inspectable and documented.
- [ ] Marketplace claims link to clean-tag evidence and disclose limitations.

## 16. Test Matrix

| Area | Required cases |
|---|---|
| Inspect | absent, valid legacy, valid receipt, partial snapshot, bad digest, foreign target |
| Version | equal, upgrade, downgrade, prerelease ordering, equal version/bad digest |
| Transaction | stage failure, checksum failure, switch failure, receipt failure, rollback failure reporting |
| State | every declared project-state file remains byte-identical unless an approved schema migration applies |
| Cross-channel | GitHub -> Marketplace, Marketplace -> GitHub, repeated alternation |
| Concurrency | two Marketplace commands, Marketplace plus GitHub, stale lock, live lock |
| VS Code | trusted, untrusted, multi-root, no-folder window, extension update, extension uninstall |
| Platform | Linux, macOS, WSL, native Windows, SSH/container workspace host |
| Packaging | clean tag, checksum reproduction, VSIX inventory, secret scan, unpacked smoke install |
| Benefit events | valid/failed context compilation, state load, TTL skip, install, update, rollback |
| Metric math | median/minimum/p95, zero/one/small denominators, rolling period, schema migration |
| Privacy | prompt/path/name/content/hash rejection, local-only default, reset/delete/export |
| Share copy | local versus fixture labels, caveats, missing metrics, user-confirmed wording, golden Markdown |
| Product KPI | 7-day activation cohort, 30-day maturity, distinct-week repeat value, survey response denominator |

## 17. Human Decisions Required Before Phase 1

1. Public/private boundary: keep one public repository with excluded files, or
   create a private development sibling repository before Marketplace work?
2. Publisher identity: personal publisher or a durable project/organization
   publisher?
3. License: what reuse and redistribution of the runtime and prompts is allowed?
4. Telemetry: recommended v1 decision is none.
5. Supported v1 platforms: recommended desktop VS Code plus local/WSL/SSH/
   container workspace hosts; no web/virtual workspace.
6. Update policy: recommended explicit per-project apply, never automatic on
   extension update.
7. Private evaluation: which new holdout cases should never enter the public
   repository or VSIX?
8. Local metrics: approve the proposed content-free aggregate ledger, 90-day
   diagnostic maximum, user reset/delete, and no-telemetry v1 policy?
9. User study: what minimum pre-release cohort and review cadence are realistic
   before setting activation or repeat-value targets?

## 18. Recommended First Implementation Slice

Do not begin with Marketplace UI. First implement and test the common receipt,
digest, lock, and conflict decision table in the existing GitHub installers.

The smallest valuable slice is:

1. add `APK_INSTALLATION.json`;
2. compute a canonical aggregate digest;
3. make repeated same-release installs no-op;
4. reject same-version/different-digest and implicit downgrade;
5. add cross-channel-neutral provenance;
6. test all of the above in Bash and PowerShell.
7. define the content-free benefit-event schema and golden share-copy fixtures,
   but do not add remote telemetry.

After that foundation passes, the extension can remain thin and predictable.
Building UI first would merely hide unresolved ownership and conflict behavior
behind buttons.

## 19. Review Gate

L1 is ready to begin after the Phase 0 decisions. L2 remains essential for the
public/private boundary, license, publisher identity, supported platforms, and
claim wording. L3 is not satisfied until native Windows, remote workspaces, a
Marketplace pre-release, and real-user channel-switch behavior have been
observed.

The plan is complete when the extension is a reversible control surface over
one APK installation—not an additional installation competing with GitHub.
