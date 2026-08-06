# Agent Project Kit

[English](README.md)

Agent Project Kit เป็นชุดไฟล์เริ่มต้นสำหรับใช้ AI coding agents กับ project
folder ให้เป็นระเบียบขึ้น

เมื่อติดตั้งแล้ว โปรเจคจะมีไฟล์คำสั่งและ template ใต้ `.ai/` เพื่อให้ Codex,
Claude Code, Antigravity หรือ agent อื่นรู้ว่าควรเริ่มอ่านจากตรงไหน
ตัว kit ตั้งใจให้เล็กและแยกชั้น: code ของโปรเจคยังเป็นของโปรเจค, note เฉพาะ
โปรเจคอยู่ใต้ `.ai/`, ส่วน snapshot ของ kit refresh ทีหลังได้

release ปัจจุบัน: `7.2.2-shared-runtime-v2-canary`

เหมาะกับโปรเจคที่คุณจะเปิดใช้กับ AI มากกว่าหนึ่งครั้ง หรืออยากให้คนในบ้านลอง
clone แล้วเริ่มใช้ได้โดยไม่ต้องตั้งโครงสร้างเองทุกครั้ง

ประโยชน์หลักคือช่วยให้ AI กลับมาเริ่มงานในโปรเจคเดิมได้โดยไม่ต้องเริ่มใหม่:
รู้ว่าครั้งก่อนทำถึงไหน เครื่องนี้เหมาะกับงานแค่ไหน มี resource เฉพาะเครื่อง
อะไร ถ้างานควรรัน parallel ควรใช้ CPU/GPU/RAM/storage ของเครื่องนี้แค่ไหน
ต้องใช้ parent/child context แค่ไหน และงานต่อไปควรทำอะไรก่อนตาม
priority/deadline

ถ้าเป็นโปรเจควิจัย จะมี prompt สำหรับ literature review, source check,
counter-argument, data interpretation และ research brief เพิ่มให้ใช้เป็นฐาน

## ได้อะไรจากการติดตั้ง

- มีไฟล์ `AGENTS.md`, `CLAUDE.md`, `ANTIGRAVITY.md` ให้ AI แต่ละตัวรู้จุดเริ่ม
- มี `.ai/` สำหรับจด state และ note ของโปรเจค
- มีที่จดว่าเครื่องนี้เหมาะกับงานแบบไหน และควรรัน parallel ได้ระดับไหน
- มีที่ประกาศ prompt pack, local resource และข้อจำกัดเฉพาะโปรเจค
- มีคำสั่ง install/update สำหรับ macOS, Linux, WSL2 และ Windows PowerShell

ถ้าเป็นงานเล็กครั้งเดียว ไม่ต้องติดตั้งก็ได้

## path ที่ใช้ตอนนี้

```text
.ai/agent-project-kit/        # managed snapshot ของ kit, update แล้ว refresh ได้
.ai/agent-project-kit-source/ # git clone/source copy สำหรับติดตั้ง
.ai/PROJECT_STATE.md          # state เฉพาะโปรเจค, ต้อง preserve ตอน update
```

อย่าเก็บ note หรือ prompt pack เฉพาะโปรเจคไว้ใน `.ai/agent-project-kit/`
เพราะ folder นี้เป็นของ kit และ updater มีสิทธิ์ refresh ได้ ให้เก็บ prompt
ของโปรเจคไว้เช่น `.ai/prompts/`, `.ai/prompt-packs/`, `.ai/custom-prompts/`
หรือ path อื่นที่ระบุใน `.ai/PROJECT_STATE.md` หรือ `.ai/RUNBOOK.md`

## เริ่มใช้กับโปรเจคใหม่

macOS / Linux:

```bash
mkdir my-project
cd my-project
mkdir -p .ai
git clone https://github.com/punpiti/agent-project-kit.git .ai/agent-project-kit-source
bash .ai/agent-project-kit-source/scripts/install-to-project.sh . .ai/agent-project-kit-source
code .
```

