# INSTALL_IN_PROJECT

ไฟล์นี้อธิบายวิธีเอา Agent Project Kit ไปผูกกับแต่ละ project

ชื่อ package ปัจจุบันคือ `agent-project-kit` / Agent Project Kit ส่วน
`computing-environment` เป็นชื่อ/path เดิมที่ยังรองรับเพื่อ compatibility

## วิธีที่แนะนำสำหรับ WSL2

## วิธีแจกให้คนอื่นแบบ Git clone

ให้ clone/update kit เข้า project ที่จะใช้งาน แล้ว install snapshot:

```bash
bash /path/to/agent-project-kit/scripts/install-from-git.sh . https://github.com/<owner>/agent-project-kit.git v6.5.0
```

โครงสร้างหลังติดตั้ง:

```text
.ai/agent-project-kit/        # git clone ของ kit
.ai/computing-environment/    # installed snapshot ที่ agent อ่าน
.ai/PROJECT_STATE.md          # state ของ project นี้ ไม่อยู่ใน clone
```

เวลาอัปเดต ให้รันคำสั่งเดิมโดยเปลี่ยน tag/ref ได้ เช่น `v6.5.1` หรือ `main`
สำหรับคนที่ไว้ใจและอยากได้รุ่นล่าสุด

## วิธีใช้จาก local folder

ให้แตกโฟลเดอร์นี้ไว้ที่ OneDrive ฝั่ง Windows โดยใช้ชื่อใหม่หรือชื่อเดิม:

```text
C:\Users\<windows-user>\OneDrive\agent-project-kit
C:\Users\<windows-user>\OneDrive\computing-environment
```

ใน WSL2 จะเห็นประมาณ:

```bash
/mnt/c/Users/<windows-user>/OneDrive/agent-project-kit
/mnt/c/Users/<windows-user>/OneDrive/computing-environment
```

จาก root ของ project ให้รัน:

```bash
bash /mnt/c/Users/<windows-user>/OneDrive/agent-project-kit/scripts/install-to-project.sh .
```

หรือระบุ source path เอง:

```bash
bash /path/to/agent-project-kit/scripts/install-to-project.sh /path/to/project /path/to/agent-project-kit
```

ถ้ายังใช้ folder เดิม `computing-environment` อยู่ คำสั่งแบบเดิมยังใช้ได้

script จะสร้างหรืออัปเดต โดยยังใช้ `.ai/computing-environment/` เป็น installed
snapshot path เพื่อไม่ทำให้ project เดิมพัง:

```text
AGENTS.md
CLAUDE.md
ANTIGRAVITY.md
.ai/computing-environment/
```

และจะสร้างไฟล์ project-local ถ้ายังไม่มี:

```text
.ai/PROJECT_STATE.md
.ai/PROJECT_HIERARCHY.md
.ai/COMPUTING_ENVIRONMENT_VERSION.md
.ai/MACHINE_PROFILE.md
.ai/LOCAL_RESOURCES.md
.ai/MACHINE_COMPATIBILITY.md
.ai/RUNBOOK.md
.ai/TOKEN_BUDGET.md
.ai/SESSION_LOG.md
.ai/ENVIRONMENT_VARIABLES.md
```

ไฟล์ project-local เหล่านี้ควรอยู่กับ project เพื่อ sync ผ่าน OneDrive และช่วย resume งานข้ามเครื่อง

## ใช้กับ Claude / Antigravity / agent อื่น

installer จะสร้างหรือ append adapter files แบบไม่ทับของเดิม:

```text
CLAUDE.md
ANTIGRAVITY.md
```

ไฟล์สองตัวนี้เป็น pointer สั้น ๆ ให้ AI client อ่าน `AGENTS.md`,
`.ai/computing-environment/`, และไฟล์ state ใน `.ai/` ก่อนทำงานจริง นโยบายหลัก
ยังอยู่ใน `AGENTS.md` และ `.ai/` เพื่อไม่ให้ policy แยกกันคนละชุดตามชื่อ AI
client

## Self-hosting / recursion guard

ถ้าติดตั้ง package นี้กลับเข้าไปใน repo `computing-environment` เอง ให้ถือว่า:

- root-level `START_HERE.md`, `AGENTS.md`, และไฟล์ governance อื่นคือ canonical source
- `.ai/computing-environment/` คือ installed snapshot สำหรับทดสอบ downstream project
- agent ไม่ควรอ่านซ้อนเข้าไปอีกชั้นหนึ่ง เว้นแต่ผู้ใช้สั่งให้ตรวจ packaged copy โดยตรง

