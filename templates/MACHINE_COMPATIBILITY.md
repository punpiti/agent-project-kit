# MACHINE_COMPATIBILITY

ใช้สรุปว่า project นี้รันได้บนเครื่องไหน และข้อจำกัดคืออะไร

อ่านคู่กับ `.ai/MACHINE_PROFILE.md`: profile บอกว่าเครื่องและ storage layout เป็น
อะไร ส่วนไฟล์นี้บอกว่า project นี้ควรทำ task ระดับไหนบนเครื่องนั้น

## Machine Matrix

| Machine | Role for this project | Can edit? | Can run smoke test? | Can run full pipeline? | Required local resources | Notes |
|---|---|---:|---:|---:|---|---|
| `think` | default heavy-run | yes | yes | yes/unknown | | should be able to run all projects unless noted |
| `madlab-i9` | office machine | yes | yes/unknown | yes/no/unknown | | check cache/data availability |
| `black5` | portable notebook | yes | yes/unknown | no/unknown | | prefer light tasks unless resources exist |
| other | unknown | yes/unknown | unknown | unknown | | inspect first |

## Recommended Task Placement

- Heavy training / full data processing:
- Medium experiment:
- Light edit / document / review:
- Smoke test:
- Final artifact generation:

## Known Non-Portable Dependencies

- 

## Last Verified

| Date | Machine | What was verified | Result |
|---|---|---|---|
| | | | |