WSL2 ที่โปรเจคอยู่ในโฟลเดอร์ฝั่ง Windows เช่น OneDrive:

```bash
mkdir my-project
cd my-project
KIT="${XDG_CACHE_HOME:-$HOME/.cache}/agent-project-kit"
if [ -d "$KIT/.git" ]; then
  git -C "$KIT" pull --ff-only
else
  git clone https://github.com/punpiti/agent-project-kit.git "$KIT"
fi
bash "$KIT/scripts/install-to-project.sh" . "$KIT"
code .
```

Windows PowerShell:

```powershell
New-Item -ItemType Directory -Force -Path "my-project" | Out-Null
Set-Location "my-project"
New-Item -ItemType Directory -Force -Path ".ai" | Out-Null
git clone https://github.com/punpiti/agent-project-kit.git ".ai\agent-project-kit-source"
powershell -ExecutionPolicy Bypass -File ".ai\agent-project-kit-source\scripts\install-to-project.ps1" -ProjectPath . -SourcePath ".ai\agent-project-kit-source"
code .
```

## ใช้กับโปรเจคที่มีอยู่แล้ว

เข้าไปที่ root ของโปรเจคก่อน แล้วรัน:

```bash
KIT="${XDG_CACHE_HOME:-$HOME/.cache}/agent-project-kit"
if [ -d "$KIT/.git" ]; then
  git -C "$KIT" pull --ff-only
else
  git clone https://github.com/punpiti/agent-project-kit.git "$KIT"
fi
bash "$KIT/scripts/install-to-project.sh" . "$KIT"
```

## ใช้ shared runtime กับหลายโปรเจคบน WSL2 (Canary)

ถ้าโปรเจคส่วนใหญ่รันด้วย Ubuntu/WSL2 สามารถติดตั้งส่วน generic และ versioned
ของ kit ไว้ใต้ OneDrive root เพียงชุดเดียวได้ ส่วน content และ state เฉพาะ
โปรเจคยังอยู่ใน workspace ของแต่ละโปรเจค ขณะที่ launcher/config เฉพาะเครื่อง
อยู่ใต้ WSL home

กำหนด path ของเครื่องและโปรเจคก่อน:

```bash
PROJECT="/home/<user>/OneDrive/path/to/project"
KIT="${XDG_CACHE_HOME:-$HOME/.cache}/agent-project-kit"
APK_SHARED_ROOT="/home/<user>/OneDrive/.agent-project-kit"
APK_MACHINE_HOME="$HOME/.local/share/agent-project-kit"
```

ติดตั้งหรืออัปเดต immutable shared version ก่อน:

```bash
python3 "$KIT/scripts/install-shared.py" \
  --source "$KIT" \
  --shared-root "$APK_SHARED_ROOT" \
  --machine-home "$APK_MACHINE_HOME" \
  --configure-shell
```

`--configure-shell` จะเขียน managed block หนึ่งชุดแบบ idempotent ลง `~/.bashrc`
เพื่อกำหนด `APK_SHARED_ROOT`, `APK_MACHINE_HOME` และเพิ่ม launcher ใน `PATH`
จากนั้นเปิด shell ใหม่หรือรัน `source ~/.bashrc` ถ้า Bash ของเครื่องอ่าน rc file
อื่น ให้ระบุ `--shell-rc /path/to/rc` รอบอัปเดตครั้งต่อไปไม่ต้องใส่
`--configure-shell` เว้นแต่ตำแหน่ง path เปลี่ยน

สำหรับโปรเจคใหม่ ให้ติดตั้ง snapshot สำหรับ fallback แล้วสร้าง binding:

```bash
bash "$KIT/scripts/install-to-project.sh" "$PROJECT" "$KIT"
python3 "$KIT/scripts/install-shared.py" \
  --source "$KIT" \
  --shared-root "$APK_SHARED_ROOT" \
  --machine-home "$APK_MACHINE_HOME" \
  --bind-project "$PROJECT"
```

