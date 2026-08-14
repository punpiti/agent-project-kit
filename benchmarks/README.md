# Agent Project Kit Benchmarks

This benchmark measures the parts of Agent Project Kit that can be evaluated
locally and reproducibly without pretending to measure model intelligence or
human productivity.

## Decision and audience

The primary audience is a prospective VS Code Marketplace user deciding
whether APK adds enough value to install. The benchmark supports claims about:

- selective task-context assembly;
- deterministic routing on a disclosed fixture;
- avoided repeated cadence-controlled work;
- project-state preservation and update recovery in covered failure paths.

It does not support claims about answer-quality lift, developer-hours saved,
API cost saved, or universal routing accuracy.

## KPI definitions

| KPI | Definition | Why it matters | Guardrail |
|---|---|---|---|
| Selective-context reduction | `1 - APK compiled bytes / eager-reference bytes`, summarized by median and minimum across the fixture | Smaller instruction bundles leave more room for task evidence and reduce repeated context loading | Report byte-based token estimates separately from billed tokens |
| Fixture pass rate | Cases satisfying expected domain, deliverable, required methods, and workflow constraints / all disclosed cases | Shows repeatability on known English/Thai tasks | Never label this general model accuracy |
| Cadence avoidance | Successful commands not re-executed / simulated starts inside one valid TTL | Measures repeated startup work that APK deterministically suppresses | Does not estimate network time or money saved |
| Safety-suite result | Real transactional and fast-start acceptance suites return success | Verifies covered preservation, exact-ref, checksum, and rollback behavior | State the host and keep native Windows as a separate gate |

## Baselines

The context comparison uses a controlled eager-loading reference, not another
product. Both sides receive the same configured project/task state:

- APK condition: the structured compiler selects one primary route and up to
  two triggered secondary workflows.
- Reference condition: load every prompt catalog entry classified as `primary`
  or `secondary`. One-time bootstrap and legacy redirect prompts are excluded.

The benchmark serializes both conditions as UTF-8 and reports bytes. Estimated
tokens are bytes divided by four, matching APK's planning estimate. This is not
a tokenizer run and is not provider-billed usage.

## Routing fixture

[`cases.json`](cases.json) contains the disclosed bilingual requests and
expected assertions. The fixture is derived from the maintained structured
context acceptance suite and adds one KPI/dashboard case. Passing means the
current deterministic router satisfies those assertions; it does not establish
performance on unseen prompts.

## Safety evidence

The full benchmark runs:

- `tests/test-transactional-update.sh`
- `tests/test-fast-start.sh`

Together these cover incomplete package sources, staged SHA-256 verification,
previous-snapshot retention, post-switch restoration, state preservation,
exact manifest refs, advertised-version mismatch rejection, managed instruction
idempotency, cadence behavior, and notification-only update checks.

PowerShell installer paths execute through `pwsh` on the current WSL host.
Native Windows is intentionally reported as unverified until that run exists.

## Run it

Full benchmark:

```bash
python3 benchmarks/run_benchmark.py
```

Quick context/cadence pass while editing the runner:

```bash
python3 benchmarks/run_benchmark.py --skip-safety --output-dir /tmp/apk-benchmark
```

Generated evidence:

- `results/latest.json`: full case-level result and environment metadata
- `results/latest.csv`: compact KPI table
- `results/latest.md`: readable summary
- `MARKETPLACE_COPY.md`: claim-safe copy ready to adapt into an extension README
- `report/report.html`: portable evidence report generated from the same result

Build the canonical report artifact after running the benchmark:

```bash
python3 benchmarks/build_report.py
```

The checked-in HTML report is packaged from `report/artifact.json` with the
Data Analytics portable-artifact builder. The current build passed artifact
validation and structural verification. Browser/render interaction QA was not
available on the recorded host because no local Chromium executable was
installed; the builder did not download one.

## Reproducibility and interpretation

Record the Git commit, dirty-tree flag, package version, UTC generation time,
OS, kernel release, and architecture with every result. A dirty-tree result is
valid for development but should be rerun from the tagged Marketplace release
before publishing headline numbers.

Do not compare runs across versions as if they were independent statistical
samples. The cases are deterministic acceptance fixtures. Use repeated runs to
detect implementation drift, and add independently reviewed real-project tasks
before making broader external claims.
