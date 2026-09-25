# Agent Project Kit

[English](README.md)

Agent Project Kit (APK) ติดตั้งไฟล์คำสั่งชุดเล็กและบันทึกโปรเจกต์ใต้ `.ai/`
เพื่อให้ AI coding agent อย่าง Claude Code, Codex และ Antigravity ทำงานต่อจาก
session ก่อนได้ เลือกวิธีทำงานให้ตรงกับงาน และตรวจผลงานก่อนส่ง
code และเอกสารยังเป็นของคุณ ตัว kit อยู่ใน `.ai/agent-project-kit/` และอัปเดตได้
โดยบันทึกของคุณไม่ถูกแตะ

release ปัจจุบัน: `8.0.1-python-core-canary`

## ช่วยอะไรคุณได้

- ทำงานต่อด้วยประโยคเดียว บอก agent ว่า "อ่าน md แล้วทำต่อ" แล้ว agent เริ่มจาก
  `.ai/PROJECT_STATE.md` ว่าทำอะไรไปแล้ว ตัดสินอะไรไปแล้ว และขั้นต่อไปคืออะไร
- เลือกวิธีทำงานตามประเภทงาน การเขียนบทของตำรา ตรวจวิทยานิพนธ์ ตอบผู้ทรงคุณวุฒิ
  ร่างนโยบาย เขียนหนังสือราชการ ทำสไลด์สอน และวิเคราะห์ข้อมูล แต่ละงานมีขั้นตอน
  ของตัวเองพร้อมจุดตรวจคุณภาพที่เกี่ยวข้อง
- ตรวจผลงาน ตัวเลขอ่านจากไฟล์ผล เอกสารและสไลด์ถูกเปิดตรวจหลัง build
  ร้อยแก้วที่ผู้อ่านเห็นผ่านตัวตรวจภาษา และไฟล์ Word ภาษาไทยผ่านขั้นซ่อมฟอนต์กับ
  การตัดคำ
- ไฟล์ของคุณปลอดภัย การติดตั้งและอัปเดตไม่เปลี่ยนบันทึกโปรเจกต์และคำสั่งที่คุณ
  เขียนเอง ถ้าอัปเดตล้มเหลว ระบบคืนชุดเดิมให้
- ใช้ได้หลายเครื่อง Linux, macOS, WSL2 และ Windows ใช้ตัวติดตั้งเดียวกัน

รุ่นนี้เป็น canary ทดสอบแล้วบน Linux, WSL2 และ Windows ยังไม่ได้ทดสอบบนเครื่อง
macOS จริง

## สิ่งที่ต้องมี

- Git
- Python 3.9 ขึ้นไป
  - macOS / Linux / WSL2 ส่วนใหญ่มี `python3` อยู่แล้ว
  - Windows ให้ติดตั้ง Python install manager จาก <https://www.python.org/downloads/>
    ซึ่งมีคำสั่ง `py` มาให้ ส่วน `python` ของ Microsoft Store เป็นแค่ทางลัดไปหน้า
    Store ตัวติดตั้งจึงข้ามตัวนี้
- Bash (macOS / Linux / WSL2) หรือ PowerShell 5.1 / 7 (Windows)

หลังติดตั้ง Git หรือ Python ให้เปิด terminal ใหม่ WSL2 จำ `PATH` ของ Windows
ตั้งแต่ตอนเริ่ม ถ้าจะเรียกโปรแกรม Windows ที่เพิ่งติดตั้งจาก WSL2 ให้รีสตาร์ต
WSL2 ก่อน (`wsl --shutdown`)

## เริ่มใช้งาน

สร้างหรือเข้าไปที่ folder ของโปรเจกต์ก่อน

```bash
mkdir my-project
cd my-project
```

### macOS / Linux

```bash
mkdir -p .ai
git clone https://github.com/punpiti/agent-project-kit.git .ai/agent-project-kit-source
bash .ai/agent-project-kit-source/scripts/install-to-project.sh . .ai/agent-project-kit-source
```

### WSL2 กับ folder ที่ sync กับ Windows (OneDrive)

