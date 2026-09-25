#!/usr/bin/env bash
# Update Agent Project Kit from the published GitHub Pages manifest.
# Thin wrapper: the core is scripts/apk_update.py (Python 3.8+).
#   bash update-from-pages.sh [--dry-run] /path/to/project [pages-manifest-url] [repo-url] [ref] [clone-dir]
set -euo pipefail
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$script_dir/apk-python.sh"
exec "$APK_PYTHON" -B "$script_dir/apk_update.py" from-pages "$@"
