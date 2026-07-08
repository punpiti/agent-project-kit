# LOCAL_RESOURCES

ไฟล์นี้บันทึกไฟล์/โฟลเดอร์ที่อยู่นอก OneDrive หรือไม่ portable ข้ามเครื่อง

## Rule

ถ้า project ใช้ data, cache, intermediate, checkpoint, build artifact, export, virtualenv, หรือไฟล์ใหญ่อื่น ๆ ที่ไม่ได้ sync ผ่าน OneDrive ต้องจดไว้ที่นี่

## Resource Table

| Resource | Purpose | Required? | Size | Synced? | Safe to delete? | Regenerate command | Notes |
|---|---|---:|---:|---:|---:|---|---|
| | | yes/no | | no | yes/no | | |

## Machine-Specific Paths

| Resource | `think` path | `madlab-i9` path | `black5` path | other/unknown path | Last verified |
|---|---|---|---|---|---|
| | | | | | |

## Environment Variables

| Variable | Meaning | Example |
|---|---|---|
| `PROJECT_DATA_ROOT` | Root of large input data outside OneDrive | `/mnt/d/datasets/<project>` |
| `PROJECT_CACHE_ROOT` | Root of generated cache/intermediate files | `/home/<user>/.cache/<project>` |
| `PROJECT_OUTPUT_ROOT` | Non-portable heavy output path | `/mnt/d/outputs/<project>` |

## Current Machine Check

- Current machine:
- Machine profile checked: yes/no (`.ai/MACHINE_PROFILE.md`)
- Checked on:
- Missing resources:
- Task can run here? yes/no/partial
- Recommended machine if not current:

## Notes

- Do not store secrets here.
- Do not assume a path exists on another machine.
- Prefer small portable sample data under OneDrive for smoke tests.