เก็บ git clone ไว้ใน cache ฝั่ง WSL แล้วติดตั้งเฉพาะ snapshot ลงโปรเจกต์ เพราะ
ข้อมูล git ใน folder ที่ sync อยู่ทำงานช้าและเสียหายได้

```bash
KIT="${XDG_CACHE_HOME:-$HOME/.cache}/agent-project-kit"
if [ -d "$KIT/.git" ]; then
  git -C "$KIT" pull --ff-only
else
  git clone https://github.com/punpiti/agent-project-kit.git "$KIT"
fi
bash "$KIT/scripts/install-to-project.sh" . "$KIT"
```

### Windows PowerShell

```powershell
New-Item -ItemType Directory -Force -Path ".ai" | Out-Null
git clone https://github.com/punpiti/agent-project-kit.git ".ai\agent-project-kit-source"
powershell -ExecutionPolicy Bypass -File ".ai\agent-project-kit-source\scripts\install-to-project.ps1" -ProjectPath . -SourcePath ".ai\agent-project-kit-source"
```

PowerShell 7 ใช้ได้เหมือนกัน โดยเปลี่ยน `powershell` เป็น `pwsh`

## เริ่มงานกับ agent

เปิด folder ใน coding agent แล้วพิมพ์

```text
อ่าน AGENTS.md และ .ai/PROJECT_STATE.md แล้วทำขั้นต่อไป
```

โปรเจกต์ใหม่ agent จะกรอก `.ai/PROJECT_STATE.md` ให้ก่อน session ต่อ ๆ ไปใช้
ประโยคนี้ประโยคเดียว หรือสั่งงานตรง ๆ เช่น "เขียนบทที่ 3 จากโครงบท" หรือ
"ตอบ reviewer ทีละประเด็น"

## ติดตั้งแล้วได้อะไร

```text
AGENTS.md, CLAUDE.md, ANTIGRAVITY.md  # จุดเริ่มของ agent แต่ละตัว ข้อความของคุณยังอยู่
.ai/PROJECT_STATE.md                  # สถานะปัจจุบันของโปรเจกต์ (ของคุณ)
.ai/SESSION_LOG.md, .ai/RUNBOOK.md    # ประวัติและคำสั่งของโปรเจกต์ (ของคุณ)
.ai/MACHINE_PROFILE.md                # เครื่องนี้รันงานแบบไหนได้ (ของคุณ)
.ai/agent-project-kit/                # ตัว kit ถูกแทนที่เมื่ออัปเดต
```

prompt pack ของโปรเจกต์ให้เก็บใน `.ai/prompts/` หรือ folder อื่นที่ระบุไว้ใน
`.ai/PROJECT_STATE.md` ของที่อยู่ใน `.ai/agent-project-kit/` จะถูกแทนที่เมื่ออัปเดต

## ดูแลโปรเจกต์

ตรวจการติดตั้งและบันทึกโปรเจกต์

```bash
python3 .ai/agent-project-kit/scripts/apk_doctor.py . --quick
```

doctor รายงาน `PROJECT_STATE.md` ที่ยังไม่ได้กรอกหรือเก่าเกินไป เวอร์ชันที่ไม่ตรงกัน
`.ai/project.json` หรือ `.ai/apk.json` ที่ผิดรูปแบบ และข้อมูลรุ่นเก่าที่ agent มองไม่เห็น

โปรเจกต์รุ่นเก่าอาจมีบันทึกอยู่ใน `.ai/state.json` ซึ่ง agent ไม่อ่านแล้ว ให้ดูก่อน
แล้วค่อยย้ายเข้า `PROJECT_STATE.md`

```bash
python3 .ai/agent-project-kit/scripts/migrate_state.py --project .          # ดูอย่างเดียว
python3 .ai/agent-project-kit/scripts/migrate_state.py --project . --write  # ย้ายและสำรอง
```

การย้ายจะต่อท้ายหนึ่งส่วนที่มีเครื่องหมายกำกับ แล้วเปลี่ยนชื่อ `state.json` เป็นไฟล์
สำรองที่มีวันที่ ไม่มีการลบไฟล์ใด บน Windows ใช้ `py -3` แทน `python3`

