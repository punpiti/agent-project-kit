# 07 — External Feedback Prompt

ใช้เมื่อโปรเจกต์ต้องเอาไปลองกับคนจริง ข้อมูลจริง หรือ stakeholder จริง

```text
งานนี้ใช้ Spec–Eval–Loop Workflow
เน้น L3 = External Feedback Loop

ให้คุณช่วยออกแบบ feedback loop โดยเริ่มจาก:

1. Hypothesis
   เรากำลังเดาอะไรอยู่
   เช่น:
   - ผู้ใช้จะเข้าใจ flow นี้หรือไม่
   - นักเรียนจะทำโจทย์นี้ได้หรือไม่
   - reviewer จะเชื่อ metric นี้หรือไม่
   - stakeholder จะยอมรับ framing นี้หรือไม่

2. Feedback Source
   จะเก็บจากใคร:
   - user
   - student
   - reviewer
   - stakeholder
   - expert
   - usage log
   - survey
   - experiment
   - A/B test

3. Method
   จะเก็บอย่างไร:
   - interview
   - usability test
   - survey
   - classroom observation
   - log analysis
   - rubric scoring
   - reviewer-style critique
   - pilot deployment

4. Decision Rule
   feedback แบบไหนแปลว่าต้องแก้
   feedback แบบไหนเป็น preference
   feedback แบบไหนขัดกับ objective หลัก
   threshold หรือ criteria คืออะไร

5. Synthesis Template
   สรุป feedback เป็น:
   - must fix
   - should improve
   - monitor
   - ignore for now
   - update spec
   - need more data

6. Next Loop
   บอกว่าหลัง feedback แล้วควรกลับไปแก้ L1 หรือ L2 อย่างไร

ห้ามสรุปแทนผู้ใช้จริงจาก intuition อย่างเดียว
```
