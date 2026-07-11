# COMPUTING_ENVIRONMENT_VERSION

บันทึก version ของ Agent Project Kit ที่ติดตั้งใน project นี้

ชื่อ package ปัจจุบันคือ `agent-project-kit`; ชื่อ/path เดิม
`computing-environment` และ `.ai/computing-environment/` ยังรองรับเพื่อ
compatibility

ไฟล์นี้เป็น metadata ของ package ที่ติดตั้ง ไม่ใช่ project state หลัก สามารถ
overwrite ได้ตอน update package โดยไม่ต้องลบหรือสร้างใหม่:

- `.ai/MACHINE_PROFILE.md`
- `.ai/LOCAL_RESOURCES.md`
- `.ai/MACHINE_COMPATIBILITY.md`
- `.ai/PROJECT_STATE.md`
- `.ai/RUNBOOK.md`
- `.ai/SESSION_LOG.md`

## Installed Package

- Package name:
- Package display name:
- Legacy package names:
- Package version:
- Package updated:
- State schema version:
- Machine profile schema version:
- Previous package version:
- Previous machine profile schema version:
- Installed/updated:
- Update check cadence: report installed version every startup; check upstream
  when last check is missing, older than 14 days, before package-level/release
  work, or when explicitly asked
- Last update check:
- Latest known upstream version:
- Update check source:
- Source path:
- Installer:
- Machine:
- Platform:

## Update Rule

ถ้า package version เปลี่ยน แต่ `machine_profile_schema_version` ยังเท่าเดิม ให้
reuse `.ai/MACHINE_PROFILE.md` เดิมได้ ไม่ต้อง rerun first-use discovery

ถ้า `machine_profile_schema_version` เปลี่ยน ให้ migrate/update
`.ai/MACHINE_PROFILE.md` ตาม template ใหม่ แต่ยังไม่ควรลบทิ้งหรือสแกนใหม่ทั้งหมด
เว้นแต่ field สำคัญหายหรือเครื่อง/path layout เปลี่ยน

ถ้า `state_schema_version` เปลี่ยน ให้ตรวจ template ใหม่และเติม field ที่ขาดลงใน
project-local state files แบบ preserve existing content

## Update Check Rule

ทุกครั้งที่ resume project ให้รายงาน installed package:

- Package display name
- Package name
- Package version
- Installed/updated

ไม่ต้อง fetch/pull ทุกครั้ง ให้เช็ก upstream เป็นช่วง ๆ:

- ถ้า `Last update check` ว่าง
- ถ้าเช็กครั้งล่าสุดเกิน 14 วัน
- ก่อนทำ package-level work, release, migration, หรือ self-install refresh
- เมื่อผู้ใช้ถามเรื่อง version/update

ถ้ามี version ใหม่ ให้สรุปก่อนว่า package version, state schema, และ machine
profile schema เปลี่ยนหรือไม่ แล้วค่อยเสนอ update path
