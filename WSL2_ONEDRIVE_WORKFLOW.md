# WSL2_ONEDRIVE_WORKFLOW

แนวทางนี้ออกแบบสำหรับการใช้ Codex / coding agent ใน WSL2 โดย source project อยู่ใน OneDrive ฝั่ง Windows และมีเครื่องหลายเครื่อง sync ข้อมูลแบบเดียวกัน

## Recommended Mental Model

ให้แยก project ออกเป็น 3 ชั้น:

1. **Portable Layer** — sync ผ่าน OneDrive
   - code
   - documents
   - prompts
   - small examples
   - `.ai/PROJECT_STATE.md`
   - `.ai/LOCAL_RESOURCES.md`
   - `.ai/MACHINE_COMPATIBILITY.md`

2. **Machine-Local Layer** — อยู่เฉพาะเครื่อง
   - virtualenv
   - build artifacts
   - cache
   - intermediate results
   - model checkpoints
   - temporary datasets

3. **External Feedback / Final Artifact Layer**
   - reviewer feedback
   - student/user feedback
   - final paper figures
   - submitted reports
   - release builds

AI ต้องรู้ว่ากำลังแตะชั้นไหนอยู่

## WSL2 Path Examples

OneDrive จาก Windows มักอยู่ประมาณนี้ใน WSL2:

```bash
/mnt/c/Users/<windows-user>/OneDrive/computing-environment
/mnt/c/Users/<windows-user>/OneDrive - <organization>/computing-environment
```

ถ้าใช้ HDD อื่น อาจเป็น:

```bash
/mnt/d/project-cache/<project-name>
/mnt/e/datasets/<project-name>
```

ถ้าใช้ WSL-local ext4:

```bash
/home/<wsl-user>/project-cache/<project-name>
/home/<wsl-user>/.cache/<project-name>
```

## Performance Note

การรันงานที่มีไฟล์ย่อยจำนวนมากผ่าน `/mnt/c/...` อาจช้ากว่า WSL-local filesystem โดยเฉพาะ build, package install, node_modules, virtualenv, image cache, ML intermediate files

ดังนั้น:

- Keep source and final docs in OneDrive.
- Keep heavy cache/intermediate outside OneDrive.
- Record non-OneDrive paths in `.ai/LOCAL_RESOURCES.md`.
- Use small smoke tests that do not require full cache.

## Project Start Protocol

เมื่อเริ่มงานใน project:

```text
อ่าน AGENTS.md และ .ai/computing-environment ก่อน
จากนั้นอ่าน .ai/PROJECT_STATE.md, .ai/MACHINE_PROFILE.md, .ai/LOCAL_RESOURCES.md, .ai/MACHINE_COMPATIBILITY.md, .ai/RUNBOOK.md
ตรวจว่าเครื่องนี้คือ think / madlab-i9 / black5 / unknown
สรุปว่าเครื่องนี้เหมาะกับ task นี้หรือไม่ ก่อนรันงานหนัก
```

ถ้า project ที่เปิดอยู่คือ `computing-environment` เอง ให้ใช้ root-level files
เป็น source of truth และถือว่า `.ai/computing-environment/` เป็น snapshot ที่
เอาไว้ทดสอบการติดตั้งลง project อื่น ไม่ใช่ context ใหม่ที่ต้องอ่านซ้อนต่อ
เว้นแต่ผู้ใช้สั่งให้ตรวจ packaged copy โดยตรง

## Machine Profile Cache

ชุดนี้ออกแบบสำหรับ workflow หลักของผู้ใช้ที่อยู่บน Windows OneDrive และเปิด
ผ่าน WSL2 แต่ project อาจถูกย้ายไป Windows-native, macOS, Linux server,
container, หรือ cloud-synced folder แบบอื่นได้ ดังนั้นห้าม assume ว่า path แบบ
`/mnt/c/...` หรือ OneDrive มีอยู่เสมอ

ให้ใช้กติกา 2 ระดับ:

1. **เครื่องใหม่หรือ layout ใหม่** — ตรวจละเอียดและบันทึกใน
   `.ai/MACHINE_PROFILE.md` ก่อนรันงานหนัก
2. **เครื่องเดิมที่เคยบันทึกแล้ว** — ตรวจขั้นต่ำแค่ hostname/platform/current
   path แล้ว reuse profile เดิม จากนั้นตรวจเฉพาะ local resource ที่ task นี้ต้องใช้

ถ้า hostname ตรง แต่ path style, OS, sync folder, หรือ mount point เปลี่ยน ให้ถือว่า
profile stale และ refresh profile ก่อนสรุปว่า project ใช้ได้หรือใช้ไม่ได้

เวลา update package ใน project เดิม ให้ดู `.ai/COMPUTING_ENVIRONMENT_VERSION.md`
ก่อน ถ้า package version เปลี่ยนแต่ machine profile schema ยังเท่าเดิม ให้ update
เฉพาะ `.ai/computing-environment/` และ version metadata โดยไม่ต้องตรวจเครื่องใหม่
ทั้งหมด

## When Local Resources Are Missing

ถ้า path ภายนอก OneDrive ไม่พบ:

1. อย่า assume ว่าข้อมูลหายถาวร
2. ตรวจ `.ai/LOCAL_RESOURCES.md` ก่อน
3. สรุปว่าทรัพยากรไหน missing บนเครื่องนี้
4. เสนอทางเลือก:
   - run light/smoke test only
   - regenerate cache
   - change `PROJECT_DATA_ROOT` / `PROJECT_CACHE_ROOT`
   - move task to `think`
   - ask user to connect/mount HDD

## Avoid

- อย่าใส่ cache ใหญ่ใน OneDrive โดยไม่ตั้งใจ
- อย่า commit path เฉพาะเครื่องลง code
- อย่าให้ notebook/script ใช้ absolute path เฉพาะเครื่องโดยไม่มี env var
- อย่าสรุปว่า project ใช้ไม่ได้ถ้าแค่ local cache ยังไม่พร้อมบนเครื่องปัจจุบัน
