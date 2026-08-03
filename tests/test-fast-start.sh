#!/usr/bin/env bash
set -euo pipefail
SOURCE_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEST_ROOT="$(mktemp -d)"; trap 'rm -rf "$TEST_ROOT"' EXIT
PROJECT="$TEST_ROOT/project"; mkdir -p "$PROJECT"
printf '# User rules\n\nkeep-me\n' > "$PROJECT/AGENTS.md"
bash "$SOURCE_PATH/scripts/install-to-project.sh" "$PROJECT" "$SOURCE_PATH" >/dev/null
grep -q 'keep-me' "$PROJECT/AGENTS.md"
test "$(grep -c '<!-- BEGIN COMPUTING-ENVIRONMENT -->' "$PROJECT/AGENTS.md")" -eq 1
grep -q 'Classify the task' "$PROJECT/AGENTS.md"
test -f "$PROJECT/.ai/agent-project-kit/STARTUP.md"
grep -q "Read Every Session" "$PROJECT/.ai/agent-project-kit/STARTUP.md"
for route in WEB_DEVELOPMENT CONTENT_ANALYSIS DATA_ANALYTICS COURSE_MATERIAL_DEVELOPMENT; do
  test -f "$PROJECT/.ai/agent-project-kit/prompts/$(printf '%s' "$route" | sed -e 's/^WEB_DEVELOPMENT$/14_WEB_DEVELOPMENT/' -e 's/^CONTENT_ANALYSIS$/15_CONTENT_ANALYSIS/' -e 's/^DATA_ANALYTICS$/16_DATA_ANALYTICS/' -e 's/^COURSE_MATERIAL_DEVELOPMENT$/17_COURSE_MATERIAL_DEVELOPMENT/').md"
done
test -f "$PROJECT/.ai/agent-project-kit/prompts/18_EDUCATIONAL_POLICY_DEVELOPMENT.md"
grep -q 'Educational Policy Development' "$PROJECT/.ai/agent-project-kit/STARTUP.md"
test -f "$PROJECT/.ai/agent-project-kit/prompts/19_SOFTWARE_DEVELOPMENT_AUTOMATION.md"
test -f "$PROJECT/.ai/agent-project-kit/prompts/20_ADMINISTRATIVE_PROFESSIONAL_OPERATIONS.md"
test -f "$PROJECT/.ai/agent-project-kit/prompts/21_STRATEGY_ADVISORY.md"
grep -q 'Software Development & Automation' "$PROJECT/.ai/agent-project-kit/STARTUP.md"
grep -q 'Administrative & Professional Operations' "$PROJECT/.ai/agent-project-kit/STARTUP.md"
python3 "$SOURCE_PATH/scripts/validate_prompt_catalog.py" >/dev/null
test -f "$PROJECT/.ai/agent-project-kit/prompts/catalog.json"
test -f "$PROJECT/.ai/project.json"
test -f "$PROJECT/.ai/state.json"
test -f "$PROJECT/.ai/local-resources.json"
test -f "$PROJECT/.ai/agent-project-kit/config/routes.json"
python3 "$SOURCE_PATH/tests/test-v7-context.py" >/dev/null
test "$(grep -c -- 'Package display name:' "$PROJECT/.ai/COMPUTING_ENVIRONMENT_VERSION.md")" -eq 1
python3 "$SOURCE_PATH/scripts/run-once.py" --project "$PROJECT" --key fixture -- sh -c 'printf x >> counter' >/dev/null
python3 "$SOURCE_PATH/scripts/run-once.py" --project "$PROJECT" --key fixture -- sh -c 'printf x >> counter' >/dev/null
test "$(wc -c < "$PROJECT/counter")" -eq 1
if python3 "$SOURCE_PATH/scripts/run-once.py" --project "$PROJECT" --key failing -- false >/dev/null; then exit 1; fi
! grep -q 'project:failing' "$PROJECT/.ai/AGENT_PROJECT_KIT_STATE.json"
if python3 "$SOURCE_PATH/scripts/apk_doctor.py" "$PROJECT" --quick >/dev/null; then
  echo "doctor should flag a placeholder PROJECT_STATE" >&2; exit 1
fi
sed -i -e 's/^- Project name:$/- Project name: Fixture/' \
  -e 's/^สรุปเป้าหมายปัจจุบัน 3–7 บรรทัด$/Validate fast startup./' \
  -e "s/^- Last updated:$/- Last updated: $(date +%F)/" "$PROJECT/.ai/PROJECT_STATE.md"
python3 "$SOURCE_PATH/scripts/apk_doctor.py" "$PROJECT" --quick >/dev/null
count="$(grep -c 'Agent Project Kit installation first recorded' "$PROJECT/.ai/SESSION_LOG.md" || true)"
bash "$SOURCE_PATH/scripts/install-to-project.sh" "$PROJECT" "$SOURCE_PATH" >/dev/null
test "$(grep -c 'Agent Project Kit installation first recorded' "$PROJECT/.ai/SESSION_LOG.md" || true)" -eq "$count"
grep -q 'keep-me' "$PROJECT/AGENTS.md"
test "$(grep -c '<!-- BEGIN COMPUTING-ENVIRONMENT -->' "$PROJECT/AGENTS.md")" -eq 1
echo "fast-start acceptance tests: PASS"