ถ้าโปรเจคมี binding เดิม ให้สำรองแบบระบุ version ก่อนอัปเกรด:

```bash
cp -p "$PROJECT/.ai/apk.json" \
  "$PROJECT/.ai/apk.json.before-7.2.1"
bash "$KIT/scripts/install-to-project.sh" "$PROJECT" "$KIT"
python3 "$KIT/scripts/install-shared.py" \
  --source "$KIT" \
  --shared-root "$APK_SHARED_ROOT" \
  --machine-home "$APK_MACHINE_HOME" \
  --bind-project "$PROJECT"
```

ตรวจ resolve และคำขอตัวอย่างที่ตรงกับงานของโปรเจค:

```bash
APK_MACHINE_HOME="$APK_MACHINE_HOME" \
  "$APK_MACHINE_HOME/bin/apk" --project "$PROJECT" resolve
APK_MACHINE_HOME="$APK_MACHINE_HOME" \
  "$APK_MACHINE_HOME/bin/apk" --project "$PROJECT" context \
  "<คำขอที่ชัดเจนและตรงกับโปรเจคนี้>"
```

ถ้าต้อง rollback คำสั่งนี้จะปิดเฉพาะ shared binding โดย snapshot ใต้
`.ai/agent-project-kit/` ยังอยู่:

```bash
APK_MACHINE_HOME="$APK_MACHINE_HOME" \
  python3 "$KIT/scripts/apk.py" --project "$PROJECT" rollback
```

ถ้าตรวจแล้วต้องการเปิด binding เดิมกลับ:

```bash
mv "$PROJECT/.ai/apk.json.disabled" "$PROJECT/.ai/apk.json"
```

อย่า migrate ทุกโปรเจคพร้อมกัน ให้เริ่มจาก canary batch เล็กและทดสอบ rollback
ก่อน ช่วง canary ให้เก็บ shared version เก่าและ snapshot ของโปรเจคไว้

ถ้า path หรือชื่อไฟล์ใน OneDrive ฝั่ง Windows ยาวเกินจน WSL2 รายงาน I/O error
ให้หยุด retry จาก Linux ก่อน ตรวจว่าไม่มี process เปิดไฟล์อยู่ แล้วใช้ Windows
PowerShell กับ Windows path ที่แน่นอนและ `-LiteralPath` เพื่อ rename หรือ move
ไป path ที่สั้นกว่า จากนั้นกลับมาเปิด WSL2 และตรวจผลอีกครั้ง

## หลังติดตั้งแล้วจะได้อะไร

```text
AGENTS.md
CLAUDE.md
ANTIGRAVITY.md
.ai/agent-project-kit/
.ai/PROJECT_STATE.md
.ai/MACHINE_PROFILE.md
.ai/LOCAL_RESOURCES.md
.ai/RUNBOOK.md
.ai/TOKEN_BUDGET.md
.ai/SESSION_LOG.md
```

ไฟล์ root เช่น `AGENTS.md`, `CLAUDE.md`, `ANTIGRAVITY.md` จะบอก AI แต่ละตัวให้ไปอ่านกติกาและ note ใน `.ai/` ถ้ามีไฟล์เหล่านี้อยู่แล้ว installer จะเติม managed block เฉพาะที่จำเป็น ไม่แทนที่ไฟล์เดิม และถ้าเจอ `.ai/agent-project-kit/` หรือ metadata ชื่อเดียวกันที่ไม่ใช่ของ Agent Project Kit จะหยุดแทนการเขียนทับ

source clone กับ installed snapshot ใช้คนละ path กัน เพื่อไม่ให้ `git clone`
ไปชนกับ directory ที่ installer ต้อง refresh

## Prompt pack

prompt ที่มากับ kit อยู่ที่:

```text
.ai/agent-project-kit/prompts/
```

prompt pack เฉพาะโปรเจคควรอยู่ข้างนอก managed snapshot เช่น:

```text
.ai/prompts/
.ai/prompt-packs/
.ai/custom-prompts/
```