---

## สำหรับ Windows PowerShell

```powershell
powershell -ExecutionPolicy Bypass -File "$env:OneDrive\agent-project-kit\scripts\install-to-project.ps1" -ProjectPath .
```

ถ้า OneDrive ไม่ได้อยู่ที่ `$env:OneDrive`:

```powershell
powershell -ExecutionPolicy Bypass -File "C:\Users\<ชื่อผู้ใช้>\OneDrive\agent-project-kit\scripts\install-to-project.ps1" -ProjectPath "D:\path\to\project" -SourcePath "C:\Users\<ชื่อผู้ใช้>\OneDrive\agent-project-kit"
```

---

## หลังติดตั้งแล้ว เริ่มคุยกับ AI แบบนี้

```text
อ่าน AGENTS.md และ .ai/computing-environment ก่อน
จากนั้น inspect project นี้ แล้วทำ Existing Project Onboarding ตาม Spec–Eval–Loop Workflow
ต้องตรวจ .ai/PROJECT_STATE.md, .ai/PROJECT_HIERARCHY.md, .ai/COMPUTING_ENVIRONMENT_VERSION.md, .ai/MACHINE_PROFILE.md, .ai/LOCAL_RESOURCES.md, .ai/MACHINE_COMPATIBILITY.md, .ai/RUNBOOK.md, .ai/TOKEN_BUDGET.md ด้วย
```

หรือถ้าจะสั่งงานทันที:

```text
อ่าน AGENTS.md และ .ai/computing-environment ก่อน
ตรวจ current machine, .ai/MACHINE_PROFILE.md, และ local resources
แล้วทำ task นี้ตาม Spec–Eval–Loop Workflow:
[ใส่โจทย์]
```

สำหรับเครื่องใหม่หรือ project ที่ไม่ได้อยู่บน WSL2 + Windows OneDrive ให้ตรวจ
ละเอียดและบันทึก `.ai/MACHINE_PROFILE.md` ก่อนรันงานหนัก รอบถัดไปถ้า hostname,
platform, และ path style ยังตรง ให้ตรวจขั้นต่ำแล้ว reuse profile เดิมได้

เวลา update package ใน project เดิม installer จะ refresh
`.ai/computing-environment/` และ `.ai/COMPUTING_ENVIRONMENT_VERSION.md` แต่จะไม่
overwrite state/profile/resource files ที่มีอยู่ ถ้า machine profile schema
ไม่เปลี่ยน ไม่ต้องตรวจเครื่องใหม่ทั้งหมด

## ถ้าอยากประหยัด token / ค่า AI

ตั้งค่าใน `.ai/TOKEN_BUDGET.md`:

```text
Default token mode: T1 Standard
Default cost profile: C0 Economy
```

เมื่อเป็น `C0 Economy` agent ควรถามก่อนทำงานที่กิน token สูง เช่น scan repo กว้าง,
web research หลายแหล่ง, test/debug loop ยาว, หรือ rewrite ไฟล์จำนวนมาก ถ้าผู้ใช้
เลือกโมเดลประหยัดอยู่แล้ว ให้ agent ถือว่าใกล้ `C0 Economy` และเสนอทางเลือก
`Economy / Standard / Deep` ก่อน เว้นแต่ผู้ใช้สั่งชัดว่าให้ทำต่อ

---

## ถ้า project ใช้ cache/intermediate/data นอก OneDrive

ให้บันทึกไว้ใน:

```text
.ai/LOCAL_RESOURCES.md
```

และระบุว่าแต่ละเครื่องมี path อะไรบ้าง:

- `think`
- `madlab-i9`
- `black5`
- other/unknown

อย่าปล่อยให้ AI หรือมนุษย์เดาว่าไฟล์อยู่ไหน เพราะจะเสียเวลาทุกครั้งที่สลับเครื่อง

---

## ถ้าไม่อยากให้ไฟล์ `.ai/` ถูก commit เข้า Git

เพิ่มใน `.gitignore` เองตามความเหมาะสม เช่น:

```gitignore
# AI working state; keep in OneDrive, not necessarily in Git
.ai/
```

แต่ถ้า project ใช้ OneDrive เป็นหลัก การมี `.ai/` อยู่ใน project จะช่วย sync state ข้ามเครื่องได้มาก
