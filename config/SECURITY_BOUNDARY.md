# Public / Private Security Boundary

The Git repository and installed Agent Project Kit runtime are public product
surfaces. Treat anything placed there as redistributable.

## Classification

| Class | Location | Git/package rule |
|---|---|---|
| Public runtime | allowlisted package files and `config/`, `prompts/`, `scripts/`, `templates/`, `checklists/` | may be committed and installed |
| Public development evidence | tests, generic benchmarks, public documentation | may be committed after review |
| Project-local private state | `.ai/` outside the managed snapshot | ignored; never packaged |
| Private product intelligence | `private/`, `internal/`, `*.private.md`, local profiles | ignored; never packaged or published |
| Credentials and key material | secret manager or machine-local secure store | never stored in this repository |

Public files may describe behavior and acceptance criteria. Keep private
roadmaps, unpublished business strategy, pricing logic, customer information,
holdout evaluations, credentials, and proprietary rationale in the private
zones. Public release notes should state outcomes, not the private reasoning
that produced them.

Run before commit, packaging, tag, or release:

```bash
python3 scripts/check_release_boundary.py
python3 scripts/check_release_boundary.py --release --history
```

The checker reports only file paths and rule identifiers. It does not print a
matched secret. Release mode also stops on tracked, staged, or non-ignored
untracked changes that could be left out of the commit or package. It fails
closed when a candidate is too large or not UTF-8 instead of silently skipping
content. The slower `--history` mode scans every reachable Git blob and is
intended for release review. A pass means the configured high-confidence
patterns found no match; it does not replace repository-host secret scanning or
human classification review. If sensitive material was ever committed,
removing the current file is insufficient because Git history may retain it.
Stop the release, rotate affected credentials, and plan history remediation
separately.
