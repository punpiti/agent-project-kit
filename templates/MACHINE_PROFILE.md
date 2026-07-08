# MACHINE_PROFILE

บันทึก identity และ storage/runtime layout ของเครื่องที่ project นี้เคยถูกเปิดใช้
เป้าหมายคือรอบแรกตรวจละเอียด รอบถัดไปตรวจขั้นต่ำแล้ว reuse ความรู้เดิมได้

## Resume Rule

ถ้า hostname/platform/current path ยังตรงกับ profile ล่าสุด ให้ตรวจขั้นต่ำ:

```bash
hostname
uname -a
pwd
```

จากนั้นตรวจเฉพาะ local resource ที่ task นี้ต้องใช้จาก `.ai/LOCAL_RESOURCES.md`
ไม่ต้อง rescan hardware/package manager ทั้งหมดทุกครั้ง

ถ้าเป็นเครื่องใหม่, profile เก่ากว่า 30 วันสำหรับงาน runtime หนัก, path style
เปลี่ยน, sync folder เปลี่ยน, OS/runtime เปลี่ยน, หรือ
`machine_profile_schema_version` ใน `.ai/COMPUTING_ENVIRONMENT_VERSION.md`
เปลี่ยน ให้ทำ first-use discovery หรือ migrate field ที่ขาด แล้วอัปเดตไฟล์นี้
ก่อนรันงานหนัก

## Machine Profiles

| Machine label | Hostname | OS / platform | Context | Project path style | Sync/storage assumption | Recommended task level | Last verified | Notes |
|---|---|---|---|---|---|---|---|---|
| `think` |  |  | WSL2 / Windows-native / macOS / Linux / container / unknown |  |  | edit/smoke/medium/full/heavy/unknown |  |  |
| `madlab-i9` |  |  | WSL2 / Windows-native / macOS / Linux / container / unknown |  |  | edit/smoke/medium/full/heavy/unknown |  |  |
| `black5` |  |  | WSL2 / Windows-native / macOS / Linux / container / unknown |  |  | edit/smoke/medium/full/heavy/unknown |  |  |
| other |  |  | unknown |  |  | unknown |  |  |

## Current Machine Snapshot

- Machine label:
- Hostname:
- Verified on:
- Verified by:
- OS / platform:
- Architecture:
- Context: WSL2 / Windows-native / macOS / Linux / container / SSH / unknown
- Current project path:
- Path style:
- Sync/storage assumption:
- Shell:
- Python:
- Package manager:
- GPU/accelerator:
- Required local resources checked:
- Missing local resources:
- Recommended task level:

## First-Use Discovery Commands

Use the commands that fit the current platform. Record only stable facts; do not
store secrets.

### Linux / WSL2 / macOS shell

```bash
hostname
uname -a
pwd
test -r /proc/version && grep -iE 'microsoft|wsl' /proc/version || true
df -h . /
command -v python3 || command -v python || true
python3 --version 2>/dev/null || python --version 2>/dev/null || true
command -v conda || command -v micromamba || true
command -v node || true
command -v pwsh || command -v powershell || true
command -v nvidia-smi >/dev/null 2>&1 && nvidia-smi || true
```

### Windows PowerShell

```powershell
$env:COMPUTERNAME
[System.Environment]::OSVersion.VersionString
Get-Location
Get-PSDrive -PSProvider FileSystem
Get-Command python, py, pwsh, powershell, node -ErrorAction SilentlyContinue
```

### macOS-specific checks

```bash
sw_vers
uname -m
pwd
df -h .
```

Check whether the project is under iCloud, OneDrive, Dropbox, a local folder, or
a network mount. Do not apply WSL2/Windows OneDrive assumptions until recorded
here.
