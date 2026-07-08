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
