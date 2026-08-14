# Agent Project Kit benchmark results

Generated: 2026-08-14T02:23:14.853608+00:00<br>
Package: `7.5.0-book-writing-framework-canary`<br>
Commit: `0f9493aca7cfb27fb50b793b32ff750b0cb9545c`<br>
Working tree dirty: `false`

## Results

| Measure | Result | Scope |
|---|---:|---|
| Controlled routing fixture | 29/29 (100.0%) | Bundled English/Thai cases; not real-world accuracy |
| Median selective-context reduction | 95.3% | Versus eager loading every primary/secondary prompt |
| Minimum selective-context reduction | 26.3% | Worst case in the controlled fixture |
| Median selective context | 2045 estimated tokens | UTF-8 bytes / 4, not billed usage |
| Secondary workflow cap observed | 2 | Controlled fixture |
| Repeated cadence actions avoided | 9/10 (90.0%) | Ten starts within a 14-day TTL |
| Transactional/state safety suites | passed | Bash + PowerShell via pwsh on WSL; native Windows not certified |

## What the evidence supports

- APK can materially reduce the instruction context assembled for these tasks compared with an eager-load policy.
- The deterministic router satisfies all expected assertions in the bundled fixture.
- Persisted cadence prevents repeated successful checks inside the configured TTL.
- The tested installer paths preserve project state and recover from the covered update failures.

## What it does not support

- No claim that APK improves model answer quality by a specific percentage.
- No claim that the fixture pass rate generalizes to every prompt or project.
- No claim of measured human time savings, cost savings, or native-Windows reliability yet.

See `benchmarks/README.md` for definitions and `benchmarks/results/latest.json` for case-level evidence.
