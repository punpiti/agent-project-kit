# 08 — Project Resume Prompt

ใช้เมื่อกลับมาเปิด project เดิมหลังจากสลับไปทำงานอื่นหลายวัน/หลายชั่วโมง

```text
อ่าน AGENTS.md และ .ai/computing-environment ก่อน
จากนั้นอ่านไฟล์ project state เหล่านี้ถ้ามี:
- .ai/PROJECT_STATE.md
- .ai/PROJECT_HIERARCHY.md
- .ai/COMPUTING_ENVIRONMENT_VERSION.md
- .ai/MACHINE_PROFILE.md
- .ai/LOCAL_RESOURCES.md
- .ai/MACHINE_COMPATIBILITY.md
- .ai/RUNBOOK.md
- .ai/SESSION_LOG.md
- .ai/TOKEN_BUDGET.md

ถ้า project นี้อยู่ใน parent/upper folder ที่เคย scan หรือมี state summary แล้ว:
- reuse parent summary, hierarchy note, shared constraint, และ machine profile
  เท่าที่เกี่ยวข้อง
- อย่า deep scan parent/upper folder ซ้ำ เว้นแต่งานแตะ parent โดยตรง
- อย่าแก้ parent files, parent .ai state, parent logs, หรือ sibling projects
  เว้นแต่ผมสั่งเป็น parent-level/cross-project change ชัดเจน
- สรุป child project จาก .ai/ ของ child เองให้ลึกกว่า parent: current objective,
  active files, task-specific evidence, blockers, และ next action

ให้ทำ Project Resume ตามนี้:

1. Current Machine / Environment
   - รายงาน Agent Project Kit package name/version จาก .ai/COMPUTING_ENVIRONMENT_VERSION.md
   - รายงาน last update check ถ้ามี และบอกว่าควรเช็ก update หรือไม่
   - ตรวจว่าอยู่บนเครื่อง known compatible machine / unknown
   - ตรวจว่าอยู่ใน WSL2 หรือไม่ ถ้าทำได้
   - ตรวจว่า project อยู่บน shared/synced project storage หรือ path อื่น
   - ตรวจว่ามี local resource สำคัญที่หายไปหรือไม่

2. Where We Left Off
   - สรุปจาก PROJECT_STATE และ SESSION_LOG ว่าครั้งล่าสุดทำอะไรไปถึงไหน
   - ระบุ blocker และ next action ล่าสุด
   - ถ้าเป็น child/subproject ให้แยก broad parent context ออกจาก sharp child state

3. Status / Deadline Dashboard
   - ถ้า project มี status/deadline/meeting/submission/review/class date ให้สรุปเป็น dashboard สั้น ๆ ก่อน:
     Priority, Due/Trigger, Status, Item, Evidence/Source, Next action
   - เรียงตาม deadline และความเสี่ยง ไม่ใช่เรียงตามไฟล์ที่เพิ่งอ่าน
   - ถ้า deadline ไม่ชัด ให้ใส่ unknown และบอกว่าต้องยืนยันจากแหล่งไหน

4. Token-Efficient Next Step
   - เสนอ next action ตาม priority/deadline ที่ใช้ context น้อยที่สุดแต่ยังเดินงานได้
   - ระบุว่าควรใช้ T0/T1/T2/T3 mode

5. Risk Check
   - มีอะไรที่รันบนเครื่องนี้ไม่ได้หรือควรย้ายไป primary-heavy หรือไม่
   - มีอะไรที่ต้องถามผมก่อนจริง ๆ หรือไม่ ถ้ามีถามไม่เกิน 1–2 ข้อ

6. Proceed
   - ถ้า next action ชัด ให้ลงมือทำทันทีใน scope เล็ก
   - ถ้ายังไม่ชัด ให้เสนอ 2–3 ทางเลือก ไม่ต้องถามกว้าง ๆ

หลังจบ ให้ช่วยอัปเดต .ai/PROJECT_STATE.md และ .ai/SESSION_LOG.md แบบสั้น โดยเฉพาะ
last session, status/deadline dashboard, และ next action by priority/deadline
เพื่อประหยัด token รอบหน้า
```
