# Sourced by the Agent Project Kit shell wrappers: sets APK_PYTHON to a
# Python 3.9+ interpreter or exits with a clear message.
APK_PYTHON="$(command -v python3 || command -v python || true)"
if [ -z "$APK_PYTHON" ]; then
  echo "Agent Project Kit needs Python 3.9 or newer (python3 not found)." >&2
  exit 1
fi
if ! "$APK_PYTHON" -c 'import sys; sys.exit(sys.version_info < (3, 9))' 2>/dev/null; then
  echo "Agent Project Kit needs Python 3.9 or newer; $APK_PYTHON is $("$APK_PYTHON" -c 'import platform; print(platform.python_version())' 2>/dev/null || echo unknown)." >&2
  exit 1
fi
