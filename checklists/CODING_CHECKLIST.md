# CODING_CHECKLIST

## Before Editing

- [ ] อ่าน `AGENTS.md` และ `.ai/computing-environment/`
- [ ] อ่าน `.ai/PROJECT_STATE.md` เพื่อรู้ว่าค้างตรงไหน
- [ ] อ่าน `.ai/LOCAL_RESOURCES.md` และ `.ai/MACHINE_COMPATIBILITY.md` ถ้า project มี data/cache/intermediate ใหญ่
- [ ] ตรวจ current machine: `think` / `madlab-i9` / `black5` / unknown
- [ ] ตรวจว่าอยู่ใน WSL2 หรือไม่ ถ้าทำได้
- [ ] อ่าน repo structure แบบ targeted ไม่ใช่ scan ทั้งหมดโดยไม่จำเป็น
- [ ] ระบุไฟล์ที่เกี่ยวข้อง
- [ ] เข้าใจ current behavior
- [ ] เขียน working spec
- [ ] ระบุ acceptance criteria
- [ ] ระบุ test/check ที่จะรัน
- [ ] ระบุ assumptions
- [ ] ระบุว่า task นี้ควรใช้ token mode T0/T1/T2/T3

## Local Resource / Portability Check

- [ ] Project source/docs/spec อยู่ใน OneDrive หรือ path portable ที่ตั้งใจไว้
- [ ] Cache/intermediate/data ใหญ่ไม่ได้ถูกใส่ OneDrive โดยไม่ตั้งใจ
- [ ] Non-OneDrive resources ถูกจดใน `.ai/LOCAL_RESOURCES.md`
- [ ] Path เฉพาะเครื่องถูกอ่านผ่าน env/config ไม่ใช่ hardcode
- [ ] มี smoke test ที่ไม่ต้องใช้ full cache/data ถ้าเป็นไปได้
- [ ] ถ้าจะรันหนัก ตรวจว่าเครื่องนี้เหมาะ หรือควรย้ายไปรันบน `think`

## During Editing

- [ ] แก้เป็นรอบเล็ก
- [ ] เปลี่ยนเท่าที่จำเป็น
- [ ] ไม่แก้ architecture ใหญ่โดยไม่บอก
- [ ] ไม่ hardcode path
- [ ] ไม่ใส่ magic number โดยไม่อธิบาย
- [ ] ไม่ลบหรือทำให้ test อ่อนลง
- [ ] run test/check เท่าที่ทำได้
- [ ] ถ้าอยู่บน `black5` หรือ resource ไม่ชัด ให้เริ่มจาก smoke test
- [ ] ถ้า local resource หาย อย่าสรุปว่า project พัง ให้สรุปว่า resource ไหน missing

## After Editing

- [ ] สรุปไฟล์ที่เปลี่ยน
- [ ] สรุป logic ที่เปลี่ยน
- [ ] บอก test/check ที่รัน
- [ ] บอกผล pass/fail
- [ ] บอกสิ่งที่ยังไม่ได้ทดสอบ
- [ ] บอก local resources ที่ใช้หรือ missing
- [ ] บอกว่าเครื่องนี้เหมาะกับ task นี้หรือไม่
- [ ] บอก risk ที่เหลือ
- [ ] บอก decision ที่ต้องให้มนุษย์ตัดสินใจ
- [ ] เสนอ next loop
- [ ] อัปเดตหรือเสนอ patch สำหรับ `.ai/PROJECT_STATE.md` และ `.ai/SESSION_LOG.md`
- [ ] ถ้าเจอ path/cache/data นอก OneDrive ใหม่ ให้ update `.ai/LOCAL_RESOURCES.md`
- [ ] ใส่ token note ว่ารอบหน้าควรอ่าน/ส่ง context อะไรเพื่อประหยัด token
