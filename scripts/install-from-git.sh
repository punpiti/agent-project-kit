#!/usr/bin/env bash
set -euo pipefail

DRY_RUN="no"
if [ "${1:-}" = "--dry-run" ]; then
  DRY_RUN="yes"
  shift
fi

PROJECT_PATH="${1:-.}"
REPO_URL="${2:-}"
REF="${3:-}"
CLONE_DIR="${4:-}"

if [ -z "$REPO_URL" ]; then
  echo "Usage:" >&2
  echo "  bash install-from-git.sh [--dry-run] /path/to/project <repo-url> [ref] [clone-dir]" >&2
  echo >&2
  echo "Example:" >&2
  echo "  bash install-from-git.sh . https://github.com/punpiti/agent-project-kit.git v6.16.0" >&2
  exit 2
fi

if ! command -v git >/dev/null 2>&1; then
  echo "git not found. Install Git first." >&2
  exit 1
fi

PROJECT_PATH="$(cd "$PROJECT_PATH" && pwd)"
AI_DIR="$PROJECT_PATH/.ai"
REF="${REF:-main}"

is_wsl2() {
  grep -qi microsoft /proc/version 2>/dev/null || grep -qi wsl /proc/version 2>/dev/null
}

default_clone_dir() {
  if is_wsl2 && [[ "$PROJECT_PATH" == /mnt/[a-zA-Z]/* ]]; then
    echo "${XDG_CACHE_HOME:-$HOME/.cache}/agent-project-kit"
  else
    echo "$AI_DIR/agent-project-kit"
  fi
}

CLONE_DIR="${CLONE_DIR:-$(default_clone_dir)}"

mkdir -p "$AI_DIR"

if [ -d "$CLONE_DIR/.git" ]; then
  git -C "$CLONE_DIR" remote set-url origin "$REPO_URL"
  git -C "$CLONE_DIR" fetch --tags --prune origin
else
  rm -rf "$CLONE_DIR"
  git clone "$REPO_URL" "$CLONE_DIR"
  git -C "$CLONE_DIR" fetch --tags --prune origin
fi

if git -C "$CLONE_DIR" rev-parse -q --verify "refs/tags/$REF" >/dev/null; then
  git -C "$CLONE_DIR" checkout -q "tags/$REF"
else
  git -C "$CLONE_DIR" checkout -q "$REF"
  git -C "$CLONE_DIR" pull --ff-only origin "$REF" 2>/dev/null || true
fi

COMMIT="$(git -C "$CLONE_DIR" rev-parse --short=12 HEAD)"

manifest_value() {
  local key="$1"
  if [ -f "$CLONE_DIR/manifest.json" ]; then
    sed -n "s/^[[:space:]]*\"$key\"[[:space:]]*:[[:space:]]*\"\\([^\"]*\\)\".*/\\1/p" "$CLONE_DIR/manifest.json" | head -n 1
  fi
}

version_line() {
  local label="$1"
  local version_file="$AI_DIR/COMPUTING_ENVIRONMENT_VERSION.md"
  if [ -f "$version_file" ]; then
    sed -n "s/^- $label:[[:space:]]*//p" "$version_file" | head -n 1
  fi
}

if [ "$DRY_RUN" = "yes" ]; then
  CURRENT_PACKAGE_VERSION="$(version_line "Package version")"
  CURRENT_STATE_SCHEMA="$(version_line "State schema version")"
  CURRENT_MACHINE_SCHEMA="$(version_line "Machine profile schema version")"
  TARGET_PACKAGE_VERSION="$(manifest_value version)"
  TARGET_STATE_SCHEMA="$(manifest_value state_schema_version)"
  TARGET_MACHINE_SCHEMA="$(manifest_value machine_profile_schema_version)"

  echo "Agent Project Kit update dry run"
  echo "Project: $PROJECT_PATH"
  echo "Repository: $REPO_URL"
  echo "Ref: $REF"
  echo "Commit: $COMMIT"
  echo "Clone path: $CLONE_DIR"
  echo "Snapshot path that would be refreshed: $AI_DIR/computing-environment"
  echo "Current package version: ${CURRENT_PACKAGE_VERSION:-none}"
  echo "Target package version: ${TARGET_PACKAGE_VERSION:-unknown}"
  echo "Current state schema: ${CURRENT_STATE_SCHEMA:-none}"
  echo "Target state schema: ${TARGET_STATE_SCHEMA:-unknown}"
  echo "Current machine profile schema: ${CURRENT_MACHINE_SCHEMA:-none}"
  echo "Target machine profile schema: ${TARGET_MACHINE_SCHEMA:-unknown}"
  echo "Project-local state files would be preserved."
  echo "No project files were updated."
  exit 0
fi

bash "$CLONE_DIR/scripts/install-to-project.sh" "$PROJECT_PATH" "$CLONE_DIR"

VERSION_FILE="$AI_DIR/COMPUTING_ENVIRONMENT_VERSION.md"
if [ -f "$VERSION_FILE" ]; then
  cat >> "$VERSION_FILE" <<EOF2

## Git Source

- Source type: git
- Repository: $REPO_URL
- Ref: $REF
- Commit: $COMMIT
- Clone path: $CLONE_DIR
EOF2
fi

echo "Agent Project Kit cloned at: $CLONE_DIR"
echo "Installed into project: $PROJECT_PATH"
echo "Ref: $REF"
echo "Commit: $COMMIT"
