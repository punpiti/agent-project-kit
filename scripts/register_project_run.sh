#!/usr/bin/env bash
set -euo pipefail

LOG_FILE="${PROJECT_RUNS_LOG:-$(pwd)/.ai/PROJECT_RUNS.md}"

PROJECT=""
STATUS="running"
RUN_PATH="$(pwd)"
COMMAND=""
PORT=""
URL=""
NOTES=""
MACHINE="$(hostname 2>/dev/null || echo unknown)"
DRY_RUN=0

usage() {
  cat <<'EOF'
Usage:
  register_project_run.sh --project NAME [options]

Options:
  --project NAME     Project name. Required.
  --status STATUS    running, testing, production, stopped, superseded, archived.
                    Default: running.
  --machine NAME     Override detected hostname.
  --path PATH        Override detected current directory.
  --command COMMAND  Command used to run the project. Do not include secrets.
  --port PORT        Local or public port.
  --url URL          Local or public URL.
  --notes NOTES      Short context note. Do not include secrets.
  --dry-run          Print the row without editing the project run log.
  -h, --help         Show this help.

Example:
  /path/to/agent-project-kit/scripts/register_project_run.sh \
    --project "Urban AI" \
    --command "ollama run qwen3:8b" \
    --port "11434" \
    --url "http://localhost:11434" \
    --notes "local smoke test"
EOF
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --project)
      PROJECT="${2:-}"
      shift 2
      ;;
    --status)
      STATUS="${2:-}"
      shift 2
      ;;
    --machine)
      MACHINE="${2:-}"
      shift 2
      ;;
    --path)
      RUN_PATH="${2:-}"
      shift 2
      ;;
    --command)
      COMMAND="${2:-}"
      shift 2
      ;;
    --port)
      PORT="${2:-}"
      shift 2
      ;;
    --url)
      URL="${2:-}"
      shift 2
      ;;
    --notes)
      NOTES="${2:-}"
      shift 2
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [ -z "$PROJECT" ]; then
  echo "--project is required" >&2
  usage >&2
  exit 2
fi

if [ ! -f "$LOG_FILE" ]; then
  mkdir -p "$(dirname "$LOG_FILE")"
  cat > "$LOG_FILE" <<'EOF'
# Project Runs

Project-local run/service/machine-role log.

## Runs

| Timestamp | Machine | Project | Status | Path | Command | Port | URL | Git Remote | Notes |
|---|---|---|---|---|---|---|---|---|---|
EOF
fi

escape_cell() {
  local value="${1:-}"
  value="${value//$'\n'/ }"
  value="${value//|/\\|}"
  printf '%s' "$value"
}

git_remote=""
if git -C "$RUN_PATH" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  git_remote="$(git -C "$RUN_PATH" remote get-url origin 2>/dev/null || true)"
fi

timestamp="$(date -Iseconds)"
row="| $(escape_cell "$timestamp") | $(escape_cell "$MACHINE") | $(escape_cell "$PROJECT") | $(escape_cell "$STATUS") | $(escape_cell "$RUN_PATH") | $(escape_cell "$COMMAND") | $(escape_cell "$PORT") | $(escape_cell "$URL") | $(escape_cell "$git_remote") | $(escape_cell "$NOTES") |"

if [ "$DRY_RUN" -eq 1 ]; then
  echo "Dry run; project run log was not modified:"
  echo "$row"
  exit 0
fi

tmp_file="$(mktemp)"
inserted=0
while IFS= read -r line; do
  printf '%s\n' "$line" >> "$tmp_file"
  if [ "$inserted" -eq 0 ] && [ "$line" = "|---|---|---|---|---|---|---|---|---|---|" ]; then
    printf '%s\n' "$row" >> "$tmp_file"
    inserted=1
  fi
done < "$LOG_FILE"

if [ "$inserted" -eq 0 ]; then
  rm -f "$tmp_file"
  echo "Could not find the runs table in $LOG_FILE" >&2
  exit 1
fi

mv "$tmp_file" "$LOG_FILE"
echo "Registered project run:"
echo "$row"
