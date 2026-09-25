#!/usr/bin/env bash
set -euo pipefail
SOURCE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["version"])' "$SOURCE/manifest.json")"
unset APK_HOME APK_SHARED_ROOT APK_MACHINE_HOME
ROOT="$(mktemp -d)";trap 'rm -rf "$ROOT"' EXIT
HOME_DIR="$ROOT/shared";PROJECT="$ROOT/project";mkdir -p "$PROJECT/.ai"
bash "$SOURCE/scripts/install-to-project.sh" "$PROJECT" "$SOURCE" >/dev/null
python3 "$SOURCE/scripts/install-shared.py" --source "$SOURCE" --home "$HOME_DIR" --bind-project "$PROJECT" >/dev/null
test -x "$HOME_DIR/bin/apk"
test -z "$(find "$HOME_DIR/versions/$VERSION" -type d -name __pycache__ -print -quit)"
test -z "$(find "$HOME_DIR/versions/$VERSION" -type f \( -name '*.pyc' -o -name '*.pyo' \) -print -quit)"

# An immutable version cannot be rebound from different source content.
ALTERED_SOURCE="$ROOT/altered-source"
mkdir -p "$ALTERED_SOURCE"
tar -C "$SOURCE" --exclude=.git --exclude=.ai -cf - . | tar -C "$ALTERED_SOURCE" -xf -
printf '\n# same-version source drift\n' >> "$ALTERED_SOURCE/STARTUP.md"
if python3 "$SOURCE/scripts/install-shared.py" --source "$ALTERED_SOURCE" --home "$HOME_DIR" --bind-project "$PROJECT" >/dev/null 2>&1; then
  echo 'same-version source drift unexpectedly reused the installed runtime' >&2
  exit 1
fi
printf '# AGENTS\n' > "$PROJECT/AGENTS.md"
APK_HOME="$HOME_DIR" python3 "$SOURCE/scripts/apk.py" --project "$PROJECT" resolve >/dev/null
APK_HOME="$HOME_DIR" "$HOME_DIR/bin/apk" --project "$PROJECT" resolve >/dev/null
APK_HOME="$HOME_DIR" python3 "$SOURCE/scripts/apk.py" --project "$PROJECT" context "fix the website login bug" --output "$ROOT/context.json"
python3 - "$ROOT/context.json" <<'PY'
import json,sys
d=json.load(open(sys.argv[1]));assert d['routing']['domain']=='software';assert d['metrics']['method_modules']<=2;assert d['metrics']['lifecycle_stages']<=2
PY
RUNTIME="$HOME_DIR/versions/$VERSION"
printf '\n# tampered\n' >> "$RUNTIME/scripts/context.py"
if APK_HOME="$HOME_DIR" python3 "$SOURCE/scripts/apk.py" --project "$PROJECT" resolve >/dev/null 2>&1;then echo 'tampered runtime unexpectedly resolved' >&2;exit 1;fi
python3 "$SOURCE/scripts/install-shared.py" --source "$SOURCE" --home "$HOME_DIR" --force --bind-project "$PROJECT" >/dev/null
rm "$PROJECT/.ai/apk.json"
python3 "$PROJECT/.ai/agent-project-kit/scripts/context.py" --project "$PROJECT" "fix the website login bug" --output "$ROOT/fallback.json"
python3 - "$ROOT/fallback.json" <<'PY'
import json,sys
assert json.load(open(sys.argv[1]))['routing']['domain']=='software'
PY
python3 "$SOURCE/scripts/install-shared.py" --source "$SOURCE" --home "$HOME_DIR" --bind-project "$PROJECT" >/dev/null
python3 - "$PROJECT/.ai/apk.json" <<'PY'
import json,sys
path=sys.argv[1]
data=json.load(open(path,encoding="utf-8"))
data["version"]="../outside-runtime"
open(path,"w",encoding="utf-8").write(json.dumps(data,indent=2)+"\n")
PY
if APK_HOME="$HOME_DIR" python3 "$SOURCE/scripts/apk.py" --project "$PROJECT" resolve >/dev/null 2>&1;then echo 'path-traversal version unexpectedly resolved' >&2;exit 1;fi
python3 "$SOURCE/scripts/install-shared.py" --source "$SOURCE" --home "$HOME_DIR" --bind-project "$PROJECT" >/dev/null
python3 - "$PROJECT/.ai/apk.json" <<'PY'
import json,sys
path=sys.argv[1]
data=json.load(open(path,encoding="utf-8"))
data["version"]="0.0-missing"
open(path,"w",encoding="utf-8").write(json.dumps(data,indent=2)+"\n")
PY
if APK_HOME="$HOME_DIR" python3 "$SOURCE/scripts/apk.py" --project "$PROJECT" resolve >/dev/null 2>&1;then echo 'missing version unexpectedly resolved' >&2;exit 1;fi
test -d "$RUNTIME"
echo 'shared runtime canary tests: PASS'
