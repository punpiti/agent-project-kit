# Marketplace benchmark copy

## Evidence-backed short version

Agent Project Kit keeps AI workspace context focused and project memory durable. In the bundled 29-case English/Thai routing benchmark, APK loaded one primary route and no more than 2 secondary workflows while reducing serialized task context by a median of **95.3%** versus an eager policy that loads every primary and secondary prompt. All **29/29 fixture assertions passed**.

Persisted cadence also avoided **9 of 10 repeated checks** inside a simulated 14-day window. Transactional update tests verified staged SHA-256 checks, project-state preservation, exact release refs, retained previous snapshots, and automatic rollback on the tested Bash and PowerShell paths.

## Suggested Marketplace bullets

- **Loads only task-relevant guidance:** median 95.3% less serialized context than the documented eager-loading reference across 29 controlled cases.
- **Routes repeatably:** 29/29 expected English/Thai routing assertions passed in the bundled fixture.
- **Avoids repeated startup work:** 90% of repeated cadence-controlled actions were skipped across ten starts inside one TTL window.
- **Protects project memory:** update tests preserve project-local state and retain a recoverable previous snapshot.
- **Fails safely:** incomplete, mismatched, or post-switch failures are rejected or rolled back in the covered installer tests.

## Required footnote

Benchmark results are from the repository's controlled fixture on `Linux / x86_64` at commit `0f9493aca7cf`. Context reduction is measured against the documented eager-loading reference, not against another product. Token counts are byte-based estimates. Routing results are fixture assertions, not general model-accuracy claims. PowerShell ran through `pwsh` on WSL; native Windows remains a separate validation gate.

Publication status: `working_tree_dirty=false`. Regenerate from the clean tagged Marketplace release before publishing headline values.

## README placement

Place the short version after the feature overview, then link to:

- `benchmarks/results/latest.md` for the readable result
- `benchmarks/results/latest.json` for case-level evidence
- `benchmarks/README.md` for methodology and rerun instructions

VS Code Marketplace renders the extension root `README.md`; use HTTPS for remote images and keep benchmark claims in normal Markdown text.
