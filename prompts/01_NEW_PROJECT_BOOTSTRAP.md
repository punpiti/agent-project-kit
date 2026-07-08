# 01 — New Project Bootstrap Prompt

ใช้เมื่อต้องเริ่ม project ใหม่

```text
อ่านกติกาจาก shared/synced project storage/computing-environment หรือจาก .ai/computing-environment ใน project นี้ก่อน
แล้วเริ่ม project นี้ด้วย Spec–Eval–Loop Workflow + machine-aware multi-machine protocol

โจทย์โปรเจกต์:
[ใส่โจทย์ตรงนี้]

ให้คุณทำดังนี้:

1. Environment / Machine Setup
   - ตรวจว่าอยู่บนเครื่อง known compatible machine / unknown
   - ตรวจว่าอยู่ใน WSL2 หรือไม่ ถ้าทำได้
   - ตรวจว่า project อยู่ใน shared/synced project storage หรือ path อื่น
   - เสนอว่าจะเก็บ source, final docs, sample data, cache/intermediate, output ใหญ่ไว้ที่ไหน

2. Loop Diagnosis
   แยกว่า project นี้มี L1/L2/L3 อะไรบ้าง

3. Project Working Spec
   - objective
   - target users/readers
   - scope
   - non-goals
   - constraints
   - assumptions

4. Architecture / Work Breakdown
   ถ้าเป็นโค้ด ให้เสนอ structure, modules, data flow, tests, local resource strategy
   ถ้าเป็นเอกสาร ให้เสนอ outline, argument flow, evidence needed
   ถ้าเป็นสไลด์ ให้เสนอ storyline, sections, learning/persuasion flow

5. Evals / Acceptance Criteria
   ระบุเกณฑ์วัดว่า version แรกผ่านหรือไม่

6. Project State Files
   ถ้ายังไม่มี ให้สร้างหรือเสนอเนื้อหาไฟล์:
   - .ai/PROJECT_STATE.md
   - .ai/LOCAL_RESOURCES.md
   - .ai/MACHINE_COMPATIBILITY.md
   - .ai/RUNBOOK.md
   - .ai/TOKEN_BUDGET.md
   - .ai/SESSION_LOG.md

7. First Execution Plan
   แตกงานเป็นรอบเล็ก ๆ ที่ AI ทำได้ทันที

8. Review Gate
   บอกชัดว่าอะไรต้องให้ผมตัดสินใจ อะไรต้องรอ feedback จริง และอะไรควรรันบน primary-heavy เท่านั้น

อย่าลงมือ implement ใหญ่ทันทีถ้า spec/eval/local resource ยังไม่ชัด
แต่ถ้าโจทย์ชัดพอ ให้เริ่มทำ draft/prototype รอบแรกได้เลย
```
