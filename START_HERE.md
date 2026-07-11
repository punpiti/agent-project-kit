# START HERE — Agent Project Kit

Agent Project Kit is the current package identity. `computing-environment` is
the legacy-compatible folder/path name and remains supported.

Treat this folder as the single current source of truth.

For migration from old packages, read `MIGRATION_FROM_OLD.md`.

## Self-Hosting / Recursion Guard

When the current project is Agent Project Kit itself, including the legacy
`computing-environment` folder, the root-level files in this folder are the
canonical source of truth. Treat `.ai/computing-environment/` as an installed
snapshot for downstream-project testing, not as another nested project context.

Do not recurse into `.ai/computing-environment/.ai/` or read another
`computing-environment` layer unless the user explicitly asks to inspect the
packaged copy. For normal development of this repository, read root-level
governance files first, then the root `.ai/` project-state files.


ไฟล์นี้คือไฟล์แรกที่ AI / Codex / coding agent ควรอ่านก่อนเริ่มงาน

## Core Rule

ทุกงานต้องแยกให้ชัดว่าอยู่ใน loop ใดบ้างภายใน project หรือ hierarchy level
ที่กำลังทำงานอยู่:

- **L1 = AI ทำเองได้**  
  เช่น เขียนโค้ด ร่างเอกสาร วิเคราะห์ แก้บั๊ก สรุปข้อมูล สร้างสไลด์ จัดตาราง

- **L2 = ต้องใช้ judgment/context ของมนุษย์**  
  เช่น เป้าหมายจริง ผู้ใช้จริง tone, strategy, UX/UI, politics, stakeholder risk, academic judgment, institutional fit

- **L3 = ต้องใช้ feedback หรือข้อมูลจริงจากโลกภายนอก**  
  เช่น reviewer, นักเรียน, ผู้ใช้ระบบ, stakeholder, usage data, survey, interview, A/B test, experimental result

งานจริงมักเป็น 1+2, 2+3 หรือ 1+2+3  
ห้าม treat งานใหญ่เหมือนเป็น L1 อย่างเดียว

Loop diagnosis ต้องเป็น project-local: ถ้าอยู่ใน child/subproject ให้ประเมิน
L1/L2/L3 จาก objective, evidence, stakeholder, reviewer, user, data, และ
blocker ของ child นั้นก่อน Parent context ใช้เป็น framing และ constraints ได้
แต่ไม่ควรทำให้ loop ของ child กลายเป็น loop กว้างของ parent เว้นแต่งานนั้นถูก
ประกาศว่าเป็น parent-level หรือ cross-project task ชัดเจน

---

## Machine-Aware Rule

Projects may be opened on different machines, operating systems, shells, sync
folders, local disks, containers, or remote servers. Do not assume that data,
cache, model files, build artifacts, or runtime environments exist everywhere.

Use project-defined machine roles such as:

- `primary-heavy` = full builds, expensive tests, GPU/data-heavy runs
- `office-desktop` = regular development with possible local-resource differences
- `portable-laptop` = editing, review, smoke tests, meetings, and light runs
- `remote-server` = deployment, services, or batch runs
- unknown = inspect first

หาก project ใช้ไฟล์นอก project folder หรือ shared/synced source tree เช่น intermediate/cache/model/data ขนาดใหญ่ ต้องจดใน:

- `.ai/LOCAL_RESOURCES.md`
- `.ai/MACHINE_COMPATIBILITY.md`
- `.ai/RUNBOOK.md`

ห้าม hardcode path เฉพาะเครื่องลง source code ให้ใช้ environment variables เช่น:

```bash
PROJECT_DATA_ROOT=/path/to/data
PROJECT_CACHE_ROOT=/path/to/cache
PROJECT_OUTPUT_ROOT=/path/to/output
```

---

## Default Process

ให้ทำ 5 ขั้นนี้เสมอ เว้นแต่งานเล็กมาก:

1. **Loop Diagnosis**  
   ระบุว่าโจทย์นี้เกี่ยวข้องกับ L1 / L2 / L3 อย่างไรภายใน current project /
   current hierarchy level

2. **Working Spec**  
   สรุปเป้าหมาย ผู้ใช้/ผู้อ่าน ขอบเขต สิ่งที่ไม่ควรทำ assumption และข้อจำกัด

3. **Evals / Acceptance Criteria**  
   ระบุเกณฑ์วัดว่า output ผ่านหรือไม่ผ่าน

4. **Execution**  
   ลงมือทำ draft/code/analysis/prototype โดยทำเท่าที่ AI ทำได้ทันที

5. **Review Gate**  
   สรุปว่าอะไรเสร็จแล้ว อะไรยังต้องให้มนุษย์ตัดสินใจ อะไรต้องรอ feedback จริง และ next loop คืออะไร

---

## Project Resume Rule

ผู้ใช้สลับงานหลาย project แทบทุกวัน ดังนั้น agent ต้องช่วยจำสถานะงานผ่านไฟล์ project-local:

- `.ai/PROJECT_STATE.md` — ค้างตรงไหน เป้าหมายคืออะไร next action คืออะไร;
  สำหรับงานที่มี deadline/status ต้องมี last session summary และ next actions
  เรียงตาม priority/deadline
- `.ai/PROJECT_HIERARCHY.md` — directory นี้เป็น project/subproject/plain subdir หรือไม่ และสัมพันธ์กับ parent/child อย่างไร
- `.ai/MACHINE_PROFILE.md` — เครื่องนี้คืออะไร path/storage layout เป็นแบบไหน และเคยตรวจละเอียดเมื่อไร
- `.ai/COMPUTING_ENVIRONMENT_VERSION.md` — package/schema version ที่ติดตั้งใน project นี้ และสถานะ update check
- `.ai/SESSION_LOG.md` — log สั้นหลังแต่ละ session
- `.ai/TOKEN_BUDGET.md` — ควรอ่านอะไรเพื่อประหยัด token

เมื่อเริ่ม project เดิม ให้ resume จากไฟล์เหล่านี้ก่อน ไม่ใช่ scan ทุกอย่างใหม่ทันที
ทุก startup/resume ควรรายงานชื่อ package และ version ที่ติดตั้ง:
`Agent Project Kit` / `agent-project-kit` จาก `.ai/COMPUTING_ENVIRONMENT_VERSION.md`
พร้อม legacy path `.ai/computing-environment/` ถ้ายังใช้อยู่

ให้เช็กว่ามี package version ใหม่หรือไม่แบบเป็นช่วง ๆ ไม่ใช่ fetch/pull ทุกครั้ง:
ถ้าไม่เคยเช็ก, เช็กครั้งล่าสุดเกิน 14 วัน, กำลังทำ package-level/release work,
หรือผู้ใช้ถามเรื่อง version/update ให้รายงานว่า update check ควรทำหรือทำแล้ว
ถ้าจะอัปเดตจริง ให้ preserve project-local `.ai/` state และเทียบ schema ก่อน

ถ้า project มี deadline, submission, review round, meeting, class date, หรือ
status ค้างหลายรายการ ให้เปิดด้วย dashboard สั้น ๆ: ครั้งสุดท้ายเข้ามาทำอะไร,
อะไร done/blocked/waiting, อะไรต้องทำต่อก่อนหลัง, deadline หรือ trigger คืออะไร,
และหลักฐานของ status/deadline มาจากไฟล์หรือแหล่งไหน ถ้าไม่รู้ deadline ให้ระบุ
`unknown` แทนการเดา

## Token Cost Rule

ก่อนงานที่อาจกิน token สูง ให้ประเมินคร่าว ๆ ว่าเป็น `Low`, `Medium`, หรือ
`High` และดู `.ai/TOKEN_BUDGET.md` ว่า project นี้ใช้ cost profile ใด:

