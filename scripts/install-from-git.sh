#!/usr/bin/env bash
set -euo pipefail

PROJECT_PATH="${1:-.}"
REPO_URL="${2:-}"
REF="${3:-}"
CLONE_DIR="${4:-}"

if [ -z "$REPO_URL" ]; then
  echo "Usage:" >&2
  echo "  bash install-from-git.sh /path/to/project <repo-url> [ref] [clone-dir]" >&2
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
CLONE_DIR="${CLONE_DIR:-$AI_DIR/agent-project-kit}"
REF="${REF:-main}"

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
