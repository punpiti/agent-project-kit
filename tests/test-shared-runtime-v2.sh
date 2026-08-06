#!/usr/bin/env bash
set -euo pipefail

SOURCE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEST_ROOT="$(mktemp -d)"
trap 'chmod -R u+w "$TEST_ROOT" 2>/dev/null || true; rm -rf "$TEST_ROOT"' EXIT

SHARED_ROOT="$TEST_ROOT/synced generic package"
MACHINE_ONE="$TEST_ROOT/machine-one"
MACHINE_TWO="$TEST_ROOT/machine-two"
PROJECT="$TEST_ROOT/self host project"
mkdir -p "$PROJECT/.ai/prompts"

python3 - "$SOURCE" <<'PY'
import importlib.util,sys
from pathlib import Path
source=Path(sys.argv[1])
for script in ("scripts/install-shared.py","scripts/apk.py"):
    spec=importlib.util.spec_from_file_location("apk_digest",source/script)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    assert module.aggregate_digest({"z":"2","A":"1"}) == module.aggregate_digest({"A":"1","z":"2"})
PY

printf '# canonical source marker\n' > "$PROJECT/START_HERE.md"
printf '# project-only state APK_PROJECT_SECRET_6f62d5\n' > "$PROJECT/.ai/PROJECT_STATE.md"
printf '# project-only prompt APK_PROJECT_PROMPT_90c2af\n' > "$PROJECT/.ai/prompts/local.md"
printf '# keep existing shell setup\nexport KEEP_ME=yes\n' > "$TEST_ROOT/bashrc"

python3 "$SOURCE/scripts/install-shared.py" \
  --source "$SOURCE" --shared-root "$SHARED_ROOT" \
  --machine-home "$MACHINE_ONE" --bind-project "$PROJECT" \
  --configure-shell --shell-rc "$TEST_ROOT/bashrc" >/dev/null
python3 "$SOURCE/scripts/install-shared.py" \
  --source "$SOURCE" --shared-root "$SHARED_ROOT" \
  --machine-home "$MACHINE_ONE" \
  --configure-shell --shell-rc "$TEST_ROOT/bashrc" >/dev/null
# Normal upgrades can omit the shared root; the installer reads machine config.
env -u APK_SHARED_ROOT -u APK_HOME APK_MACHINE_HOME="$MACHINE_ONE" \
  python3 "$SOURCE/scripts/install-shared.py" --source "$SOURCE" >/dev/null
test -d "$SHARED_ROOT/versions/7.2.3-shared-runtime-v2-canary"
test "$(grep -c '^# BEGIN AGENT PROJECT KIT SHARED RUNTIME$' "$TEST_ROOT/bashrc")" -eq 1
test "$(grep -c '^# END AGENT PROJECT KIT SHARED RUNTIME$' "$TEST_ROOT/bashrc")" -eq 1
grep -q '^export KEEP_ME=yes$' "$TEST_ROOT/bashrc"
env -i PATH=/usr/bin:/bin bash -c ". '$TEST_ROOT/bashrc'; test \"\$APK_SHARED_ROOT\" = '$SHARED_ROOT'; test \"\$APK_MACHINE_HOME\" = '$MACHINE_ONE'; case :\$PATH: in *:'$MACHINE_ONE/bin':*) ;; *) exit 1;; esac"

python3 - "$PROJECT/.ai/apk.json" <<'PY'
import json,sys
data=json.load(open(sys.argv[1],encoding="utf-8"))
assert data["schema_version"] == 2
assert data["runtime_mode"] == "shared-with-snapshot-fallback"
assert "shared_root" not in data
PY

if rg -l 'APK_PROJECT_SECRET_6f62d5|APK_PROJECT_PROMPT_90c2af|self host project' "$SHARED_ROOT" >/dev/null; then
  echo 'project content leaked into shared runtime' >&2
  exit 1
fi

APK_MACHINE_HOME="$MACHINE_ONE" "$MACHINE_ONE/bin/apk" \
  --project "$PROJECT" resolve >/dev/null

python3 "$SOURCE/scripts/install-shared.py" \
  --source "$SOURCE" --shared-root "$SHARED_ROOT" \
  --machine-home "$MACHINE_TWO" >/dev/null
APK_MACHINE_HOME="$MACHINE_TWO" "$MACHINE_TWO/bin/apk" \
  --project "$PROJECT" resolve >/dev/null

# An explicit shared root must work without changing the project binding.
APK_SHARED_ROOT="$SHARED_ROOT" APK_MACHINE_HOME="$TEST_ROOT/unconfigured-machine" \
  python3 "$SOURCE/scripts/apk.py" --project "$PROJECT" resolve >/dev/null

# Schema v1 remains readable during the migration window.
sed -i 's/"schema_version": 2/"schema_version": 1/' "$PROJECT/.ai/apk.json"
APK_MACHINE_HOME="$MACHINE_ONE" python3 "$SOURCE/scripts/apk.py" \
  --project "$PROJECT" resolve >/dev/null
sed -i 's/"schema_version": 1/"schema_version": 2/' "$PROJECT/.ai/apk.json"

# Normal resolution is read-only against an immutable installed version.
RUNTIME="$SHARED_ROOT/versions/7.2.3-shared-runtime-v2-canary"
chmod -R a-w "$RUNTIME"
APK_MACHINE_HOME="$MACHINE_ONE" python3 "$SOURCE/scripts/apk.py" \
  --project "$PROJECT" resolve >/dev/null

# Guarded rollback disables only the binding and leaves canonical source intact.
APK_MACHINE_HOME="$MACHINE_ONE" python3 "$SOURCE/scripts/apk.py" \
  --project "$PROJECT" rollback >/dev/null
test ! -e "$PROJECT/.ai/apk.json"
test -e "$PROJECT/.ai/apk.json.disabled"
grep -q 'canonical source marker' "$PROJECT/START_HERE.md"
test -d "$RUNTIME"
if APK_MACHINE_HOME="$MACHINE_ONE" python3 "$SOURCE/scripts/apk.py" \
  --project "$PROJECT" rollback >/dev/null 2>&1; then
  echo 'second rollback unexpectedly succeeded' >&2
  exit 1
fi

echo 'shared runtime v2 preparation tests: PASS'
