Use the current `computing-environment v5` as the single source of truth. Ignore older duplicated prompt files unless they are referenced from `legacy/` for historical context.

# GLOBAL_START_PROMPT

แปะ prompt นี้เมื่อต้องการให้ AI เริ่มงานโดยอิงกติกาในโฟลเดอร์นี้

## General Version

```text
อ่านและใช้กติกาจากโฟลเดอร์ OneDrive/computing-environment ก่อนทำงานนี้
โดยเฉพาะ START_HERE.md, AGENTS.md, SPEC_EVAL_LOOP_INSTRUCTION.md, MACHINE_PROFILES.md, WSL2_ONEDRIVE_WORKFLOW.md และ TOKEN_DISCIPLINE.md

งานนี้ให้ใช้ Spec–Eval–Loop Workflow:
แยก L1 = AI ทำเองได้, L2 = ต้องใช้ judgment/context ของผม, L3 = ต้องใช้ feedback หรือข้อมูลจริง

ถ้าเป็น project/repo ให้ตรวจ project state ด้วย:
- .ai/PROJECT_STATE.md
- .ai/LOCAL_RESOURCES.md
- .ai/MACHINE_COMPATIBILITY.md
- .ai/RUNBOOK.md
- .ai/SESSION_LOG.md
- .ai/TOKEN_BUDGET.md

จากนั้นให้ทำ:
1. Loop Diagnosis
2. Working Spec
3. Evals / Acceptance Criteria
4. Execution หรือ Draft แรก
5. Review Gate พร้อม local resource / machine issue และ token note ถ้าเกี่ยวข้อง

อย่าอวย
อย่าบอกว่าเสร็จถ้ายังไม่มี test หรือ evidence
ถ้าต้องเดา ให้บอก assumption แล้วเดินหน้าก่อน
ถ้าเห็นว่าผมกำลังวนแก้แบบไม่มีเกณฑ์ ให้หยุดแล้วเสนอ eval
ถ้าเห็นว่าผมใช้ token เปลืองโดยไม่เพิ่มคุณภาพ ให้แนะนำวิธีที่ประหยัดกว่า
```

## WSL2 / Codex Version

```text
Before working, read:
- OneDrive/computing-environment/START_HERE.md
- OneDrive/computing-environment/SPEC_EVAL_LOOP_INSTRUCTION.md
- OneDrive/computing-environment/AGENTS.md
- OneDrive/computing-environment/MACHINE_PROFILES.md
- OneDrive/computing-environment/WSL2_ONEDRIVE_WORKFLOW.md
- OneDrive/computing-environment/TOKEN_DISCIPLINE.md

Then inspect this project using the machine-aware Spec–Eval–Loop Workflow.

First detect:
- current machine: think / madlab-i9 / black5 / unknown
- whether running in WSL2
- whether project is under OneDrive
- whether .ai/PROJECT_STATE.md and .ai/LOCAL_RESOURCES.md exist
- whether local resources required for this task exist on this machine

Do not run heavy commands before checking machine suitability.
Do not hardcode non-portable paths.
Do not pretend missing local cache means the project is broken.
After meaningful work, update or propose updates to .ai/PROJECT_STATE.md and .ai/SESSION_LOG.md.
```

## For project already installed with `.ai/computing-environment`

```text
Before working, read:
- AGENTS.md
- .ai/computing-environment/START_HERE.md
- .ai/computing-environment/SPEC_EVAL_LOOP_INSTRUCTION.md
- .ai/computing-environment/MACHINE_PROFILES.md
- .ai/computing-environment/WSL2_ONEDRIVE_WORKFLOW.md
- .ai/computing-environment/TOKEN_DISCIPLINE.md
- .ai/PROJECT_STATE.md
- .ai/LOCAL_RESOURCES.md
- .ai/MACHINE_COMPATIBILITY.md
- .ai/RUNBOOK.md
- .ai/TOKEN_BUDGET.md

Then perform Loop Diagnosis, Working Spec, Evals, Execution, and Review Gate.
```


## Document Production Addendum

For document-producing work, also read:

- `DOCUMENT_PRODUCTION_POLICY.md`
- `checklists/DOCUMENT_CHECKLIST.md`
- `prompts/10_DOCUMENT_PRODUCTION.md`
- `templates/DOCUMENT_PIPELINE.md`
- `templates/DOCUMENT_STYLE.md`
- `templates/DOCUMENT_QA.md`

Default document workflow: Markdown first, content critique/revision second, final PDF/build last. Formal Thai documents use TH Sarabun New for Thai text; public documents use modern minimal readable fonts. Paper output defaults to A4; screen output defaults to 16:9. Final PDFs must pass table, Thai word-break, spelling, hanging title, and hanging line checks before being called final.