- `C0 Economy`: ถามก่อน deep scan, web research, test loop ยาว, หรือ rewrite กว้าง
- `C1 Normal`: ทำงานแบบ focused และเตือนก่อนขยาย scope ที่กิน token ชัดเจน
- `C2 Premium`: ทำ deep work ที่จำเป็นได้โดยไม่ถามซ้ำ แต่ยังต้องคุม scope

ถ้าผู้ใช้เลือกโมเดลประหยัดหรือพูดเรื่องค่าใช้จ่าย/token ให้ถือว่าอยู่ใกล้
`C0 Economy` และเสนอทางเลือกประหยัดก่อน เว้นแต่ผู้ใช้สั่งชัดว่าให้ทำต่อ

เมื่อ update `computing-environment` ใน project เดิม ให้เทียบ version/schema ใน
`.ai/COMPUTING_ENVIRONMENT_VERSION.md` กับ package ใหม่ก่อน ถ้า
`machine_profile_schema_version` ไม่เปลี่ยน ให้ reuse `.ai/MACHINE_PROFILE.md`
เดิม ไม่ต้องตรวจเครื่องละเอียดซ้ำ

## Project Hierarchy Rule

Subdirectory ไม่เท่ากับ subproject โดยอัตโนมัติ ต้องมี explicit marker เช่น
`.ai/PROJECT_HIERARCHY.md`, `.ai/PROJECT_STATE.md`, หรือ `AGENTS.md` ที่ประกาศว่า
directory นั้นเป็น project/subproject จริง

Parent project อ่าน child summary ได้เพื่อรู้ว่าลูกทำอะไรอยู่ แต่ไม่ควร load
full child context เว้นแต่งานนั้นแตะ child โดยตรง ส่วน child project ควรอ่าน
parent summary แค่ framing, constraint, shared resource, naming, หรือ policy
ไม่ควรดึง parent context ทั้งหมดเข้ามาโดยอัตโนมัติ

ให้คิด parent เหมือน public interface/contract ของ OOP: child อ่าน parent ได้แบบ
read-only เพื่อเข้าใจ constraint และ shared assumptions แต่ห้ามแก้ parent files,
parent `.ai/`, parent logs, หรือ parent resource manifests โดยอัตโนมัติ ถ้าพบว่า
parent stale ให้เสนอ parent update หรือจด note ใน child ก่อน ไม่ silent patch
parent

ยิ่ง project อยู่ลึกลงไป context ควรยิ่งเฉียบคมและ task-specific มากขึ้น เช่น
`nowcast/ting67/amt` เก็บสถานะ paper/reviewer/AMT journal ส่วน `nowcast/ting67`
เก็บ grant-level framing และ `nowcast` เก็บ research-program map

---

## Token Discipline

คุณภาพสำคัญกว่า token saving แบบสุดโต่ง แต่ต้องไม่ใช้ token เปลืองโดยไม่จำเป็น

ค่าเริ่มต้นคือ `T1 Standard`

- `T0 Quick` = งานเล็ก ตอบสั้น เจาะจุด
- `T1 Standard` = งานทั่วไป อ่านเท่าที่เกี่ยวข้อง
- `T2 Deep` = งานยาก reviewer/architecture/research/policy
- `T3 Agentic Run` = ให้ Codex แก้และ test เป็นรอบ

ถ้าเห็นว่าผู้ใช้กำลังส่ง context ยาวเกินจำเป็น หรือกำลังให้ AI scan ทั้ง project ทั้งที่ควรอ่านแค่บางไฟล์ ให้แนะนำวิธีประหยัด token แบบตรง ๆ

---

## Tone

ตอบตรง ไม่ต้องอวย

ห้ามพูดว่า:

- งานนี้ดีแล้ว ถ้ายังไม่มีเกณฑ์
- โค้ดผ่านแล้ว ถ้ายังไม่ได้รัน test
- ผู้ใช้จะชอบ ถ้ายังไม่มี user feedback
- reviewer จะพอใจ ถ้ายังไม่ได้ตอบ concern จริง
- เอกสารชัดแล้ว ถ้า logic ยังไม่ defend ได้
- project รันไม่ได้ เพียงเพราะ local cache บนเครื่องนี้ยังไม่มี

---

## Red Flag Detection

ถ้าเห็นสิ่งเหล่านี้ ให้เตือนทันที:

- งานเริ่มวนแก้โดยไม่มี eval
- prompt กว้างเกินไป เช่น “ช่วย improve”
- output ดูสวยแต่ไม่มี logic
- code รันได้แต่ไม่มี test
- conclusion แรงกว่า evidence
- spec คลุมเครือจน AI เดาเยอะเกินไป
- AI กำลังทำ L1 แล้ว claim ว่า L2/L3 จบแล้ว
- local path/cache/intermediate ใหญ่อยู่นอก project folder หรือ shared/synced source tree แต่ไม่ได้จดไว้
- กำลังใช้ token เยอะเพราะเล่า context ซ้ำ แทนที่จะอัปเดต `.ai/PROJECT_STATE.md`

---

## One Sentence Summary

แยกให้ชัดว่า AI ทำอะไรได้เอง อะไรต้องให้มนุษย์ตัดสินใจ อะไรต้องพิสูจน์กับโลกจริง และอะไรเป็น resource เฉพาะเครื่องที่อาจหายเมื่อย้ายเครื่อง


## Document Production Addendum

For document-producing work, also read:

- `DOCUMENT_PRODUCTION_POLICY.md`
- `checklists/DOCUMENT_CHECKLIST.md`
- `prompts/10_DOCUMENT_PRODUCTION.md`
- `templates/DOCUMENT_PIPELINE.md`
- `templates/DOCUMENT_STYLE.md`
- `templates/DOCUMENT_QA.md`

Default document workflow: Markdown first, content critique/revision second, final PDF/build last. Formal Thai documents use TH Sarabun New for Thai text; public documents use modern minimal readable fonts. Paper output defaults to A4; screen output defaults to 16:9. Final PDFs must pass table, Thai word-break, spelling, hanging title, and hanging line checks before being called final.

## Markdown classification rule for old projects

Older projects may contain serious Markdown source files mixed with AI scratch files. Before resuming such a project, do not read all Markdown files blindly and do not archive Markdown files just because they are loose.

Use this order:

1. Read `.ai/PROJECT_STATE.md` and `.ai/MARKDOWN_INVENTORY.md` if they exist.
2. If Markdown files are scattered, run or ask the agent to run:

```bash
python3 .ai/computing-environment/scripts/organize-project-markdown.py .
```

3. Review `.ai/MARKDOWN_INVENTORY.md`.
4. Treat files marked `document-source` as serious work, not trash. Register them in `.ai/DOCUMENT_PIPELINE.md` when needed.
5. Use `--apply` only for high-confidence AI scratch candidates. Ambiguous files must stay in place.

```bash
python3 .ai/computing-environment/scripts/organize-project-markdown.py . --apply
```

The script never deletes files. With `--apply`, it archives only high-confidence AI scratch candidates, not serious Markdown documents. To review files that may already have been archived too aggressively, run:

```bash
python3 .ai/computing-environment/scripts/organize-project-markdown.py . --include-archive
```

New AI working Markdown must be created under `.ai/`. Serious Markdown document sources may remain as project documents or be moved deliberately to `documents/<document-id>/content.md` and registered in `.ai/DOCUMENT_PIPELINE.md`.

## Built-in document template

For formal Thai A4 PDF documents, this package includes:

```text
templates/pandoc-thai-a4/
```

Use Markdown-first document production, register active document sources in `.ai/DOCUMENT_PIPELINE.md`, and do not call a PDF final until visual QA passes.
