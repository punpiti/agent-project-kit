# คู่มือเริ่มโครงการเขียนหนังสือใหม่

ใช้ไฟล์นี้เป็น checklist ก่อนสร้าง `chapter.md` หรือ `prose.md` สำหรับหนังสือ
เล่มใหม่ โดยให้ Agent Project Kit รุ่นปัจจุบันเป็น workflow หลัก และเก็บวิธีเดิม
ไว้เป็น baseline จนกว่าจะตรวจ migration เสร็จ

## หลักการ

- เริ่มจากการกำหนดหนังสือและผู้อ่าน ไม่เริ่มจากการเขียน prose ทันที
- ใช้ Markdown และไฟล์โครงสร้างของหนังสือเป็น source of truth
- ค่าหรือข้อกำหนดที่ยังไม่รู้ให้ใส่เป็น template แล้วถามผู้เขียนว่า
  **“มีข้อมูลนี้ไหม และอยู่ที่ไหน”**
- ห้ามยืม outline, style, path, citation code หรือ production setting จากหนังสือ
  เล่มอื่นโดยไม่ระบุว่าเป็นการตัดสินใจใหม่
- preview ทำได้ระหว่างทาง แต่ pagination และ publication package เป็นงานท้ายเล่ม

## Phase 0: สร้างพื้นที่โครงการ

สร้างหรือยืนยันรายการต่อไปนี้:

- project root และ `.ai/PROJECT_STATE.md`
- `.ai/PROJECT_HIERARCHY.md`, `.ai/MACHINE_PROFILE.md` และ `.ai/LOCAL_RESOURCES.md`
  ตามความจำเป็น
- `BOOK_WRITING_PROFILE.md` โดยคัดลอกจาก `templates/BOOK_WRITING_PROFILE.md`
- `00_project_admin/` สำหรับ policy, checklist, audit และ decision log
- `02_manuscript/` หรือ manuscript root ที่ผู้เขียนเลือกเอง
- `references/` สำหรับ metadata, BibTeX, PDF, extracted cache และ figure index
- `90_outputs/` หรือ output root สำหรับ preview/build ที่ไม่ใช่ source of truth

ก่อนเริ่ม ให้ตรวจว่า project ใช้ APK รุ่นใด และอ่าน
`prompts/22_BOOK_WRITING.md` กับ profile รุ่นเดียวกัน

## Phase 1: กำหนดหนังสือและผู้อ่าน

บันทึกอย่างน้อย:

- ชื่อชั่วคราวและชื่อทางการถ้ามี
- เป้าหมายของหนังสือและสิ่งที่ผู้อ่านทำได้หลังอ่านจบ
- ผู้อ่านเป้าหมาย ความรู้ตั้งต้น ระดับความลึก ภาษา และน้ำเสียง
- ขอบเขต สิ่งที่ไม่ครอบคลุม และความยาวโดยประมาณ
- ความสัมพันธ์กับรายวิชา syllabus, slides, course outcomes หรือมาตรฐานใด
- เงื่อนไขทางวิชาการ เช่น การขอตำแหน่งวิชาการ การใช้ self-citation หรือการเปิดเผยที่มา

จากนั้น resolve profile ทั้งหมดและแสดงรายงาน meta/profile ให้ผู้เขียนตรวจ ก่อน
เริ่มทำ outline โดยรายงานต้องระบุ key, ค่า, สถานะ, แหล่งที่มา/locator และคำถามค้าง

## Phase 2: เตรียมคลังหลักฐาน

ทำ inventory ของแหล่งข้อมูลก่อนเขียน:

- syllabus, slides, lecture notes และเอกสารตั้งต้น
- หนังสือ ตำรา paper thesis report และเอกสารของผู้เขียน
- PDF ที่มีอยู่จริง พร้อม edition, DOI/URL, hash และสถานะสิทธิ์การใช้
- BibTeX หรือ metadata จาก DOI/OpenAlex และ abstract เมื่อหาได้
- ไฟล์ที่ดาวน์โหลดไม่ได้ ให้สร้างรายการ `manual-needed` พร้อม URL และเหตุผล

สำหรับ PDF ให้ extract text/Markdown ก่อนใช้เป็น reference และเก็บ locator เช่น
เลขหน้า หัวข้อ สมการ ตาราง และรูป หากมี figure ให้เก็บ caption และข้อความรอบรูป
พร้อมแยก raster หรือ render full page สำหรับ vector/multi-panel figure

ไฟล์ที่ควรมีอย่างน้อย:

- `references/manifest.*`
- `references/*.bib`
- `references/reading-cache/`
- `references/figures/INDEX.md`
- `references/SHA256SUMS` เมื่อมี corpus ที่ต้องควบคุมรุ่น

รูปจากแหล่งอ้างอิงใช้เป็น compositional reference เว้นแต่สิทธิ์อนุญาตให้เผยแพร่
ห้ามนำรูปที่ extract มาใส่หนังสือโดยอัตโนมัติ

## Phase 3: สร้างสถาปัตยกรรมหนังสือ

