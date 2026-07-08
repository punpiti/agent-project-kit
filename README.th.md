# Agent Project Kit

[English](README.md)

Agent Project Kit ช่วยให้ใช้ AI coding agents กับโปรเจคจริงได้เป็นระบบขึ้น

ถ้าไม่ติดตั้งอะไรเลย แต่ละครั้งที่เปิด AI มักต้องเริ่มใหม่: AI ต้อง scan
โปรเจคซ้ำ ลืม decision เดิม เดา path เฉพาะเครื่อง ใช้ token ซ้ำกับบริบทเดิม
และอาจสับสนว่า folder ไหนคือ project, subproject, หรือแค่ subdirectory ธรรมดา

ถ้าติดตั้งชุดนี้ โปรเจคจะมี `.ai/` working layer และ root instruction files
เพื่อให้ AI resume จาก state เดิม ตรวจเครื่องปัจจุบัน รู้ว่า resource อยู่ไหน
คุม token/cost และใช้ workflow เดียวกันได้กับ Codex, Claude Code, Antigravity
หรือ agent อื่นที่อ่านไฟล์คำสั่งใน repo

## ได้อะไรจากการติดตั้ง

- AI ไม่ต้องเริ่มจากศูนย์ทุกครั้ง
- ลดการ scan repo ซ้ำโดยไม่จำเป็น
- จดว่าโปรเจคค้างตรงไหนใน `.ai/PROJECT_STATE.md`
- จดว่าเครื่องนี้คืออะไรและรันอะไรเหมาะใน `.ai/MACHINE_PROFILE.md`
- จด path ของ data/cache/resource ที่อยู่นอกโปรเจคใน `.ai/LOCAL_RESOURCES.md`
- แยก project / subproject / plain folder ให้ชัด
- ตั้ง token/cost mode ได้ เช่น economy mode ให้ถามก่อนใช้ token หนัก
- ใช้ policy เดียวกันได้กับ Codex, Claude Code, Antigravity และ agent อื่น

## เหมาะกับใคร

เหมาะกับโปรเจคที่:

- จะใช้ AI มากกว่าหนึ่งครั้ง
- มีหลายเครื่อง หรือย้ายงานระหว่างเครื่อง
- มี data/cache/intermediate files ที่ไม่ควรอยู่ใน repo หรือ shared drive
- มี subproject หลายระดับ
- ใช้ AI หลายตัว เช่น Codex, Claude Code, Antigravity
- อยากลด token ระยะยาวโดยให้ AI อ่าน state สั้น ๆ แทนการ scan ใหม่

ถ้าเป็นงานเล็กครั้งเดียว ไม่ต้องติดตั้งก็ได้

## เริ่มใช้กับโปรเจคใหม่

macOS / Linux / WSL2:

```bash
mkdir my-project
cd my-project
mkdir -p .ai
git clone https://github.com/punpiti/agent-project-kit.git .ai/agent-project-kit
bash .ai/agent-project-kit/scripts/install-to-project.sh . .ai/agent-project-kit
code .
```

Windows PowerShell:

```powershell
New-Item -ItemType Directory -Force -Path "my-project" | Out-Null
Set-Location "my-project"
New-Item -ItemType Directory -Force -Path ".ai" | Out-Null
git clone https://github.com/punpiti/agent-project-kit.git ".ai\agent-project-kit"
powershell -ExecutionPolicy Bypass -File ".ai\agent-project-kit\scripts\install-to-project.ps1" -ProjectPath . -SourcePath ".ai\agent-project-kit"
code .
```

## ใช้กับโปรเจคที่มีอยู่แล้ว

เข้าไปที่ root ของโปรเจคก่อน แล้วรัน:

```bash
mkdir -p .ai
git clone https://github.com/punpiti/agent-project-kit.git .ai/agent-project-kit
bash .ai/agent-project-kit/scripts/install-to-project.sh . .ai/agent-project-kit
```

## หลังติดตั้งแล้วจะได้อะไร

```text
AGENTS.md
CLAUDE.md
ANTIGRAVITY.md
.ai/computing-environment/
.ai/PROJECT_STATE.md
.ai/PROJECT_HIERARCHY.md
.ai/COMPUTING_ENVIRONMENT_VERSION.md
.ai/MACHINE_PROFILE.md
.ai/LOCAL_RESOURCES.md
.ai/MACHINE_COMPATIBILITY.md
.ai/RUNBOOK.md
.ai/TOKEN_BUDGET.md
.ai/SESSION_LOG.md
```

ไฟล์ root เช่น `AGENTS.md`, `CLAUDE.md`, `ANTIGRAVITY.md` จะบอก AI แต่ละตัวให้กลับไปอ่าน policy และ state ใน `.ai/`

## Prompt แรกที่ควรบอก AI

```text
อ่าน AGENTS.md และ .ai/computing-environment ก่อน
จากนั้นอ่าน .ai/PROJECT_STATE.md, .ai/PROJECT_HIERARCHY.md,
.ai/COMPUTING_ENVIRONMENT_VERSION.md, .ai/MACHINE_PROFILE.md,
.ai/LOCAL_RESOURCES.md, .ai/MACHINE_COMPATIBILITY.md, .ai/RUNBOOK.md,
และ .ai/TOKEN_BUDGET.md
สรุปว่า project ค้างตรงไหน เครื่องนี้คือเครื่องอะไร มี local resource อะไรขาด
และควรใช้ token/cost mode แบบไหน ก่อนเริ่มทำงาน
```

## Token จะเปลืองขึ้นไหม

รอบแรกอาจใช้ token มากขึ้น เพราะต้อง onboard โปรเจค ตรวจเครื่อง และสร้าง state
แต่ระยะยาวควรประหยัดลง เพราะ AI ไม่ต้อง scan หรือถามบริบทเดิมซ้ำทุกครั้ง

หลักคือจ่ายครั้งแรกเพื่อสร้าง project memory ที่ดี แล้วใช้ `.ai/PROJECT_STATE.md`
เป็น compression layer ในรอบต่อไป

## Shared Storage Policy

นี่ไม่ใช่กติกาเฉพาะ OneDrive แต่เป็นแนวทาง programming ทั่วไป:

- source code, docs, specs, small fixtures, prompts, และ AI state อยู่ใน project folder หรือ shared/synced folder ได้
- cache, intermediate files, virtualenv, `node_modules`, model checkpoints, build folders, temporary exports ควรอยู่ machine-local
- ถ้าต้องใช้ resource นอก project/shared folder ให้จดไว้ใน `.ai/LOCAL_RESOURCES.md`

วิธีนี้ช่วยให้ repo/shared drive เล็กลง sync เร็วขึ้น และย้ายเครื่องแล้วไม่เดา path ผิด

## อัปเดต

macOS / Linux / WSL2:

```bash
git -C .ai/agent-project-kit pull --ff-only
bash .ai/agent-project-kit/scripts/install-to-project.sh . .ai/agent-project-kit
```

Windows PowerShell:

```powershell
git -C ".ai\agent-project-kit" pull --ff-only
powershell -ExecutionPolicy Bypass -File ".ai\agent-project-kit\scripts\install-to-project.ps1" -ProjectPath . -SourcePath ".ai\agent-project-kit"
```
