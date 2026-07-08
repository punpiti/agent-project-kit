#!/usr/bin/env bash
set -u

echo "=== SYSTEM ==="
if [ -r /etc/os-release ]; then
  grep -E 'PRETTY_NAME|VERSION=' /etc/os-release
else
  echo "/etc/os-release not found"
fi
uname -a
echo

echo "=== CPU ==="
lscpu | grep -E 'Model name|Socket|Core|Thread|CPU\(s\)' || true
echo

echo "=== MEMORY ==="
free -h
echo

echo "=== DISK ==="
df -h /
echo

echo "=== GPU ==="
if command -v nvidia-smi >/dev/null 2>&1; then
  nvidia-smi
else
  echo "nvidia-smi not found"
fi
echo

echo "=== PYTHON ==="
PYTHON_BIN=""
if command -v python >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python)"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python3)"
fi

if [ -n "$PYTHON_BIN" ]; then
  echo "$PYTHON_BIN"
  "$PYTHON_BIN" --version
else
  echo "python/python3 not found"
fi
echo

echo "=== PYTORCH ==="
if [ -n "$PYTHON_BIN" ]; then
  "$PYTHON_BIN" - <<'PY'
try:
    import torch
    print("torch:", torch.__version__)
    print("cuda available:", torch.cuda.is_available())
    print("torch cuda:", torch.version.cuda)
    print("gpu count:", torch.cuda.device_count())
    if torch.cuda.is_available():
        print("gpu:", torch.cuda.get_device_name(0))
except Exception as e:
    print("torch check failed:", e)
PY
else
  echo "torch check skipped: python/python3 not found"
fi
