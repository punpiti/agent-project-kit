# MACHINE_PROFILES — WSL2 + OneDrive Multi-Machine Setup

ไฟล์นี้คือบริบทเครื่องหลักของผู้ใช้ สำหรับให้ Codex / IDE agent / AI agent ใช้ตัดสินใจก่อนรันงานหนักหรือสร้าง path ภายนอก OneDrive

## Default Storage Model

- Source code, documents, specs, prompts, small sample data, and project state should live under **Windows OneDrive** so they sync across machines.
- Codex is usually run inside **WSL2**.
- OneDrive folders from Windows are accessed in WSL2 through `/mnt/c/...` or another mounted Windows drive.
- Large intermediate files, cache, model checkpoints, generated datasets, build artifacts, temporary exports, and heavy experiment outputs may live outside OneDrive.
- Anything outside OneDrive is **not portable** and may be missing on another machine.

## Machine Roles

| Machine | Hardware / Role | Expected Use | Portability Assumption |
|---|---|---|---|
| `think` | Xeon PC | Main heavy-run machine. At home and sometimes moved to the garden on weekends. | Treat as the machine that can run every project unless proven otherwise. |
| `madlab-i9` | Core i9 PC | Office machine. Good for serious work, but may not have all local caches or external HDD paths. | Check local resource manifest before heavy runs. |
| `black5` | Core i7 notebook | Always with the user. Best for editing, review, light experiments, meetings, teaching work, and project steering. | Avoid assuming large caches exist. Prefer lightweight tasks unless manifest says otherwise. |
| other / unknown | Less-used machines | Use cautiously. | Inspect first; do not assume external resources exist. |

## Required Behavior for AI Agents

At the start of every non-trivial project session:

1. Detect or ask for the current machine name if possible.
2. Read project-local files if they exist:
   - `.ai/PROJECT_STATE.md`
   - `.ai/MACHINE_PROFILE.md`
   - `.ai/LOCAL_RESOURCES.md`
   - `.ai/MACHINE_COMPATIBILITY.md`
   - `.ai/SESSION_LOG.md`
   - `.ai/RUNBOOK.md`
3. If `.ai/MACHINE_PROFILE.md` already has a fresh entry for the current
   machine, do the minimal resume check: `hostname`, OS/platform, WSL2 yes/no,
   current path style, and whether required local paths still exist.
4. If the current machine is unknown, stale, or the platform/storage layout has
   changed, run first-use discovery and update `.ai/MACHINE_PROFILE.md` before
   heavy work.
5. Check whether required data/cache paths are available on the current machine.
6. If a task needs large local files and the current machine is not marked compatible, say so directly and suggest running on `think` or updating `.ai/LOCAL_RESOURCES.md`.
7. Do not hardcode machine-specific paths into code. Use environment variables or config files.
8. Keep a small portable smoke-test path under OneDrive when feasible.

## Two-Stage Machine Protocol

### First-use discovery

Use this when a project is opened on a new machine, a known machine has changed
OS/storage layout, or the project is copied outside the user's usual OneDrive
setup.

Record the result in `.ai/MACHINE_PROFILE.md`:

- machine identity: hostname, human label if known, OS, shell, architecture
- execution context: WSL2, Windows-native, macOS, Linux, container, SSH/remote
- project path style: `/mnt/c/...`, `/home/...`, `C:\...`, `/Users/...`, or other
- sync/storage assumption: OneDrive personal/business, iCloud, local disk, network drive, unknown
- available interpreters/package managers: Python, conda/mamba, Node, PowerShell, shell
- GPU/accelerator summary when relevant
- project-specific local paths checked from `.ai/LOCAL_RESOURCES.md`
- recommended task level on this machine: edit, smoke, medium, full/heavy
- last verified date and command/source used

Recommended commands:

```bash
hostname
uname -a
printf '%s\n' "$PWD"
test -r /proc/version && grep -iE 'microsoft|wsl' /proc/version || true
df -h . /
command -v python3 || command -v python || true
command -v pwsh || command -v powershell || true
command -v nvidia-smi >/dev/null 2>&1 && nvidia-smi || true
```

On Windows-native PowerShell, use:

```powershell
$env:COMPUTERNAME
[System.Environment]::OSVersion.VersionString
Get-Location
Get-PSDrive -PSProvider FileSystem
```

On macOS, also check whether the project is under iCloud, OneDrive, or a local
folder. Do not assume the WSL2/OneDrive rules fit macOS until the profile says
so.

### Resume check

Use this when `.ai/MACHINE_PROFILE.md` already has a current entry for the
machine.

Check only:

```bash
hostname
uname -a  # or platform equivalent
pwd
```

Then read the matching machine row in `.ai/MACHINE_PROFILE.md` and only verify
required local paths for the current task. Do not rescan hardware, package
managers, or broad storage unless the identity/path does not match or the task
needs resources not yet recorded.

### Package update check

When `.ai/computing-environment/` is updated in an existing project, read
`.ai/COMPUTING_ENVIRONMENT_VERSION.md` before deciding to rescan the machine.

- If only the package version changed, reuse the existing machine profile.
- If `machine_profile_schema_version` changed, migrate/fill missing profile
  fields but do not discard the old profile.
- If hostname, platform, path style, or sync/storage layout changed, refresh the
  profile before heavy work.

## Path Policy

Prefer this split:

| Resource Type | Preferred Location | Sync? | Notes |
|---|---|---:|---|
| Source code / manuscript / slides / specs | OneDrive project folder | Yes | Portable across machines |
| Small fixtures / tiny sample data | OneDrive project folder | Yes | Use for smoke tests |
| Python virtualenv, node_modules, build cache | WSL-local or machine-local | No | Recreate per machine |
| Large datasets / radar data / image caches / model checkpoints | WSL-local or HDD | No | Must be recorded in `.ai/LOCAL_RESOURCES.md` |
| Generated figures for paper/report | Usually OneDrive if final, local cache if intermediate | Depends | Final artifacts should be portable; massive intermediates should not |
| Secrets / credentials | Never in OneDrive project docs | No | Use local secret manager or ignored env files |

## Environment Variable Convention

When code needs non-portable resources, prefer environment variables such as:

```bash
PROJECT_DATA_ROOT=/path/to/large/dataset
PROJECT_CACHE_ROOT=/path/to/cache
PROJECT_OUTPUT_ROOT=/path/to/nonportable/outputs
```

The project should include `.env.example` or `.ai/ENVIRONMENT_VARIABLES.md`, not real secrets.

## Hard Rule

If a project uses files outside OneDrive, record them in `.ai/LOCAL_RESOURCES.md`. Otherwise the next machine switch will waste time.

If a project is not on the user's WSL2 + Windows OneDrive layout, record that in
`.ai/MACHINE_PROFILE.md` instead of forcing the default assumptions onto the
project.