ให้จด path ของ prompt pack เฉพาะโปรเจคไว้ใน `.ai/PROJECT_STATE.md` หรือ
`.ai/RUNBOOK.md` เพื่อให้ session ถัดไปรู้ว่าต้องอ่านตรงไหน

ถ้าเป็นงานวิจัย ให้ดู prompt ชุดนี้:

```text
.ai/agent-project-kit/prompts/13_RESEARCH_PROJECT_PROMPTS.md
```

## Changelog

ดูการเปลี่ยนแปลงของ package ได้ที่ [CHANGELOG.md](CHANGELOG.md)

## Prompt แรกที่ควรบอก AI

```text
อ่าน AGENTS.md และ .ai/agent-project-kit ก่อน
จากนั้นอ่าน note ที่เกี่ยวข้องใน .ai/
สรุปว่าโปรเจคนี้คืออะไร เครื่องนี้คือเครื่องอะไร และต้องรู้อะไรก่อนเริ่มงาน
รายงาน Agent Project Kit version ที่ติดตั้งจาก .ai/COMPUTING_ENVIRONMENT_VERSION.md
ถ้าโปรเจคนี้อยู่ใต้ parent/upper folder ที่เคย scan แล้ว ให้ reuse parent
summary และ machine profile ได้ ไม่ต้อง scan parent ซ้ำกว้าง ๆ แต่ให้ถือ parent
เป็น broad context เท่านั้น ส่วนโปรเจคลูกต้องสรุป state ของตัวเองให้ลึกและคมกว่า
ถ้าโปรเจคมี status หรือ deadline ให้เริ่มจากครั้งสุดท้ายทำอะไร และควรทำอะไรต่อ
โดยเรียงตาม priority และ deadline
ถ้างานไหนควรรัน parallel ให้ตัดสินใจก่อนว่าเครื่องนี้มี CPU กี่ core, มี GPU
หรือ accelerator แบบไหน, RAM/storage พอหรือไม่ และมี resource limit ของโปรเจค
หรือไม่ จากนั้นเลือกระดับ parallelism แบบ conservative แล้วรายงานก่อนรันงานหนัก
ถ้ายังไม่ได้เช็ก update ของ kit มาสักพัก ให้บอกก่อนทำงานระดับ package
```

## อัปเดตโปรเจคที่เคยติดตั้งแล้ว

ดู checklist เต็มได้ที่ [UPDATE_EXISTING_PROJECT.md](UPDATE_EXISTING_PROJECT.md)

หลักคืออ่าน version เดิม, เช็ก `manifest.json` บน GitHub Pages แบบ dry-run
ก่อน, แล้วค่อย apply update โดยไม่ลบ project-local state ใต้ `.ai/` ส่วน
แนวคิด/ไฟล์ package ใหม่จะถูก refresh ใต้ `.ai/agent-project-kit/`

การเริ่มงานตามปกติจะตรวจเฉพาะ manifest ทุก 14 วันและแจ้งเมื่อมีเวอร์ชันใหม่
โดยไม่ clone, pull หรือติดตั้งให้อัตโนมัติ การเปิดซ้ำภายในช่วง 14 วันจะไม่ยิง
network ซ้ำ

dry-run:

```bash
bash .ai/agent-project-kit/scripts/update-from-pages.sh --dry-run .
```

macOS / Linux:

```bash
bash .ai/agent-project-kit/scripts/update-from-pages.sh .
```

WSL2 ที่โปรเจคอยู่ในโฟลเดอร์ฝั่ง Windows เช่น OneDrive:

```bash
KIT="${XDG_CACHE_HOME:-$HOME/.cache}/agent-project-kit"
bash "$KIT/scripts/update-from-pages.sh" --dry-run .
bash "$KIT/scripts/update-from-pages.sh" .
```

Windows PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File ".ai\agent-project-kit\scripts\update-from-pages.ps1" -ProjectPath . -DryRun
powershell -ExecutionPolicy Bypass -File ".ai\agent-project-kit\scripts\update-from-pages.ps1" -ProjectPath .
```
