# MACHINE_PROFILES

Machine profiles help AI agents avoid assuming that every project folder has the
same operating system, path layout, data cache, or runtime environment.

Use this document as the portable public policy. Put personal machine names,
sync-folder conventions, and family/team-specific setup notes in an ignored
local profile folder, not in the public package.

## Default Storage Model

- Source code, documents, specs, prompts, small sample data, and project state
  should live in the project folder or another intentionally synced/shared
  location.
- Large intermediate files, caches, model checkpoints, generated datasets,
  build artifacts, temporary exports, and heavy experiment outputs may live in
  machine-local storage.
- Anything outside the project folder may be missing on another machine and
  must be recorded in `.ai/LOCAL_RESOURCES.md`.
- Secrets and credentials must not be stored in project docs or committed files.

## Machine Roles

Projects should define their own machine labels in `.ai/MACHINE_PROFILE.md`.

Common role labels:

| Role | Expected Use | Portability Assumption |
|---|---|---|
| `primary-heavy` | Full builds, expensive tests, GPU/data-heavy runs | Check local resource manifest before use |
| `office-desktop` | Regular development and medium runs | Local resources may differ |
| `portable-laptop` | Editing, review, smoke tests, meetings, teaching | Avoid assuming large caches exist |
| `remote-server` | Deployment, services, batch jobs | Treat paths and permissions as machine-specific |
| `unknown` | New or unprofiled machine | Inspect before heavy work |

## Required Behavior For AI Agents

At the start of every non-trivial project session:

1. Detect or ask for the current machine identity if possible.
2. Read project-local files if they exist:
   - `.ai/PROJECT_STATE.md`
   - `.ai/MACHINE_PROFILE.md`
   - `.ai/LOCAL_RESOURCES.md`
   - `.ai/MACHINE_COMPATIBILITY.md`
   - `.ai/SESSION_LOG.md`
   - `.ai/RUNBOOK.md`
3. If `.ai/MACHINE_PROFILE.md` already has a fresh entry for the current
   machine, do the minimal resume check: hostname, OS/platform, path style, and
   whether required local paths still exist.
4. If the current machine is unknown, stale, or the platform/storage layout has
   changed, run first-use discovery and update `.ai/MACHINE_PROFILE.md` before
   heavy work.
5. Check whether required data/cache paths are available on the current machine.
6. If a task needs missing local files, do not declare the project broken. State
   what is missing and propose a smoke path, resource setup step, or compatible
   machine.
7. Do not hardcode machine-specific paths into source code. Use environment
   variables or config files.

## First-Use Discovery

Use this when a project is opened on a new machine, a known machine has changed
OS/storage layout, or the project is copied to a different sync/storage system.

Record the result in `.ai/MACHINE_PROFILE.md`:

- machine identity: hostname, human label if known, OS, shell, architecture
- execution context: Windows-native, WSL2, macOS, Linux, container, SSH/remote
- project path style: `C:\...`, `/mnt/c/...`, `/Users/...`, `/home/...`, or other
- sync/storage assumption: local disk, shared/synced project storage, iCloud, Dropbox, network drive,
  external drive, remote server, unknown
- available interpreters/package managers: Python, conda/mamba, Node,
  PowerShell, shell
- GPU/accelerator summary when relevant
- project-specific local paths checked from `.ai/LOCAL_RESOURCES.md`
- recommended task level on this machine: edit, smoke, medium, full/heavy
- last verified date and command/source used

Useful shell commands:

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

Useful Windows PowerShell commands:

```powershell
$env:COMPUTERNAME
[System.Environment]::OSVersion.VersionString
Get-Location
Get-PSDrive -PSProvider FileSystem
```

## Resume Check

Use this when `.ai/MACHINE_PROFILE.md` already has a current entry for the
machine.

Check only:

```bash
hostname
uname -a  # or platform equivalent
pwd
```

Then read the matching machine row in `.ai/MACHINE_PROFILE.md` and verify only
the local paths needed for the current task. Do not rescan hardware, package
managers, or broad storage unless the identity/path does not match or the task
needs resources not yet recorded.

## Package Update Check

When `.ai/computing-environment/` is updated in an existing project, read
`.ai/COMPUTING_ENVIRONMENT_VERSION.md` before deciding to rescan the machine.

- If only the package version changed, reuse the existing machine profile.
- If `machine_profile_schema_version` changed, migrate/fill missing profile
  fields but do not discard the old profile.
- If hostname, platform, path style, or sync/storage layout changed, refresh the
  profile before heavy work.

## Path Policy

Prefer this split:

| Resource Type | Preferred Location | Portable? | Notes |
|---|---|---:|---|
| Source code / manuscript / slides / specs | Project folder or synced source folder | Usually | Keep small and intentional |
| Small fixtures / tiny sample data | Project folder | Yes | Use for smoke tests |
| Python virtualenv, `node_modules`, build cache | Machine-local | No | Recreate per machine |
| Large datasets / model checkpoints / generated caches | Machine-local or external storage | No | Must be recorded in `.ai/LOCAL_RESOURCES.md` |
| Final figures/reports | Project folder if deliverable | Usually | Keep reproducible sources |
| Secrets / credentials | Secret manager or ignored env files | No | Never commit real secrets |

## Environment Variable Convention

When code needs non-portable resources, prefer environment variables such as:

```bash
PROJECT_DATA_ROOT=/path/to/large/dataset
PROJECT_CACHE_ROOT=/path/to/cache
PROJECT_OUTPUT_ROOT=/path/to/nonportable/outputs
```

The project should include `.env.example` or `.ai/ENVIRONMENT_VARIABLES.md`, not
real secrets.

## Hard Rule

If a project uses files outside the project folder or outside the shared/synced
source tree, record them in `.ai/LOCAL_RESOURCES.md`. Otherwise the next machine
switch will waste time.
