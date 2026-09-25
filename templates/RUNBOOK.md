# RUNBOOK

คำสั่งสำคัญสำหรับ project นี้ เพื่อให้ AI ไม่ต้องเดาทุกครั้ง

## Setup

```bash
# Example: select the shared environment for this project/task.
micromamba run -n <text|image|ml|project-declared-env> <command>

# If a required direct library is missing, install it into that environment.
micromamba install -n <env> <conda-package>
# Pip fallback only when required:
micromamba run -n <env> python -m pip install <pip-distribution>
```

- Selected shared environment:
- Dependency manifest/source:
- Last dependency verification:

Do not create a project `.venv`. Announce ordinary scoped repairs and proceed;
ask before large/metered, GPU/CUDA, privileged, or package-replacing changes.

## Environment Variables

```bash
export PROJECT_DATA_ROOT="/path/to/data"
export PROJECT_CACHE_ROOT="/path/to/cache"
export PROJECT_OUTPUT_ROOT="/path/to/output"
```

## Smoke Test

```bash
# command that should be small and portable
```

## Full Run

```bash
# command for full run, maybe only on primary-heavy
```

## Build / Lint / Type Check

```bash
# commands
```

## Known Slow Commands

| Command | Expected machine | Expected time/size | Notes |
|---|---|---:|---|
| | | | |

## Failure Notes

| Symptom | Likely cause | Fix |
|---|---|---|
| | | |
