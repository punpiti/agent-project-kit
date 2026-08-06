#!/usr/bin/env bash
set -euo pipefail
SOURCE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ROOT="$(mktemp -d)";trap 'rm -rf "$ROOT"' EXIT
HOME_DIR="$ROOT/shared";PROJECT="$ROOT/project";mkdir -p "$PROJECT/.ai"
bash "$SOURCE/scripts/install-to-project.sh" "$PROJECT" "$SOURCE" >/dev/null
python3 "$SOURCE/scripts/install-shared.py" --source "$SOURCE" --home "$HOME_DIR" --bind-project "$PROJECT" >/dev/null
test -x "$HOME_DIR/bin/apk"
printf '# AGENTS\n' > "$PROJECT/AGENTS.md"
APK_HOME="$HOME_DIR" python3 "$SOURCE/scripts/apk.py" --project "$PROJECT" resolve >/dev/null
APK_HOME="$HOME_DIR" "$HOME_DIR/bin/apk" --project "$PROJECT" resolve >/dev/null
APK_HOME="$HOME_DIR" python3 "$SOURCE/scripts/apk.py" --project "$PROJECT" context "fix the website login bug" --output "$ROOT/context.json"
python3 - "$ROOT/context.json" <<'PY'
import json,sys
d=json.load(open(sys.argv[1]));assert d['routing']['domain']=='software';assert d['metrics']['secondary_modules']<=2
PY
RUNTIME="$HOME_DIR/versions/7.2-shared-runtime-v2-canary"
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
sed -i 's/7.2-shared-runtime-v2-canary/0.0-missing/' "$PROJECT/.ai/apk.json"
if APK_HOME="$HOME_DIR" python3 "$SOURCE/scripts/apk.py" --project "$PROJECT" resolve >/dev/null 2>&1;then echo 'missing version unexpectedly resolved' >&2;exit 1;fi
test -d "$RUNTIME"
echo 'shared runtime canary tests: PASS'
