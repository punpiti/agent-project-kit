# Prompt: Document Production Workflow

Use this when creating formal documents, reports, public PDFs, teaching handouts, or other written artifacts.

```text
งานนี้ให้ใช้ Document Production Workflow แบบ Markdown-first

เป้าหมาย:
- เริ่มจาก Markdown เป็น source of truth
- ปรับ content จน logic, structure, audience fit, evidence, tone ดีพอ
- แล้วค่อยสร้าง PDF หรือ output final
- ไม่ให้ต้องสั่งซ้ำบ่อย ให้ทำเป็น loop ที่ครบเท่าที่ทำได้

ก่อนลงมือให้ทำ:
1. Loop Diagnosis: L1/L2/L3 ของงานนี้คืออะไร
2. Working Spec: เอกสารนี้ทำเพื่อใคร ใช้ทำอะไร เป็น formal/public/teaching/internal
3. Document Style: A4 หรือ 16:9, font, color, table style, output path
4. Acceptance Criteria / QA: content + layout + final PDF checks

กติกาเอกสาร:
- ถ้าเป็นงานเอกสารทางการ: Thai text ใช้ TH Sarabun New; English ใช้ modern thin/light sans-serif หรือ fallback ที่ระบุ
- ถ้าเป็นเอกสารเผยแพร่: ใช้ฟอนต์ทันสมัย minimal ตัวบาง อ่านง่าย
- ใช้สีแบบ minimal แต่มีสีสรรค์พอควร
- โปรเจคเดียวกันใช้ stylesheet/template เดียวกัน
- เอกสารกระดาษใช้ A4
- เอกสารสำหรับจอภาพใช้ 16:9

Workflow:
1. สร้าง/แก้ Markdown ก่อน
2. critique content หนึ่งรอบก่อน layout
3. อัปเดต Markdown จนพร้อม
4. สร้าง PDF/output
5. ทำ final QA:
   - spell/typo
   - Thai word break
   - table autofit/wrap
   - no hanging title
   - no bad hanging line/orphan/widow
   - captions stay with figures/tables
   - final PDF opens and fits target
6. อัปเดต .ai/DOCUMENT_PIPELINE.md และ .ai/DOCUMENT_QA.md

ถ้ายังสร้าง PDF ไม่ได้ ให้บอกตรง ๆ ว่าขาด dependency/font/tool อะไร และยังต้องทำอะไรต่อ
อย่าบอกว่า final ถ้ายังไม่ได้ตรวจ PDF จริง
```
