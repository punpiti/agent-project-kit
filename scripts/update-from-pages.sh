#!/usr/bin/env bash
set -euo pipefail

DRY_RUN="no"
if [ "${1:-}" = "--dry-run" ]; then
  DRY_RUN="yes"
  shift
fi

PROJECT_PATH="${1:-.}"
PAGES_MANIFEST_URL="${2:-https://punpiti.github.io/agent-project-kit/manifest.json}"
REPO_URL="${3:-https://github.com/punpiti/agent-project-kit.git}"
REF="${4:-main}"
CLONE_DIR="${5:-}"

PROJECT_PATH="$(cd "$PROJECT_PATH" && pwd)"
AI_DIR="$PROJECT_PATH/.ai"
VERSION_FILE="$AI_DIR/COMPUTING_ENVIRONMENT_VERSION.md"

usage() {
  echo "Usage:" >&2
  echo "  bash update-from-pages.sh [--dry-run] /path/to/project [pages-manifest-url] [repo-url] [ref] [clone-dir]" >&2
  echo >&2
  echo "Example:" >&2
  echo "  bash update-from-pages.sh --dry-run . https://punpiti.github.io/agent-project-kit/manifest.json" >&2
}

if ! command -v curl >/dev/null 2>&1; then
  echo "curl not found. Install curl first." >&2
  exit 1
fi

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
installer="$script_dir/install-from-git.sh"
if [ ! -f "$installer" ]; then
  echo "install-from-git.sh not found next to update-from-pages.sh." >&2
  exit 1
fi

read_version_line() {
  local label="$1"
  if [ -f "$VERSION_FILE" ]; then
    sed -n "s/^- $label:[[:space:]]*//p" "$VERSION_FILE" | head -n 1
  fi
}

json_value() {
  local key="$1"
  sed -n "s/^[[:space:]]*\"$key\"[[:space:]]*:[[:space:]]*\"\\([^\"]*\\)\".*/\\1/p" | head -n 1
}

version_key() {
  local raw="$1"
  local main
  main="$(printf '%s' "$raw" | sed 's/^[vV]//' | sed 's/[^0-9.].*$//')"
  awk -F. '{
    major=($1=="" ? 0 : $1);
    minor=($2=="" ? 0 : $2);
    patch=($3=="" ? 0 : $3);
    printf "%06d%06d%06d\n", major, minor, patch;
  }' <<EOF2
$main
EOF2
}

is_newer_or_different() {
  local current="$1"
  local latest="$2"
  local current_updated="$3"
  local latest_updated="$4"

  [ -z "$latest" ] && return 1
  [ "$current" = "$latest" ] && return 1

  local current_key latest_key
  current_key="$(version_key "$current")"
  latest_key="$(version_key "$latest")"
  if [ "$latest_key" -gt "$current_key" ]; then
    return 0
  fi

  if [ "$latest_key" -eq "$current_key" ] && [ -n "$latest_updated" ] && [ -n "$current_updated" ] && [ "$latest_updated" \> "$current_updated" ]; then
    return 0
  fi

  # Keep non-semver package labels useful: a changed manifest version means a
  # package update is available even when the numeric prefix is unchanged.
  [ "$current" != "$latest" ]
}

mkdir -p "$AI_DIR"

manifest="$(curl -fsSL "$PAGES_MANIFEST_URL")" || {
  echo "Could not read GitHub Pages manifest: $PAGES_MANIFEST_URL" >&2
  usage
  exit 1
}

latest_version="$(printf '%s\n' "$manifest" | json_value version)"
latest_updated="$(printf '%s\n' "$manifest" | json_value updated)"
latest_state_schema="$(printf '%s\n' "$manifest" | json_value state_schema_version)"
latest_machine_schema="$(printf '%s\n' "$manifest" | json_value machine_profile_schema_version)"
current_version="$(read_version_line "Package version")"
current_updated="$(read_version_line "Package updated")"
current_state_schema="$(read_version_line "State schema version")"
current_machine_schema="$(read_version_line "Machine profile schema version")"

current_version="${current_version:-none}"
latest_version="${latest_version:-unknown}"

echo "Agent Project Kit GitHub Pages update check"
echo "Project: $PROJECT_PATH"
echo "Manifest: $PAGES_MANIFEST_URL"
echo "Repository: $REPO_URL"
echo "Ref: $REF"
echo "Current package version: $current_version"
echo "Latest package version: $latest_version"
echo "Current package updated: ${current_updated:-unknown}"
echo "Latest package updated: ${latest_updated:-unknown}"
echo "Current state schema: ${current_state_schema:-none}"
echo "Latest state schema: ${latest_state_schema:-unknown}"
echo "Current machine profile schema: ${current_machine_schema:-none}"
echo "Latest machine profile schema: ${latest_machine_schema:-unknown}"

if ! is_newer_or_different "$current_version" "$latest_version" "$current_updated" "$latest_updated"; then
  echo "Result: no newer package version found."
  if [ "$DRY_RUN" != "yes" ] && [ -f "$VERSION_FILE" ]; then
    tmp_file="$(mktemp)"
    sed \
      -e "s|^- Last update check:.*|- Last update check: $(date -Iseconds)|" \
      -e "s|^- Latest known upstream version:.*|- Latest known upstream version: $latest_version|" \
      -e "s|^- Update check source:.*|- Update check source: $PAGES_MANIFEST_URL|" \
      "$VERSION_FILE" > "$tmp_file"
    mv "$tmp_file" "$VERSION_FILE"
  fi
  exit 0
fi

echo "Result: newer or different package version found."
echo "Project-local state files will be preserved by install-from-git."

if [ "$DRY_RUN" = "yes" ]; then
  if [ -n "$CLONE_DIR" ]; then
    bash "$installer" --dry-run "$PROJECT_PATH" "$REPO_URL" "$REF" "$CLONE_DIR"
  else
    bash "$installer" --dry-run "$PROJECT_PATH" "$REPO_URL" "$REF"
  fi
  exit 0
fi

if [ -n "$CLONE_DIR" ]; then
  bash "$installer" "$PROJECT_PATH" "$REPO_URL" "$REF" "$CLONE_DIR"
else
  bash "$installer" "$PROJECT_PATH" "$REPO_URL" "$REF"
fi

if [ -f "$VERSION_FILE" ]; then
  tmp_file="$(mktemp)"
  sed \
    -e "s|^- Last update check:.*|- Last update check: $(date -Iseconds)|" \
    -e "s|^- Latest known upstream version:.*|- Latest known upstream version: $latest_version|" \
    -e "s|^- Update check source:.*|- Update check source: $PAGES_MANIFEST_URL|" \
    "$VERSION_FILE" > "$tmp_file"
  mv "$tmp_file" "$VERSION_FILE"
fi
