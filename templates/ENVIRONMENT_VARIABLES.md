# ENVIRONMENT_VARIABLES

บันทึกตัวแปรแวดล้อมที่ project ต้องใช้ โดยไม่ใส่ secret จริง

## Required Variables

| Variable | Required? | Purpose | Example | Machine-specific? |
|---|---:|---|---|---:|
| `PROJECT_DATA_ROOT` | no/yes | Large data outside the project/shared source tree | `/mnt/d/datasets/<project>` | yes |
| `PROJECT_CACHE_ROOT` | no/yes | Cache/intermediate outside the project/shared source tree | `/home/<user>/.cache/<project>` | yes |
| `PROJECT_OUTPUT_ROOT` | no/yes | Heavy outputs outside the project/shared source tree | `/mnt/d/outputs/<project>` | yes |

## Secret Variables

Do not write real secret values here. Record only variable names and where they are managed.

| Variable | Purpose | Where managed |
|---|---|---|
| | | |

## Example `.env.example`

```bash
PROJECT_DATA_ROOT=/path/to/data
PROJECT_CACHE_ROOT=/path/to/cache
PROJECT_OUTPUT_ROOT=/path/to/output
```
