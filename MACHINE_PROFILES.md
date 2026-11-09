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

## Source-Of-Truth Storage Tiers

The full tier model (`git`, `durable` cloud drive, `hot` SSD, `cold` HDD,
`scratch`), rebuild classes, and cache placement live in
`DATA_FLOW_POLICY.md`. In short: the Git remote plus the synced folder are the
only source of truth; everything on a machine's SSD/HDD must be rebuildable
from them or be recorded as a backup copy.

Machine-specific steps:

- Record each machine's storage devices (SSD, HDD, external), sync clients,
  and network-cost status in `.ai/MACHINE_PROFILE.md`.
- Migrate repos out of synced folders one at a time: confirm everything is
  pushed, move gitignored durable files into the synced folder, clone fresh on
  the `hot` tier, verify, then remove the synced copy only after the user
  confirms.

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
6. If the task could benefit from parallel execution, decide the local
   parallelism policy before running it. Check CPU core count, GPU/accelerator
   type and availability, RAM, storage pressure, thermal/remote-session
   constraints when relevant, and any project-specific resource limits. Choose a
   conservative worker count or batch size, record the reasoning in the session
   report, and prefer a small smoke run before heavy parallel work.
7. If a task needs missing local files, do not declare the project broken. State
   what is missing and propose a smoke path, resource setup step, or compatible
   machine.
8. Do not hardcode machine-specific paths into source code. Use environment
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
- available interpreters/package managers: Python, micromamba/mamba/conda, Node,
  PowerShell, shell
- GPU/accelerator summary when relevant
- parallel execution readiness: CPU core count, usable GPU/accelerator,
  memory/storage constraints, and recommended worker count or batch-size range
- project-specific local paths checked from `.ai/LOCAL_RESOURCES.md`
- recommended task level on this machine: edit, smoke, medium, full/heavy
- last verified date and command/source used

Useful shell commands:

```bash
hostname
uname -a
printf '%s\n' "$PWD"
test -r /proc/version && grep -iE 'microsoft|wsl' /proc/version || true
nproc 2>/dev/null || getconf _NPROCESSORS_ONLN 2>/dev/null || true
command -v lscpu >/dev/null 2>&1 && lscpu | sed -n '1,20p' || true
free -h 2>/dev/null || true
df -h . /
command -v python3 || command -v python || true
command -v micromamba || command -v mamba || command -v conda || true
command -v pwsh || command -v powershell || true
command -v nvidia-smi >/dev/null 2>&1 && nvidia-smi || true
```

Useful Windows PowerShell commands:

```powershell
$env:COMPUTERNAME
[System.Environment]::OSVersion.VersionString
Get-Location
Get-PSDrive -PSProvider FileSystem
Get-CimInstance Win32_Processor | Select-Object Name,NumberOfCores,NumberOfLogicalProcessors
Get-CimInstance Win32_VideoController | Select-Object Name,AdapterRAM
Get-CimInstance Win32_OperatingSystem | Select-Object TotalVisibleMemorySize,FreePhysicalMemory
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

## Compute Nodes And Dispatch

When a user has several machines that can run work over SSH, keep a node
inventory and send heavy jobs to the node with the most free capacity, no
matter which machine the session runs on.

- Inventory: a machine-local JSON file read by `scripts/compute_nodes.py`
  (template `templates/compute-nodes.example.json`). It lists each node's role
  (`hub` main node that steers work, `compute`, `mobile`, `client`), SSH alias, CPU cores/threads (and the threads
  WSL2 exposes), RAM, GPU, and storage by tier (`hot` SSD, `cold` HDD,
  `durable` synced) with mount points. Machine names and aliases are private:
  keep the file in an ignored local profile and point `APK_COMPUTE_NODES` at
  it. Do not symlink it into a synced folder.
- Storage is more than SSD and HDD. Each node also declares how it reaches
  the two sources of truth in `DATA_FLOW_POLICY.md`: `git` (GitHub access:
  `ssh`, `gh+ssh`, or `null`) and `cloud_drives` (tier `durable`: a synced
  folder `path` or an `rclone_remote`, with the provider). The same drive can
  sit at a different path on each machine, so record the path per node.
- A node whose key is authorized only on one machine sets `via` to that
  machine; other machines reach it as `ssh <via> ssh <alias>`. Machines that
  later get their own key go in the node's `direct_from` list and connect
  directly.
- `python3 scripts/compute_nodes.py status` shows which nodes are up with
  load, free threads, free memory, GPU use, and free space per listed mount.
  Add `--watch 30` to monitor. Probes are read-only.
- `pick --min-threads N [--min-mem-gb G] [--gpu]` returns the reachable node
  with the most free threads (`threads - load1`, times `thread_weight`), so a
  large node at half load beats a small idle one. Nodes with
  `"dispatch": false` are never picked. Exit code 3 means none fits: say so and
  propose waiting, a smaller run, or a lower requirement instead of
  overloading a node.
- Each node records its `network`: `type` (`infra`, `home`, `mobile`) and
  `metered` (`false`, `true`, or `"sometimes"`). Unless it is `false`, the
  probe reads the live Windows connection cost, and an unknown cost counts as
  metered. The inventory's `egress` list orders the nodes to use for GitHub
  pushes, clones, and large downloads; `compute_nodes.py egress` returns the
  first one that is up, unmetered, and has `github`. If none qualifies, ask
  before downloading on a metered link (`DATA_FLOW_POLICY.md` "Metered
  links").
- `status` shows each node's channels: installed `git`, `rsync`, `rclone`,
  `gh`, plus `github` and one slug per reachable cloud drive (`onedrive`,
  `googledrive`). `--check-github` verifies GitHub SSH auth instead of trusting
  the inventory. `pick --needs git,onedrive` keeps only nodes with those
  channels.
- Moving work to a node follows the tiers. Code: `git pull` on the target when
  it has `github`, otherwise `rsync` from a node that has the clone; never copy
  a working tree out of a synced folder. Inputs: read `durable` files on a node
  that has that cloud drive, or copy the needed subset to the target's `hot` or
  `cold` tier first. Results: final deliverables go back to `durable` or are
  committed to `git`; intermediates stay on the target and are recorded in
  `.ai/LOCAL_RESOURCES.md` with the node name.
- Before `run`, confirm the target has the code, data paths
  (`.ai/LOCAL_RESOURCES.md`), and environment. Put job data on the target's
  `hot` tier and large inputs or outputs on its `cold` tier, not on a synced
  folder. Use `nohup`, `tmux`, or a scheduler for long jobs, and record the
  node, path, and command in the session report.
- Shared nodes carry other users' load. Respect it: never kill or renice
  processes you did not start.

## Session Sync Across Machines

Clones live outside synced folders, so work reaches other machines only when
it is pushed. `scripts/projects_sync.py` does the routine part for every clone
under one root (inventory key `projects_sync`: `root`, `hub`, `backup_remote`,
`extra_paths`; see the template):

- `start`: fetch, fast-forward branches that are only behind, and pull newer
  non-Git files (`.ai/`, `.env.local`) from the hub with `rsync --update`.
- `end`: push branches that are only ahead, mirror all branches and tags to the
  backup remote (bare repos on the hub), push newer non-Git files to the hub,
  and list uncommitted work, which is not backed up anywhere.
- `status`: ahead/behind/uncommitted counts only.

It detects the machine by hostname, skips the non-Git copy on the hub itself,
and never commits, merges diverged branches, rebases, stashes, or deletes.
Exit code 1 means something needs a person; report those lines. Run `start`
before work and `end` before leaving a machine; an agent client may run them
from session start/end hooks.

## Package Update Check

When `.ai/agent-project-kit/` is updated in an existing project, read
`.ai/COMPUTING_ENVIRONMENT_VERSION.md` before deciding to rescan the machine.

- If only the package version changed, reuse the existing machine profile.
- If `machine_profile_schema_version` changed, migrate/fill missing profile
  fields but do not discard the old profile.
- If hostname, platform, path style, or sync/storage layout changed, refresh the
  profile before heavy work.

## Path Policy

### WSL2 long-path / OneDrive recovery note

On a Windows-backed OneDrive workspace, WSL2 may report an I/O error when a
path or filename becomes too long even though the file is still visible from
Windows. Do not keep retrying rename/delete operations from the Linux side.
First check that no process has the file open, then use Windows PowerShell with
the Windows path and `-LiteralPath` to rename or move the item to a shorter
path. Reopen WSL2 and verify the result afterward. Use the `\\?\` extended-path
prefix only when the normal PowerShell path still fails and the target has been
resolved exactly.

A single name component is also limited to 255 bytes on the WSL2 side, counted
in UTF-8, while Windows counts 255 UTF-16 units. Thai takes 3 UTF-8 bytes per
character, so a Thai name of about 85+ characters is fine in Windows but gives
`Input/output error` in WSL2 even when the full path is short. Find such names
from PowerShell with `[Text.Encoding]::UTF8.GetByteCount($_.Name) -gt 255`
and rename them with `Rename-Item -LiteralPath`. Put Thai names in a `.ps1`
file and run it with `pwsh -File` instead of passing them inline through the
WSL2 shell. When naming new files in a synced folder, keep Thai names under
about 80 characters.

### OneDrive stops syncing

If OneDrive in a WSL2 workspace stops syncing or stays stuck on "processing",
check for two causes:

1. Symlinks created from WSL2 inside the sync root, including the
   `bin/python*` links inside a Python virtualenv. OneDrive cannot sync them.
   List them with `find . -type l` and save each link with its `readlink`
   target to a manifest outside the sync root. Then remove them with
   `rm -- <link>` (no trailing slash, so the target is untouched). After that,
   recreate any virtualenv machine-locally.
2. Names over 255 UTF-8 bytes (see above). `find` reports their parent folders
   as `Input/output error`.

Rerun both scans and expect zero results. Folders with attributes
`Directory, ReparsePoint` and an empty `LinkType` in PowerShell are OneDrive
cloud placeholders, not symlinks. Leave them alone.

Prefer this split:

| Resource Type | Preferred Location | Portable? | Notes |
|---|---|---:|---|
| Source code / manuscript / slides / specs | Project folder or synced source folder | Usually | Keep small and intentional |
| Small fixtures / tiny sample data | Project folder | Yes | Use for smoke tests |
| Python virtualenv, `node_modules`, build cache | Machine-local | No | Recreate per machine |
| Large datasets / model checkpoints / generated caches | Machine-local or external storage | No | Must be recorded in `.ai/LOCAL_RESOURCES.md` |
| Final figures/reports | Project folder if deliverable | Usually | Keep reproducible sources |
| Secrets / credentials | Secret manager or ignored env files | No | Never commit real secrets |

## Conda-Family Environment Policy

Use the first available manager in this order: `micromamba`, `mamba`,
`conda`. Use it to access shared machine-local environments
and route work to the smallest suitable environment:

| Environment | Intended work |
|---|---|
| `text` | Document processing/generation, PDF-to-text, LaTeX, Pandoc, Markdown, PDF, DOCX, HTML, and text utilities |
| `image` | OpenCV, image and video processing, Tesseract, and OCR |
| `ml` | Machine-learning training, inference, evaluation, and model tooling |

CUDA and other GPU-specific packages are opt-in. Before installing them, verify
the target GPU, driver status, platform, and framework/CUDA compatibility. If
that evidence is missing or inconclusive, use the non-CUDA `ml` baseline and do
not install GPU runtime packages.

Prefer `<available-manager> run -n <environment> <command>` in scripts and
agent-run commands. Do not create `venv`, `.venv`, or equivalent per-project
environment copies because they duplicate dependencies and consume unnecessary
disk space. If a task-required library is absent, select the project-declared
shared environment or the narrowest of `text`, `image`, and `ml`; reproduce the
failure there; install the smallest compatible direct dependency into that
environment; and verify the import/command plus focused task check. Prefer
Conda, with pip inside the selected environment only when needed. If the
standard environment is absent, create it from the matching undated manifest.
Record meaningful machine changes in `.ai/LOCAL_RESOURCES.md`; do not treat
their absence on one machine as a broken project or silently create `.venv`.

Environment installation is demand-driven, not part of routine startup. Create
or update an environment only when the current task requires it. Announce and
proceed with ordinary scoped repairs. Warn and obtain approval before
potentially large downloads, metered-network transfers, GPU/CUDA changes,
root/admin operations, or transactions that may remove/replace packages.

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
