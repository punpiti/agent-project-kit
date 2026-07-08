# Project Runs

Cross-machine log of projects that are running, deployed, tested, or moved.

Last updated: 2026-06-30

## Rules

- Newest rows go at the top of the table.
- Add a row whenever a project starts running on a machine, moves host, changes
  port/URL, or changes role.
- Mark stale rows in `Status` as `superseded`, `stopped`, or `archived`; do not
  delete historical rows unless they contain secrets.
- Do not include tokens, passwords, private keys, or secret query strings.

## Runs

| Timestamp | Machine | Project | Status | Path | Command | Port | URL | Git Remote | Notes |
|---|---|---|---|---|---|---|---|---|---|
| 2026-06-30T09:39:06+07:00 | madlab-i9 | Nowcast / ting67 | analysis | /home/punpiti/OneDrive/nowcast/ting67 | conda activate rain |  |  |  | Default local environment for nowcast/AMT work; conda shell function maps to micromamba; env path /home/punpiti/.local/share/mamba/envs/rain |
| 2026-06-16T01:03:51+07:00 | urban | Urban Platform | production | /home/punpiti/OneDrive/urban/urban_platform |  |  | https://urban.cpe.ku.ac.th | git@github.com:punpiti/urban.git | Known production/deploy host from README; command and port not recorded |
