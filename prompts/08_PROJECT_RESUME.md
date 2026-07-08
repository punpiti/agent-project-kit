# 08 — Project Resume Prompt

ใช้เมื่อกลับมาเปิด project เดิมหลังจากสลับไปทำงานอื่นหลายวัน/หลายชั่วโมง

```text
อ่าน AGENTS.md และ .ai/computing-environment ก่อน
จากนั้นอ่านไฟล์ project state เหล่านี้ถ้ามี:
- .ai/PROJECT_STATE.md
- .ai/LOCAL_RESOURCES.md
- .ai/MACHINE_COMPATIBILITY.md
- .ai/RUNBOOK.md
- .ai/SESSION_LOG.md
- .ai/TOKEN_BUDGET.md

ให้ทำ Project Resume ตามนี้:

1. Current Machine / Environment
   - ตรวจว่าอยู่บนเครื่อง known compatible machine / unknown
   - ตรวจว่าอยู่ใน WSL2 หรือไม่ ถ้าทำได้
   - ตรวจว่า project อยู่บน shared/synced project storage หรือ path อื่น
   - ตรวจว่ามี local resource สำคัญที่หายไปหรือไม่

2. Where We Left Off
   - สรุปจาก PROJECT_STATE และ SESSION_LOG ว่าครั้งล่าสุดทำอะไรไปถึงไหน
   - ระบุ blocker และ next action ล่าสุด

3. Token-Efficient Next Step
   - เสนอ next action ที่ใช้ context น้อยที่สุดแต่ยังเดินงานได้
   - ระบุว่าควรใช้ T0/T1/T2/T3 mode

4. Risk Check
   - มีอะไรที่รันบนเครื่องนี้ไม่ได้หรือควรย้ายไป primary-heavy หรือไม่
   - มีอะไรที่ต้องถามผมก่อนจริง ๆ หรือไม่ ถ้ามีถามไม่เกิน 1–2 ข้อ

5. Proceed
   - ถ้า next action ชัด ให้ลงมือทำทันทีใน scope เล็ก
   - ถ้ายังไม่ชัด ให้เสนอ 2–3 ทางเลือก ไม่ต้องถามกว้าง ๆ

หลังจบ ให้ช่วยอัปเดต .ai/PROJECT_STATE.md และ .ai/SESSION_LOG.md แบบสั้น เพื่อประหยัด token รอบหน้า
```
