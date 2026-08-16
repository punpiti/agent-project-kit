# PORTFOLIO_COORDINATION

ใช้ไฟล์นี้เป็น Project Radar กลางเพื่อเห็นว่า project ไหนยังค้าง หรือไม่ได้
ทบทวนนานเกินไป. เก็บไว้ใน personal work hub เพียงแห่งเดียว ไม่ใช่ `.ai/` ของทุก
project. `.ai/PROJECT_STATE.md` ของแต่ละ project ยังคงเก็บรายละเอียดภายใน project.

## Rules

- หนึ่งแถวต่อ project ที่ `active`, `waiting`, `blocked`, หรือ `parked`
- เก็บเฉพาะวันทบทวนล่าสุด, สถานะ, งานค้างหนึ่งเรื่อง, และ next action
- รายละเอียด งานย่อย หลักฐาน และ log อยู่ใน project เดิม ไม่ copy มาที่นี่
- `unknown` ดีกว่าเดาสถานะหรือวัน
- weekly review: flag ทุกแถวที่ `Last reviewed` เกิน 14 วัน แล้วตัดสินใจว่า
  project นั้นยัง active, blocked, intentionally parked, หรือถูกลืม
- ลบแถวได้ต่อเมื่อ project จบจริง; `parked` ให้คงไว้เพื่อไม่ลืมว่าตั้งใจพัก

## Project Pulse

| Project | Current state | Last reviewed | One open loop to clear | Next return action | Priority |
|---|---|---|---|---|---:|
|  | active / waiting / blocked / parked | YYYY-MM-DD / unknown |  |  | P0 / P1 / P2 |

## Weekly review questions

- Which row has not been reviewed for 14+ days?
- Is each old row intentionally parked, blocked, still active, or forgotten?
- What is the one next action for the highest-priority open row?
