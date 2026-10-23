# LOCAL_RESOURCES

ไฟล์นี้บันทึกไฟล์/โฟลเดอร์ที่อยู่นอก project folder หรือ shared/synced source tree และไม่ portable ข้ามเครื่อง

## Rule

ถ้า project ใช้ data, cache, intermediate, checkpoint, build artifact, export, virtualenv, หรือไฟล์ใหญ่อื่น ๆ ที่อยู่นอก project/shared source tree ต้องจดไว้ที่นี่

## Resource Table

Tier และ rebuild class ใช้ตาม `DATA_FLOW_POLICY.md`: tier = `hot` (SSD) / `cold` (HDD/external) / `scratch` / `durable` (cloud drive); class = `R0` ถูกและสร้างซ้ำได้ / `R1` สร้างซ้ำได้แต่แพง / `R2` มี judgment ของคนหรือ AI (ห้ามลบเอง) / `final`

| Resource | Purpose | Tier | Rebuild class | Required? | Size | Synced? | Safe to delete? | Regenerate command | Notes |
|---|---|---|---|---:|---:|---:|---:|---|---|
| | | hot/cold/scratch/durable | R0/R1/R2/final | yes/no | | no | yes/no | | |

## Machine-Specific Paths

| Resource | `primary-heavy` path | `office-desktop` path | `portable-laptop` path | other/unknown path | Last verified |
|---|---|---|---|---|---|
| | | | | | |

## Environment Variables

| Variable | Meaning | Example |
|---|---|---|
| `PROJECT_DATA_ROOT` | Root of large input data outside the project/shared source tree | `/mnt/d/datasets/<project>` |
| `PROJECT_CACHE_ROOT` | Root of generated cache/intermediate files | `/home/<user>/.cache/<project>` |
| `PROJECT_OUTPUT_ROOT` | Non-portable heavy output path | `/mnt/d/outputs/<project>` |
| `APK_CACHE_ROOT` | Kit extraction cache (`hot` tier, never synced) | `/home/<user>/.cache/agent-project-kit-cache` |
| `APK_PDF_FIGURE_CACHE` | PDF figure cache, if moved off the synced project | `/home/<user>/.cache/agent-project-kit-cache/pdf-figures/<project>` |

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
- Prefer small portable sample data in the project/shared source tree for smoke tests.
