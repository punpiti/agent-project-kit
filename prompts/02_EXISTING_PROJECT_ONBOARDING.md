# 02 — Existing Project Onboarding Prompt

ใช้กับ project ที่มีอยู่แล้ว และต้องการให้ AI เข้าใจระบบก่อนลงมือแก้

```text
อ่านกติกาจาก shared/synced project storage/computing-environment หรือจาก .ai/computing-environment ใน project นี้ก่อน
แล้ว onboard ตัวเองกับ project นี้ด้วย Spec–Eval–Loop Workflow + machine-aware multi-machine protocol

ให้คุณทำดังนี้:

1. Environment Inspect
   - ตรวจ current machine: known compatible machine / unknown
   - ตรวจว่าอยู่ใน WSL2 หรือไม่ ถ้าทำได้
   - ตรวจ path ของ project ว่าอยู่ใต้ shared/synced project storage หรือไม่
   - อ่าน .ai/LOCAL_RESOURCES.md และ .ai/MACHINE_COMPATIBILITY.md ถ้ามี
   - สรุปว่าเครื่องนี้เหมาะกับ full run / smoke test / edit-only หรือไม่

2. Project State Inspect
   - อ่าน .ai/PROJECT_STATE.md ถ้ามี
   - อ่าน .ai/SESSION_LOG.md ถ้ามี โดยดู entry ล่าสุด
   - อ่าน .ai/RUNBOOK.md และ .ai/TOKEN_BUDGET.md ถ้ามี
   - สรุปว่า project ค้างตรงไหน

3. Repository / Folder Inspect
   - อ่านโครงสร้าง repository / folder แบบ targeted ไม่ใช่ scan ทั้งหมดโดยไม่จำเป็น
   - ระบุไฟล์สำคัญ
   - ระบุ entry points
   - ระบุ test / build / run commands ที่พบ
   - ระบุเอกสาร spec เดิม ถ้ามี

4. Loop Diagnosis
   แยกว่า project นี้มี L1/L2/L3 อะไรบ้าง
   โดยเฉพาะส่วนไหนเป็น code execution, ส่วนไหนต้องใช้ human judgment, ส่วนไหนต้องใช้ external feedback
   ถ้า project นี้เป็น child/subproject ให้ประเมิน loops จาก local objective,
   active files, evidence, blockers, และ next action ของ child ก่อน แล้วค่อยใช้
   parent เป็น broad framing/shared constraint

5. Current Working Spec
   สรุปว่า project นี้น่าจะทำอะไร
   ผู้ใช้คือใคร
   ขอบเขตคืออะไร
   assumption ของคุณคืออะไร

6. Existing Evals
   ระบุว่า project มี test/check/eval อะไรอยู่แล้ว
   และยังขาด eval อะไร

7. Risk Map
   - technical risk
   - data/local resource risk
   - machine portability risk
   - UX/user risk
   - academic/evidence risk
   - stakeholder risk
   ตามลักษณะ project

8. Next Action
   เสนอ 3 ทางเลือก:
   A. safe small improvement / token-light
   B. useful medium change
   C. deeper run/refactor/reanalysis อาจต้องใช้ primary-heavy หรือ local resources

อย่าแก้ไฟล์ก่อนสรุป onboarding ยกเว้นผมสั่งให้ลงมือทันที
ถ้าพบ cache/intermediate/data นอก shared/synced project storage ที่ไม่ได้จด ให้เสนอ patch สำหรับ .ai/LOCAL_RESOURCES.md
```
