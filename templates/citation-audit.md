---
title: Citation audit — <manuscript name>
manuscript: <path to manuscript>
manuscript_version: <version, date or commit>
audited: <YYYY-MM-DD>
auditor: <agent/tool and owner>
---

# Citation audit — <manuscript name>

Claim-level check of every citation against its source. Later sessions re-check
only rows whose `source_sha256` or citing sentence changed; everything else is
reused. Keep this file in the project's `evidence/` folder.

Verdicts: `SUPPORTED` (source states the claim), `PARTLY` (states a weaker,
narrower or different claim), `NOT` (does not state it), `CANNOT CHECK` (no PDF
or resolvable link, or the needed pages are unreadable).

| Key | Citing sentence (or its SHA-256 prefix) | Source (PDF path or DOI/URL) | source_sha256 (12) | Verdict | Supporting quote | Page/section | Accurate rewording |
|---|---|---|---|---|---|---|---|
| smith2024 | "…" | refs/smith2024.pdf | 0123456789ab | SUPPORTED | "…" | p. 4, §3.1 | — |

## Missing sources

Keys without a PDF or resolvable link (report to the owner; never guess the content).

## Owner notes

Concerns about scope or citation choice that belong outside the manuscript.