## อัปเดตโปรเจกต์ที่ติดตั้งแล้ว

ดูก่อน แล้วค่อยอัปเดตจริง

```bash
bash .ai/agent-project-kit/scripts/update-from-pages.sh --dry-run .
bash .ai/agent-project-kit/scripts/update-from-pages.sh .
```

WSL2 กับ folder ที่ sync กับ Windows

```bash
KIT="${XDG_CACHE_HOME:-$HOME/.cache}/agent-project-kit"
bash "$KIT/scripts/update-from-pages.sh" --dry-run .
bash "$KIT/scripts/update-from-pages.sh" .
```

Windows PowerShell (ต้องมี Git และ Python 3.9 ขึ้นไป)

```powershell
powershell -ExecutionPolicy Bypass -File ".ai\agent-project-kit\scripts\update-from-pages.ps1" -ProjectPath . -DryRun
powershell -ExecutionPolicy Bypass -File ".ai\agent-project-kit\scripts\update-from-pages.ps1" -ProjectPath .
```

updater อ่าน manifest ที่เผยแพร่ checkout tag ของ release นั้นตรงตัว และไม่ยอม
downgrade หรือติดตั้งรุ่นที่เวอร์ชันไม่ตรง agent เช็กรุ่นใหม่อย่างมากทุก 14 วัน
และแจ้งเท่านั้น ไม่อัปเดตเอง รายละเอียดทั้งหมดอยู่ใน
[UPDATE_EXISTING_PROJECT.md](UPDATE_EXISTING_PROJECT.md)

## ความปลอดภัยของไฟล์

- บันทึกโปรเจกต์ใต้ `.ai/` ถูกสร้างเฉพาะเมื่อยังไม่มี และไม่ถูกเขียนทับ
- `AGENTS.md`, `CLAUDE.md` และ `ANTIGRAVITY.md` เก็บข้อความของคุณไว้ kit ดูแล
  block ที่มีเครื่องหมายกำกับหนึ่ง block ใน `AGENTS.md` และเพิ่มข้อความสั้น ๆ ในอีก
  สองไฟล์
- snapshot ใหม่ถูกเตรียมและตรวจ SHA-256 ก่อนแทนที่ของเดิม ของเดิมเก็บไว้เป็น
  `.ai/agent-project-kit.previous` ถ้าขั้นใดล้มเหลว ระบบคืน snapshot เดิมและทุกไฟล์
  ที่ตัวติดตั้งแตะ
- ถ้าเจอ folder หรือไฟล์ชื่อซ้ำที่ไม่ใช่ของ kit ตัวติดตั้งหยุดก่อนเขียนอะไร
- git clone และ snapshot ที่ติดตั้งใช้ path คนละที่

## ขั้นตอนการทำงานและ prompt pack

คุณไม่ต้องเลือก prompt pack เอง agent อ่าน `.ai/agent-project-kit/STARTUP.md`
จัดประเภทคำขอ แล้วโหลดขั้นตอนหลักหนึ่งชุดพร้อมจุดตรวจที่จำเป็น ถ้าอยากดูว่าคำขอ
หนึ่งถูกจัดเป็นงานแบบไหน

```bash
python3 .ai/agent-project-kit/scripts/route_task.py "เขียนบทที่ 3 ของตำรา"
```

ขั้นตอนครอบคลุมงานซอฟต์แวร์ งานวิจัย การเขียนหนังสือ สไลด์ การวิเคราะห์เนื้อหา
การวิเคราะห์ข้อมูล เอกสารประกอบการสอน นโยบายการศึกษา และงานธุรการ แต่ละขั้นตอน
มี prompt pack อยู่ใน `.ai/agent-project-kit/prompts/`

## Shared runtime สำหรับหลายโปรเจกต์บน WSL2 (Canary)

หลายโปรเจกต์บน WSL2 ใช้ kit ชุดเดียวที่ตรวจแล้วและระบุเวอร์ชันตายตัวร่วมกันได้
โดยเก็บไว้ที่ OneDrive root แต่ละโปรเจกต์ยังมีบันทึกของตัวเองและ snapshot สำรอง

