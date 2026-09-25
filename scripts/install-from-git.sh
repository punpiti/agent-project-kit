#!/usr/bin/env bash
# Install Agent Project Kit into a project from a Git ref.
# Thin wrapper: the core is scripts/apk_update.py (Python 3.9+).
#   bash install-from-git.sh [--dry-run] /path/to/project <repo-url> [ref] [clone-dir]
set -euo pipefail
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$script_dir/apk-python.sh"
exec "$APK_PYTHON" -B "$script_dir/apk_update.py" from-git "$@"
