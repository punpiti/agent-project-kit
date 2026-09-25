# Sourced by the Agent Project Kit shell wrappers: sets APK_PYTHON to a
# Python 3.8+ interpreter or exits with a clear message.
APK_PYTHON="$(command -v python3 || command -v python || true)"
if [ -z "$APK_PYTHON" ] || ! "$APK_PYTHON" -c 'import sys; sys.exit(sys.version_info < (3, 8))' 2>/dev/null; then
  echo "Agent Project Kit needs Python 3.8 or newer (python3 not found)." >&2
  exit 1
fi