ทำเอกสารตามลำดับนี้:

1. **Book Master Outline** — ภาพรวมทั้งเล่ม บท และลำดับเหตุผล
2. **Chapter Plan / Detailed Chapter Outline** — จุดประสงค์ ขอบเขต หัวข้อย่อย
   หลักฐาน ตัวอย่าง สมการ รูป ตาราง และผลลัพธ์ที่ต้องการในแต่ละบท
3. **Evidence ledger** — mapping ระหว่าง claim/หัวข้อกับแหล่งหลักฐานและ locator
4. **`chapter.md`** — working file ที่ผ่าน evidence/depth/structure QA
5. **`prose.md`** — ร้อยแก้วสำหรับผู้อ่านที่เขียนจาก `chapter.md`

ถ้า outline หรือชื่อไฟล์เหล่านี้ยังไม่มี ให้สร้าง template และหยุดถามเฉพาะ
การตัดสินใจที่มีผลต่อโครงหนังสือ อย่าเดาจากหนังสือเล่มอื่น

## Phase 4: กำหนดระบบกลางทั้งเล่ม

ก่อนเขียนหลายบท ให้ตัดสินใจหรือทำ template สำหรับ:

- variables และสัญลักษณ์
- glossary และ English technical terms
- citation/reference codes และ cross-reference
- รูป ตาราง caption และ figure IDs
- visual tokens: font, palette, line weight, aspect ratio และ graphics engine
- ตัวอย่างคำนวณและรูปแบบกล่องเนื้อหา
- research integration: ใช้งานผู้เขียนเป็น case, evidence, comparison, limitation
  หรือ further reading โดยไม่ทำให้หนังสือกลายเป็นการประชาสัมพันธ์งานวิจัย
- frontmatter/backmatter และ metadata

ใช้ style เดียวกันทั้งเล่ม เว้นแต่ profile จะระบุเหตุผลที่บทหรือส่วนหนึ่งต้องต่างกัน

## Phase 5: ทดลองบทแรก

เลือกบทแรกหรือบทนำร่องหนึ่งบท แล้วทำวงจรสั้น:

1. ตรวจ detailed outline และ evidence ledger
2. เขียน `chapter.md`
3. ตรวจ depth, title–content, citations, variables, figures และ tables
4. เขียน `prose.md`
5. สร้าง preview เพื่อดูภาพรวม layout และการอ้างอิง
6. ให้ผู้เขียนตรวจ L2 และบันทึกข้อแก้ไข
7. ปรับ profile/method ก่อนขยายไปบทอื่น

หาก prose ยังไม่ครบทั้งเล่ม อนุญาตให้ preview ได้ แต่ให้ติดป้ายว่าเป็น draft และ
อย่าสรุปเลขหน้าหรือสารบัญท้ายเล่มเป็น final

## Phase 6: production package ตอนท้าย

เมื่อ prose ทุกบทผ่าน QA แล้วจึงจัดทำหรือ finalize:

- หน้าปก ปกหลัง หน้าชื่อเรื่อง และ metadata/copyright page
- คำนำ acknowledgement และวิธีใช้หนังสือ
- สารบัญ สารบัญภาพ สารบัญตาราง และบรรณานุกรม
- ภาคผนวก ดัชนี และไฟล์ส่งออกตาม format ที่ profile ระบุ

องค์ประกอบเหล่านี้อาจสร้างเป็น preview ได้ก่อน แต่ต้อง rebuild หลัง prose และ
ลำดับองค์ประกอบสุดท้าย เพราะมีผลต่อเลขหน้าและ cross-reference

## Definition of ready ก่อนขยายทั้งเล่ม

- profile ถูก resolve หรือมีคำถามค้างที่ผู้เขียนเห็นแล้ว
- master outline และ detailed outline ได้รับการยืนยัน
- reference corpus มี manifest และ locator ที่ย้อนกลับได้
- ระบบ variables, glossary, citation และ graphics ถูกกำหนด
- บทนำร่องผ่าน draft QA และมี feedback จากผู้เขียน
- แยก source, cache, preview และ final output ชัดเจน
- งานที่ยังเป็นข้อสมมติหรือรอผู้เขียนถูกบันทึกใน decision log

## Migration จาก workflow เดิม

เมื่อเริ่มจากโครงการที่มีไฟล์เก่า:

1. เก็บ profile, method, outline และ script เดิมไว้ใน `archive/` หรือ tag/commit
   ที่ระบุชัด
2. ทำ mapping ของไฟล์เดิมกับ contract ใหม่
3. คัดลอกเฉพาะข้อมูลที่ยืนยันแล้วเข้ารุ่นใหม่ ไม่ copy ทับทั้งไฟล์
4. รัน profile checker และแก้ทีละ contract
5. ทดลองกับหนึ่งบทก่อน commit migration

ห้ามลบ baseline จนกว่าจะตรวจว่า workflow ใหม่สร้างผลลัพธ์ที่ผู้เขียนยอมรับได้
