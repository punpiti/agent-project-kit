#!/usr/bin/env bash
# Install or update Agent Project Kit in a project.
# Thin wrapper: the installer core is scripts/apk_install.py (Python 3.8+).
#   bash install-to-project.sh /path/to/project /path/to/agent-project-kit
set -euo pipefail
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python_bin="$(command -v python3 || command -v python || true)"
if [ -z "$python_bin" ] || ! "$python_bin" -c 'import sys; sys.exit(sys.version_info < (3, 8))' 2>/dev/null; then
  echo "Agent Project Kit needs Python 3.8 or newer (python3 not found)." >&2
  exit 1
fi
exec "$python_bin" -B "$script_dir/apk_install.py" "$@" --installer-name install-to-project.sh
