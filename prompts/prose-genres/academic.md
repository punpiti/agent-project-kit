# Prose Genre Overlay — Academic (paper, thesis, proposal, technical report)

ใช้ร่วมกับ `prompts/24_PROSE_STYLE.md` เสมอ ไฟล์นี้เพิ่มเฉพาะชั้นตรวจของงานวิชาการ
Checker profile: `python3 scripts/check_prose_style.py FILE --profile academic`
(รายงาน `review` candidates ของวลี artifact/meta-writing ด้วย)

## A. Scientific-reporting and trust gate สำหรับงานวิชาการ

ใช้ส่วนนี้กับ paper, thesis, proposal, technical report และข้อความที่รายงานวิธีหรือผล
เป้าหมายไม่ใช่การซ่อนว่าใช้ AI แต่คือทำให้ต้นฉบับ self-contained, ตรวจสอบได้ และไม่ใช้
provenance ของไฟล์หรือโค้ดแทนเหตุผลทางวิทยาศาสตร์

1. **Methods ทุกประโยคต้องมีหน้าที่ทางวิทยาศาสตร์** อย่างน้อยหนึ่งอย่าง: ระบุข้อมูลเข้า,
   การแปลง/การคำนวณ, พารามิเตอร์หรือเกณฑ์, เหตุผลรองรับ, หรือผลผลิตที่นำไปวิเคราะห์ต่อ
2. **ใช้ชื่อวัตถุจริงแทนชื่อ artifact ภายใน** เช่น `reconstructed rainfall fields` หรือ
   `storm-level indicators` แทน `analysis cache`, `stored metrics` หรือชื่อ notebook
   เว้นแต่ artifact นั้นเป็นส่วนของ reproducibility contract ที่ผู้อ่านต้องเข้าถึงจริง
3. **อย่าใช้ provenance เป็น justification** การพบค่า threshold ใน workflow, archive,
   notebook หรือโค้ดเดิมบอกเพียงที่มา ถ้ายังไม่มี calibration หรือหลักฐานทางวิทยาศาสตร์
   ให้เรียกค่าตามหน้าที่จริง เช่น `historical input-error screen` และบอกข้อจำกัดครั้งเดียว
4. **ต้นฉบับต้องอธิบายวิธีที่จำเป็นได้เอง** ห้ามฝากสาระไว้กับ notebook, repository,
   caption หรือ supplement โดยไม่บอกขั้นตอนและพารามิเตอร์ขั้นต่ำใน Methods
5. **caption อธิบายรูป; Methods อธิบายวิธี** ตัดประโยคชี้ทาง เช่น “its caption
   summarizes the sequence” แล้ววางสาระไว้ในส่วนที่ผู้อ่านคาดว่าจะพบ
6. **แยก reproducibility ออกจาก validity** การรันซ้ำได้, มี cache ครบ หรือมี lineage
   ไม่ได้พิสูจน์ว่า reconstruction, anchoring, optical flow, threshold หรือการตีความเหมาะสม
7. **ตรวจ lineage ก่อนเกลาภาษา** ถ้าวิธีหรือพารามิเตอร์เปลี่ยน ให้เชื่อม input → setting →
   derived field/metric → figure/table/claim และคำนวณผลกระทบปลายน้ำใหม่ก่อน rewrite
8. **ใช้คำเรียกคงที่ตาม data model** ทำ terminology map สำหรับข้อมูลดิบ, ข้อมูลหลัง QC,
   reconstructed fields, analysis windows, indicators, classes และ validation evidence
9. **แยก operational definition จาก independent validation** การจัดกลุ่มด้วยกฎภายใน
   บอกผลของกฎนั้น ส่วนความถูกต้องทางกายภาพหรือ meteorological skill ต้องใช้หลักฐานอิสระ
10. **แยก AI disclosure จาก Methods** disclosure ระบุชื่อเครื่องมือ วัตถุประสงค์ ขอบเขต
    และความรับผิดชอบของผู้เขียน ส่วน Methods ต้องยืนได้ด้วยข้อมูล เหตุผล และหลักฐานของวิธีเอง

ก่อนผ่าน gate ให้ตอบคำถามต่อไปนี้จากข้อความในต้นฉบับได้โดยไม่เปิดไฟล์ทำงานภายใน:

| คำถาม | หลักฐานที่ควรอยู่ในต้นฉบับ |
|---|---|
| ใช้ข้อมูลอะไร | ชนิด แหล่ง ช่วงเวลา หน่วย ขอบเขต และข้อจำกัดที่มีผลต่อการตีความ |
| ทำอะไรกับข้อมูล | ลำดับการประมวลผลที่เปลี่ยนข้อมูลหรือสร้างตัวชี้วัด |
| ใช้ค่าใดและเพราะอะไร | ค่า พิสัย/หน่วย บทบาท และฐานสนับสนุนหรือสถานะว่าไม่ได้ calibrate |
| ได้ผลผลิตอะไร | ชื่อวัตถุจริงที่เชื่อมต่อกับผล รูป ตาราง หรือ claim |
| วิธีเปลี่ยนแล้วผลใดต้องคำนวณใหม่ | lineage และ impact/sensitivity check ของผลปลายน้ำ |
| อะไรเป็นเพียง operational grouping | ขอบเขต claim และ independent evidence ที่ยังขาด |

บทเรียนด้านหลักฐาน: editor อาจตั้งข้อกังวลเรื่อง methodology และการใช้ AI ขณะที่ public
review วิจารณ์ภาษาและวิธีโดยไม่ระบุว่าประโยคใดสร้างด้วย AI ได้ ห้ามรวมหลักฐานสองชุดนี้
เป็นคำกล่าวว่า reviewer “ตรวจพบ AI จากสำนวน” ถ้าไม่มีข้อความนั้นโดยตรง รูปแบบภาษาและ
คำศัพท์ภายในเป็นสัญญาณให้ตรวจความชัดเจนและความน่าเชื่อถือ ไม่ใช่เครื่องพิสูจน์ผู้เขียนหรือเครื่องมือ

## B. Scientific pre-pass สำหรับงานวิชาการ

1. **ตรึง evidence boundary** แยกสิ่งที่ source กล่าวโดยตรง ข้ออนุมาน และสิ่งที่ยังไม่ทราบ
2. **ทำ method/lineage pass ก่อน style pass** ตรวจ input → processing → parameter → output → claim;
   ถ้ามีวิธีเปลี่ยน ให้ตรวจผลปลายน้ำก่อนล็อกเนื้อหา
3. **ทำ artifact/provenance pass** แทนคำภายในด้วยวัตถุจริง และเติม scientific justification
   หรือระบุสถานะ operational/uncalibrated อย่างตรงไปตรงมา
4. เมื่อ pre-pass พบปัญหา ให้แก้หรือรายงานแยกก่อนล็อกเนื้อหา ห้ามกลบปัญหาด้วย style edit

## C. รายงานผล

สำหรับงานวิชาการ ให้รายงานผล scientific pre-pass แยกจาก pattern counts และอ่าน `review`
candidates ทุกจุด ถ้า style pass พบปัญหาเนื้อหา ให้ย้อนกลับไป method/lineage pass
