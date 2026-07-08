# My Computing Environment

ข้อมูลสิ่งแวดล้อมการคำนวณกลางของผม สำหรับใช้ข้ามโปรเจกต์ใน OneDrive:
เครื่อง, CPU/RAM/GPU, Python/runtime, local LLM/Ollama, deployment hosts,
GitHub remotes, websites, model archives, and other compute constraints.

Canonical location:

```text
/home/punpiti/OneDrive/computing-environment/README.md
```

Compatibility symlink:

```text
/home/punpiti/OneDrive/MACHINE_RESOURCES.md
```

Last updated: 2026-06-30

## Rules

- Treat this file as the cross-project source of truth for my computing
  environment, not just hardware specs.
- For any new OneDrive project, read this file before assuming where to run
  heavy compute, local LLM, GPU, deployment, GitHub, or website work.
- When a project discovers a new machine, GPU, Python/runtime setup, deployment
  host, GitHub remote, website URL, model archive, or resource constraint,
  update this file first or add a clearly marked TODO here.
- Keep project-specific path issues in the project notes, not here.
- When a spec is inferred from an old notebook, mark it as unconfirmed until
  verified with `hostname` and `nvidia-smi`.
- Do not assume another person's workstation is available just because its GPU
  appears in a shared notebook.

## New Project Checklist

At the start of a new project or when moving work to another machine:

1. Read this file.
2. Identify the intended machine and confirm current resources with the scan
   commands below.
3. Check whether the project has a GitHub remote, website, deployment host, or
   large local model/data dependency that should be recorded here.
4. Register where the project is running with
   `tools/register_project_run.sh`.
5. Add or update entries in this file when the answer changes.

## Environment Policy

Cross-project dependency environments should stay machine-local, not inside
OneDrive project folders. See the detailed policy:

```text
/home/punpiti/OneDrive/computing-environment/ENVIRONMENT_POLICY.md
```

## Project Runtime Inventory

Use this as the cross-machine log for projects that have been started,
deployed, or moved between machines.

Canonical log:

```text
/home/punpiti/OneDrive/computing-environment/PROJECT_RUNS.md
```

Register a new run from inside the project directory:

```bash
/home/punpiti/OneDrive/computing-environment/tools/register_project_run.sh \
  --project "Urban AI" \
  --command "ollama run qwen3:8b" \
  --port "11434" \
  --url "http://localhost:11434" \
  --notes "local smoke test"
```

Minimum form:

```bash
/home/punpiti/OneDrive/computing-environment/tools/register_project_run.sh \
  --project "Project name"
```

Rules for this log:

- Add a row every time a project starts running on a new machine, moves to a
  different host, changes port/URL, or changes from test to production use.
- Mark old rows as superseded in `PROJECT_RUNS.md` instead of deleting them.
- Keep secrets out of commands, URLs, and notes.
- Use the machine hostname from the script as the canonical machine key unless
  this README uses a clearer alias such as `think`, `madlab-i9`, or `urban`.

## Quick Scan Commands

Run these on a target machine before planning heavy local-model or GPU work:

```bash
/home/punpiti/OneDrive/computing-environment/tools/scan_machine_resources.sh
```

Manual equivalent:

```bash
hostname
free -h
lscpu | egrep 'Model name|CPU\(s\)|Core|Thread'
nvidia-smi -L
nvidia-smi
```

For Ollama placement:

```bash
ollama list
ollama run qwen3:8b 'ตอบสั้น ๆ ว่าพร้อม'
ollama ps
```

For GitHub / website project inventory:

```bash
git remote -v
git status --short
rg -n "Production instance|PUBLIC_BASE_URL|https?://|github.com" README.md docs -S
```

## Machines

### `think`

Confirmed on: 2026-06-15 / 2026-06-16

- Environment: WSL2
- OS: Ubuntu 25.10 (Questing Quokka)
- Kernel: Linux 6.6.87.2-microsoft-standard-WSL2
- CPU: Intel Xeon W-1290 @ 3.20GHz
- CPU layout: 16 CPUs, 8 cores / 16 threads, 1 socket, 2 threads per core
- RAM: 94GiB
- Swap: 8GiB
- Root disk: 1007G filesystem, 124G used, 833G available at scan time
- GPU: Quadro P1000
- GPU VRAM: 4096 MiB
- NVIDIA-SMI observed in WSL: 580.95.02
- NVIDIA driver observed in WSL: 581.42
- CUDA version reported by NVIDIA-SMI: 13.0
- Python: `/home/punpiti/.local/share/mamba/envs/rain/bin/python`, Python
  3.13.9
- PyTorch: not available in `rain` at scan time; `torch` not installed
- Ollama result: `qwen3:8b` runs, but slowly; observed placement was about
  `62%/38% CPU/GPU` with runtime size about 6.2GB.