```bash
PROJECT="/home/<user>/OneDrive/path/to/project"
KIT="${XDG_CACHE_HOME:-$HOME/.cache}/agent-project-kit"
APK_SHARED_ROOT="/home/<user>/OneDrive/.agent-project-kit"
APK_MACHINE_HOME="$HOME/.local/share/agent-project-kit"

# ครั้งเดียวต่อเครื่อง: ติดตั้งชุดกลางและตั้งค่า shell
python3 "$KIT/scripts/install-shared.py" --source "$KIT" \
  --shared-root "$APK_SHARED_ROOT" --machine-home "$APK_MACHINE_HOME" --configure-shell

# ต่อโปรเจกต์: ติดตั้ง snapshot สำรอง สำรอง binding เดิม แล้วผูก
bash "$KIT/scripts/install-to-project.sh" "$PROJECT" "$KIT"
[ -f "$PROJECT/.ai/apk.json" ] && cp -p "$PROJECT/.ai/apk.json" "$PROJECT/.ai/apk.json.backup-$(date +%Y%m%d)"
python3 "$KIT/scripts/install-shared.py" --source "$KIT" --bind-project "$PROJECT"

# ตรวจ
"$APK_MACHINE_HOME/bin/apk" --project "$PROJECT" resolve
```

`--configure-shell` เขียน block ที่มีเครื่องหมายกำกับหนึ่ง block ลง `~/.bashrc`
แล้วให้เปิด shell ใหม่ `resolve` ตรวจชุดกลางกับ SHA-256 ที่ผูกไว้ และปฏิเสธชุดที่ถูก
แก้ไข ถ้าจะกลับไปใช้ snapshot ของโปรเจกต์ ให้รัน
`python3 "$KIT/scripts/apk.py" --project "$PROJECT" rollback` และถ้าจะย้อนกลับ
ให้เปลี่ยนชื่อ `.ai/apk.json.disabled` กลับเป็น `.ai/apk.json` ควรลองกับไม่กี่
โปรเจกต์ก่อนผูกหลายโปรเจกต์

## แก้ปัญหาที่พบบ่อย

- `Agent Project Kit needs Python 3.9 or newer` ให้ติดตั้ง Python ตามหัวข้อ
  สิ่งที่ต้องมี แล้วเปิด terminal ใหม่
- `git not found` บน Windows ให้ติดตั้ง Git for Windows แล้วเปิด terminal ใหม่
  ถ้าเรียกจาก WSL2 ให้รีสตาร์ต WSL2 ก่อน
- `Input/output error` จาก WSL2 ใน OneDrive ส่วนใหญ่เป็นไฟล์ที่อยู่บน cloud อย่างเดียว
  ให้เปิดไฟล์นั้นจาก Windows หนึ่งครั้ง หรือตั้ง folder เป็น "Always keep on this
  device" แล้วลองใหม่ path ของ Windows ที่ยาวเกิน 260 ตัวอักษรก็ทำให้เกิด error นี้
  ให้ย่อหรือย้ายจาก PowerShell ด้วย `-LiteralPath`
- `Refusing to overwrite existing ...` มี folder หรือไฟล์ชื่อเดียวกับของ kit ที่เก็บ
  เนื้อหาของคุณอยู่ ให้เปลี่ยนชื่อแล้วรันตัวติดตั้งใหม่

## อ่านต่อ

- [CHANGELOG.md](CHANGELOG.md)
- [INSTALL_IN_PROJECT.md](INSTALL_IN_PROJECT.md)
- [UPDATE_EXISTING_PROJECT.md](UPDATE_EXISTING_PROJECT.md)
- [GIT_DISTRIBUTION.md](GIT_DISTRIBUTION.md)

repository นี้ไม่เก็บ `.ai/` เพราะเป็นสถานะเฉพาะเครื่องและ snapshot ที่ติดตั้ง
ชื่อเดิม `computing-environment` และ path `.ai/computing-environment/` เก็บไว้เพื่อ
ย้ายข้อมูลเท่านั้น
