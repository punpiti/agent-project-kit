# Agent Project Kit

[English](README.md)

Agent Project Kit เป็นชุดไฟล์เริ่มต้นสำหรับใช้ AI coding agents กับ project
folder ให้เป็นระเบียบขึ้น

เมื่อติดตั้งแล้ว โปรเจคจะมีไฟล์คำสั่งและ template ใต้ `.ai/` เพื่อให้ Codex,
Claude Code, Antigravity หรือ agent อื่นรู้ว่าควรเริ่มอ่านจากตรงไหน

เหมาะกับโปรเจคที่คุณจะเปิดใช้กับ AI มากกว่าหนึ่งครั้ง หรืออยากให้คนในบ้านลอง
clone แล้วเริ่มใช้ได้โดยไม่ต้องตั้งโครงสร้างเองทุกครั้ง

ประโยชน์หลักคือช่วยให้ AI กลับมาเริ่มงานในโปรเจคเดิมได้โดยไม่ต้องเริ่มใหม่:
รู้ว่าครั้งก่อนทำถึงไหน เครื่องนี้เหมาะกับงานแค่ไหน มี resource เฉพาะเครื่อง
อะไร ต้องใช้ parent/child context แค่ไหน และงานต่อไปควรทำอะไรก่อนตาม
priority/deadline

## ได้อะไรจากการติดตั้ง

- มีไฟล์ `AGENTS.md`, `CLAUDE.md`, `ANTIGRAVITY.md` ให้ AI แต่ละตัวรู้จุดเริ่ม
- มี `.ai/` สำหรับจด state และ note ของโปรเจค
- มีที่จดว่าเครื่องนี้เหมาะกับงานแบบไหน
- มีคำสั่ง install/update สำหรับ macOS, Linux, WSL2 และ Windows PowerShell

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
.ai/MACHINE_PROFILE.md
.ai/LOCAL_RESOURCES.md
.ai/RUNBOOK.md
.ai/TOKEN_BUDGET.md
.ai/SESSION_LOG.md
```

ไฟล์ root เช่น `AGENTS.md`, `CLAUDE.md`, `ANTIGRAVITY.md` จะบอก AI แต่ละตัวให้ไปอ่านกติกาและ note ใน `.ai/`

## Changelog

ดูการเปลี่ยนแปลงของ package ได้ที่ [CHANGELOG.md](CHANGELOG.md)

## Prompt แรกที่ควรบอก AI

```text
อ่าน AGENTS.md และ .ai/computing-environment ก่อน
จากนั้นอ่าน note ที่เกี่ยวข้องใน .ai/
สรุปว่าโปรเจคนี้คืออะไร เครื่องนี้คือเครื่องอะไร และต้องรู้อะไรก่อนเริ่มงาน
รายงาน Agent Project Kit version ที่ติดตั้งจาก .ai/COMPUTING_ENVIRONMENT_VERSION.md
ถ้าโปรเจคนี้อยู่ใต้ parent/upper folder ที่เคย scan แล้ว ให้ reuse parent
summary และ machine profile ได้ ไม่ต้อง scan parent ซ้ำกว้าง ๆ แต่ให้ถือ parent
เป็น broad context เท่านั้น ส่วนโปรเจคลูกต้องสรุป state ของตัวเองให้ลึกและคมกว่า
ถ้าโปรเจคมี status หรือ deadline ให้เริ่มจากครั้งสุดท้ายทำอะไร และควรทำอะไรต่อ
โดยเรียงตาม priority และ deadline
ถ้ายังไม่ได้เช็ก update ของ kit มาสักพัก ให้บอกก่อนทำงานระดับ package
```

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