- Best use: local smoke tests, rule-based brief generation, small prototype
  local LLM runs.

### `madlab-i9`

Confirmed on: 2026-06-16 / 2026-06-30

- Environment: WSL2
- OS: Ubuntu 25.10 (Questing Quokka)
- Kernel: Linux 5.15.133.1-microsoft-standard-WSL2
- CPU: 11th Gen Intel Core i9-11900K @ 3.50GHz
- CPU layout: 8 CPUs, 4 cores / 8 threads, 1 socket, 2 threads per core
- RAM: 23GiB
- Swap: 8GiB
- Root disk: 251G filesystem, 95G used, 144G available at scan time
- GPU: Quadro P2000
- GPU VRAM: 5120 MiB
- NVIDIA-SMI observed in WSL: 580.118
- NVIDIA driver observed in WSL: 582.08
- CUDA version reported by NVIDIA-SMI: 13.0
- Python: `/usr/bin/python`, Python 3.13.7
- Nowcast Python: `/home/punpiti/.local/share/mamba/envs/rain/bin/python`,
  Python 3.11.15. In the interactive shell, `conda` is a function that maps to
  `micromamba`, so the normal nowcast activation command is
  `conda activate rain`.
- Nowcast `rain` env packages observed on 2026-06-30: `pandas 3.0.3`,
  `numpy 2.4.6`; `scipy`, `matplotlib`, `xarray`, `duckdb`, `pyarrow`,
  `sklearn`, `cv2`, `geopandas`, `rasterio`, and `netCDF4` were not installed
  in this env at scan time.
- PyTorch: not available at scan time; `torch` not installed
- Ollama: not found in `PATH` at scan time.
- Ollama expectation: `qwen3:8b` should run and may offload more than `think`,
  but will probably still split across CPU/GPU.
- Best use: Urban AI local Ollama test after installing Ollama and verifying
  `qwen3:8b` placement with `ollama ps`.

### `urban`

Confirmed on: 2026-06-15 / 2026-06-16

- Environment: Ubuntu 25.10 VM on Nutanix AHV / KVM
- Kernel: Linux 6.17.0-23-generic
- CPU: Intel Xeon Silver 4214 @ 2.20GHz
- CPU layout: 16 vCPU, 16 sockets, 1 thread per core
- RAM: 30GiB
- Swap: 8GiB
- Root disk: 48G filesystem, 38G used, 8.1G available at scan time
- GPU: no usable NVIDIA GPU recorded
- GPU PCI: `00:02.0 VGA compatible controller: Device 1234:1111`
- NVIDIA: `nvidia-smi` not installed
- CUDA: `nvcc` not found
- Python: `/home/punpiti/miniforge3/bin/python`, Python 3.13.12
- PyTorch CUDA: not available at scan time; `torch` not installed
- Role: production/server-side machine and stable-network host for pulling
  Ollama model archives.
- Best use: deployment/runtime, cache/service jobs, model archive download and
  transfer.
- Not ideal for: local GPU inference.
- Ollama model service path observed:

```text
/usr/share/ollama/.ollama/models
```

- Useful command for portable archive:

```bash
sudo tar -C /usr/share/ollama/.ollama -czf ~/qwen3-8b-ollama-models.tgz models
```

### Indy's Machine

Observed / user-reported machines, not available for current runs unless
explicitly arranged.

- GPU: NVIDIA GeForce RTX 4070 Ti
- GPU: NVIDIA GeForce GTX 1060
- Source note: this is not `madlab-i9`.

## GitHub / Websites / Deployments

### Urban Platform

- Workspace: `/home/punpiti/OneDrive/urban/urban_platform`
- GitHub remote:

```text
git@github.com:punpiti/urban.git
```

- Production website:

```text
https://urban.cpe.ku.ac.th
```

- Runtime/deploy host context: `urban`
- Secret/runtime warning: `.env`, runtime `cache/`, `logs/`, `.venv/`, and
  `docs/private/` must not be pushed to GitHub.
- Related local LLM workspace:

```text
/home/punpiti/OneDrive/urban-ai
```

### Urban AI

- Workspace: `/home/punpiti/OneDrive/urban-ai`
- Purpose: read-only first-pass LLM/RAG layer over Urban cache.
- GitHub remote: not recorded in this workspace at update time.
- Important local artifact:

```text
/home/punpiti/OneDrive/urban-ai/local_ollama_runbook_2026-06-16.md
```

## Project References

- Urban AI local Ollama runbook:
  `/home/punpiti/OneDrive/urban-ai/local_ollama_runbook_2026-06-16.md`
- Nowcast machine notes:
  `/home/punpiti/OneDrive/nowcast/ting67/MACHINE_NOTES.md`
