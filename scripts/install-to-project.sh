#!/usr/bin/env bash
# Install or update Agent Project Kit in a project.
# Thin wrapper: the installer core is scripts/apk_install.py (Python 3.8+).
#   bash install-to-project.sh /path/to/project /path/to/agent-project-kit
set -euo pipefail
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$script_dir/apk-python.sh"
exec "$APK_PYTHON" -B "$script_dir/apk_install.py" "$@" --installer-name install-to-project.sh
