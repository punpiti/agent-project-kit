# 04 — Paper / Reviewer Response Stage

ใช้กับ paper, manuscript, reviewer response, proposal, report, academic document

```text
งานนี้ใช้ Spec–Eval–Loop Workflow
เน้น paper / reviewer response / academic document

ก่อนแก้ ให้แยกว่า problem เป็นอะไร:
- language problem
- logic problem
- evidence problem
- positioning problem
- reviewer trust problem
- scope / limitation problem

อย่าแก้แค่ภาษา ถ้า argument ยังอ่อน

ให้ทำดังนี้:

1. Loop Diagnosis
   L1 = AI ช่วยร่าง/แก้/จัดตาราง
   L2 = ต้องใช้ academic judgment/context ของผม
   L3 = reviewer/editor/reader feedback หรือ evidence จริง

2. Concern Mapping
   ทำตาราง:
   - reviewer/reader concern
   - actual problem
   - required change
   - where to change
   - evidence needed
   - risk if not addressed
   แยก source boundary ทุกครั้ง:
   - editor statement
   - public reviewer comment
   - confidential comment ที่มีข้อความให้ตรวจจริง
   - author/agent inference
   ห้ามรวมข้อความจากคนละแหล่งเป็นข้อสรุปว่า reviewer ตรวจพบ AI หรือเจตนาของผู้เขียน
   ถ้า source ไม่ได้กล่าวเช่นนั้นโดยตรง

3. Revision Strategy
   ระบุว่าควรแก้ manuscript, response letter, experiment, figure, table หรือ framing

4. Draft / Rewrite
   เขียนข้อความที่แก้จริง โดยคุม:
   - claim ไม่แรงเกิน evidence
   - contribution ชัด
   - limitation ซื่อสัตย์แต่ไม่ทำลายงานตัวเอง
   - tone สุภาพแต่ไม่ยอมรับผิดเกินจริง
   - Methods รายงาน data → processing → parameter/justification → output โดยไม่ใช้
     notebook/cache/archive/workflow provenance แทน scientific justification
   - แยก reproducibility, methodological validity และ independent validation
   - ถ้าวิธีเปลี่ยน ให้ตรวจ lineage และ recompute/assess ผลปลายน้ำก่อนเกลาภาษา
   - AI disclosure ระบุเครื่องมือ/วัตถุประสงค์/ความรับผิดชอบแยกจากเหตุผลรองรับวิธี

   Rebuttal writing contract
   (adapted from the Nature Methods Editorial, "How to write a rebuttal letter",
   https://doi.org/10.1038/s41592-026-03261-0; journal-specific instructions
   override this default):

   Structure and traceability
   - เปิดหน้าแรกด้วย bullet list สั้นๆ ของ major revisions และต้องรวม
     ประเด็นที่ editor เน้นโดยตรง
   - ตอบแบบ point-by-point โดยคัดลอก reviewer/editor comment แต่ละข้อ
     ตามต้นฉบับ (verbatim) ให้ครบ ห้ามตัดทิ้ง และให้ใส่เลขข้อถ้าต้นฉบับยังไม่มี
   - แยก reviewer comment กับ author response ให้เห็นชัดด้วย style
     ที่ต่างกัน เช่น bold/normal หรือ italic/non-italic
   - ทุกคำตอบต้องระบุให้ตรวจกลับได้ว่า (a) ทำอะไร (b) หลักฐาน/ผลคืออะไร
     และ (c) เปลี่ยนที่ใดด้วย page/line/section/figure/table/supplement locator
   - ไม่ต้องคัดลอกข้อความที่แก้ทั้งหมดมาใส่ rebuttal; ยกเฉพาะข้อความสั้นที่จำเป็น
     แล้วชี้ locator ที่แม่นยำ
   - ทำให้ revision ทั้งใน manuscript และ supplementary files สังเกตได้ง่าย
     ตามวิธีที่วารสารกำหนด เช่น tracked changes หรือสีข้อความ

   Concision and interpretation
   - อธิบายการแก้ให้พอตรวจได้ แต่ตัดคำขอบคุณซ้ำๆ และข้อความที่ไม่ช่วย
     ให้พิจารณาประเด็นทางวิทยาศาสตร์
   - ห้าม paraphrase reviewer comment แทนต้นฉบับ; ถ้าข้อความกำกวม ให้ระบุความไม่แน่ใจ
     แล้วบอก interpretation ที่ใช้ตอบอย่างตรงไปตรงมา
   - ถ้าหลาย reviewer ถามประเด็นเดียวกัน ให้ตอบเต็มครั้งเดียว แล้ว cross-reference
     ด้วย reviewer number + point number หรือ rebuttal page; อย่าคัดลอกคำตอบซ้ำ

   Disagreement, infeasible requests, and trust
   - ห้ามเมิน reviewer comment แม้ไม่เห็นด้วย; ให้ตอบข้ออ้างนั้นโดยตรง ใช้เหตุผล
     และหลักฐาน และรักษา tone แบบ professional/measured
   - ห้ามสื่อว่า reviewer ขาดความรู้ ฉลาดน้อย หรืออ่านไม่รอบคอบ; ถ้ากังวลเรื่อง
     misunderstanding หรือ bias ที่ร้ายแรง ให้เตรียมหลักฐานและขอคำแนะนำจาก editor ก่อน
   - ถ้าทำ experiment/analysis ตามขอไม่ได้ หรือเห็นว่าไม่ช่วยยกระดับ paper ให้อธิบาย
     practical barrier หรือ scientific rationale ให้เฉพาะเจาะจง และระบุสิ่งที่ทำแทนถ้ามี
   - ถ้าใส่ figure/data "for reviewers only" ต้องอธิบายว่าเหตุใดจึงไม่รวมใน manuscript
     หรือ supplementary file; ห้ามปล่อยให้ดูเหมือนหลบเลี่ยงการแก้ paper

   Public-record and rights check
   - ถ้าวารสารใช้ transparent peer review ให้ถือว่า rebuttal อาจเป็นเอกสารสาธารณะ:
     ห้ามวาง figure จากงานตีพิมพ์อื่นโดยตรง; ให้ cite และ link ไปยัง figure นั้น
   - ทำ confidentiality/copyright check ก่อนส่ง และระบุส่วนที่ต้องขอให้วารสาร redact
     ตามกระบวนการของวารสาร; อย่าลบเองจนทำให้ scientific record ไม่ครบ

   Operational completion test
   (ข้อกำหนดต่อไปนี้เป็น author/agent inference ที่แปลงหลักการข้างต้นให้ตรวจได้
   ไม่ใช่คำสั่งโดยตรงของ Nature Methods)
   - ให้แต่ละ point มี primary disposition ที่ชัดเจน: changed / clarified / added evidence /
     disagreed with rationale / unable with justification / cross-referenced
   - ถ้าเป็น changed, clarified, หรือ added evidence ต้องมี locator
   - ถ้าเป็น disagreed หรือ unable ต้องมีเหตุผล/หลักฐาน และผลต่อ claim/scope ของ paper
   - ถ้าเป็น cross-referenced ต้องชี้จุดปลายทางที่แน่นอน
   - ห้ามปิด point ด้วยคำขอบคุณหรือข้อยืนยันลอยๆ โดยไม่มี action, evidence,
     locator, cross-reference, หรือ reasoned justification

5. Self-Critique
   critique ร่างตัวเองหนึ่งรอบ:
   - ยังมีช่องให้ reviewer โต้แย้งตรงไหน
   - evidence พอไหม
   - wording เสี่ยงไหม
   - จำนวนข้อความต้นฉบับกับจำนวน point ใน rebuttal ตรงกันหรือไม่
   - editor-specific points ปรากฏทั้งใน major-revision summary และคำตอบรายข้อหรือไม่
   - locator ทุกจุดตรงกับ revised files จริงหรือไม่
   - cross-reference ทุกจุดมีปลายทางที่มีคำตอบสมบูรณ์หรือไม่
   - มีข้อความ ภาพ หรือข้อมูลที่เสี่ยงต่อ copyright/confidentiality หากถูกเปิดเผยหรือไม่

6. Review Gate
   ระบุว่าจุดไหนต้องให้ผมตัดสินใจ
   จุดไหนต้องใช้ข้อมูล/ผลทดลองเพิ่ม
```
