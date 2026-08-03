#!/usr/bin/env bash
set -euo pipefail
SOURCE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ROOT="$(mktemp -d)";trap 'rm -rf "$ROOT"' EXIT
HOME_DIR="$ROOT/shared";PROJECT="$ROOT/project";mkdir -p "$PROJECT/.ai"
python3 "$SOURCE/scripts/install-shared.py" --source "$SOURCE" --home "$HOME_DIR" >/dev/null
test -x "$HOME_DIR/bin/apk"
cp "$SOURCE/templates/apk.json" "$PROJECT/.ai/apk.json"
cp "$SOURCE/templates/PROJECT_STATE.md" "$PROJECT/.ai/PROJECT_STATE.md"
printf '# AGENTS\n' > "$PROJECT/AGENTS.md"
APK_HOME="$HOME_DIR" python3 "$SOURCE/scripts/apk.py" --project "$PROJECT" resolve >/dev/null
APK_HOME="$HOME_DIR" "$HOME_DIR/bin/apk" --project "$PROJECT" resolve >/dev/null
APK_HOME="$HOME_DIR" python3 "$SOURCE/scripts/apk.py" --project "$PROJECT" context "fix the website login bug" --output "$ROOT/context.json"
python3 - "$ROOT/context.json" <<'PY'
import json,sys
d=json.load(open(sys.argv[1]));assert d['routing']['domain']=='software';assert d['metrics']['secondary_modules']<=2
PY
sed -i 's/7.1-shared-runtime-canary/0.0-missing/' "$PROJECT/.ai/apk.json"
if APK_HOME="$HOME_DIR" python3 "$SOURCE/scripts/apk.py" --project "$PROJECT" resolve >/dev/null 2>&1;then echo 'missing version unexpectedly resolved' >&2;exit 1;fi
test -d "$HOME_DIR/versions/7.1-shared-runtime-canary"
echo 'shared runtime canary tests: PASS'
