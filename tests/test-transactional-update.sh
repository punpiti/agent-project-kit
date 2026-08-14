#!/usr/bin/env bash
set -euo pipefail

SOURCE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEST_ROOT="$(mktemp -d)"
trap 'rm -rf "$TEST_ROOT"' EXIT
PROJECT="$TEST_ROOT/project"
mkdir -p "$PROJECT"
printf '# User rules\n\nkeep-me\n' > "$PROJECT/AGENTS.md"

copy_package_source() {
  local destination="$1"
  mkdir -p "$destination"
  tar -C "$SOURCE" --exclude=.git --exclude=.ai -cf - . | tar -C "$destination" -xf -
}

bash "$SOURCE/scripts/install-to-project.sh" "$PROJECT" "$SOURCE" >/dev/null
printf 'project-state-sentinel\n' > "$PROJECT/.ai/PROJECT_STATE.md"
original_version="$(sed -n 's/^- Package version:[[:space:]]*//p' "$PROJECT/.ai/COMPUTING_ENVIRONMENT_VERSION.md")"

# A missing required source item must fail before the active snapshot changes.
BAD_SOURCE="$TEST_ROOT/bad-source"
copy_package_source "$BAD_SOURCE"
rm "$BAD_SOURCE/PACKAGE_CONTENTS.md"
if bash "$SOURCE/scripts/install-to-project.sh" "$PROJECT" "$BAD_SOURCE" >/dev/null 2>&1; then
  echo 'incomplete source unexpectedly installed' >&2
  exit 1
fi
test "$(sed -n 's/^[[:space:]]*"version"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' "$PROJECT/.ai/agent-project-kit/manifest.json")" = "$original_version"
grep -q 'project-state-sentinel' "$PROJECT/.ai/PROJECT_STATE.md"
test -z "$(find "$PROJECT/.ai" -maxdepth 1 -name '.agent-project-kit.stage.*' -print -quit)"

# A valid update swaps once and retains exactly one usable previous snapshot.
GOOD_SOURCE="$TEST_ROOT/good-source"
copy_package_source "$GOOD_SOURCE"
sed -i 's/"version": "[^"]*"/"version": "99.1.0-transaction-test"/' "$GOOD_SOURCE/manifest.json"
printf '\ntransaction-test-marker\n' >> "$GOOD_SOURCE/STARTUP.md"
bash "$SOURCE/scripts/install-to-project.sh" "$PROJECT" "$GOOD_SOURCE" >/dev/null
grep -q 'transaction-test-marker' "$PROJECT/.ai/agent-project-kit/STARTUP.md"
test -f "$PROJECT/.ai/agent-project-kit.previous/STARTUP.md"
! grep -q 'transaction-test-marker' "$PROJECT/.ai/agent-project-kit.previous/STARTUP.md"
grep -q 'project-state-sentinel' "$PROJECT/.ai/PROJECT_STATE.md"

# Force a failure after the snapshot swap. The active snapshot, metadata,
# user control file, and previous snapshot must all be restored.
FAIL_SOURCE="$TEST_ROOT/fail-source"
mkdir -p "$FAIL_SOURCE"
tar -C "$GOOD_SOURCE" -cf - . | tar -C "$FAIL_SOURCE" -xf -
sed -i 's/99.1.0-transaction-test/99.2.0-rollback-test/' "$FAIL_SOURCE/manifest.json"
printf '\nrollback-test-marker\n' >> "$FAIL_SOURCE/STARTUP.md"
rm "$PROJECT/AGENTS.md"
mkdir "$PROJECT/AGENTS.md"
if bash "$SOURCE/scripts/install-to-project.sh" "$PROJECT" "$FAIL_SOURCE" >/dev/null 2>&1; then
  echo 'post-swap failure unexpectedly succeeded' >&2
  exit 1
fi
grep -q 'transaction-test-marker' "$PROJECT/.ai/agent-project-kit/STARTUP.md"
! grep -q 'rollback-test-marker' "$PROJECT/.ai/agent-project-kit/STARTUP.md"
test -d "$PROJECT/AGENTS.md"
test "$(sed -n 's/^- Package version:[[:space:]]*//p' "$PROJECT/.ai/COMPUTING_ENVIRONMENT_VERSION.md")" = '99.1.0-transaction-test'
grep -q 'project-state-sentinel' "$PROJECT/.ai/PROJECT_STATE.md"
test -z "$(find "$PROJECT/.ai" -maxdepth 1 \( -name '.agent-project-kit.stage.*' -o -name '.agent-project-kit.control-backup.*' -o -name 'agent-project-kit.previous.old' \) -print -quit)"

# The Pages updater follows the manifest's exact git_ref, even when main has
# advanced, and rejects a checked-out package whose version disagrees.
rm -rf "$PROJECT/AGENTS.md"
printf '# User rules\n' > "$PROJECT/AGENTS.md"
GIT_SOURCE="$TEST_ROOT/git-source"
copy_package_source "$GIT_SOURCE"
git -C "$GIT_SOURCE" init -q
git -C "$GIT_SOURCE" config user.email test@example.invalid
git -C "$GIT_SOURCE" config user.name 'APK test'
sed -i 's/"version": "[^"]*"/"version": "100.1.0-pinned-test"/' "$GIT_SOURCE/manifest.json"
sed -i 's/"git_ref": "[^"]*"/"git_ref": "v100.1.0-pinned-test"/' "$GIT_SOURCE/manifest.json"
git -C "$GIT_SOURCE" add .
git -C "$GIT_SOURCE" commit -qm pinned
git -C "$GIT_SOURCE" tag v100.1.0-pinned-test
sed -i 's/100.1.0-pinned-test/100.2.0-main-advanced/g' "$GIT_SOURCE/manifest.json"
git -C "$GIT_SOURCE" add manifest.json
git -C "$GIT_SOURCE" commit -qm advanced
printf '%s\n' \
  '{' \
  '  "version": "100.1.0-pinned-test",' \
  '  "git_ref": "v100.1.0-pinned-test",' \
  '  "updated": "2099-01-01T00:00:00Z",' \
  '  "state_schema_version": "1",' \
  '  "machine_profile_schema_version": "1"' \
  '}' > "$TEST_ROOT/pages-manifest.json"
bash "$SOURCE/scripts/update-from-pages.sh" "$PROJECT" "file://$TEST_ROOT/pages-manifest.json" "$GIT_SOURCE" "" "$TEST_ROOT/clone" >/dev/null
test "$(sed -n 's/^- Package version:[[:space:]]*//p' "$PROJECT/.ai/COMPUTING_ENVIRONMENT_VERSION.md")" = '100.1.0-pinned-test'
if bash "$SOURCE/scripts/install-from-git.sh" --dry-run "$PROJECT" "$GIT_SOURCE" main "$TEST_ROOT/clone" 100.1.0-pinned-test >/dev/null 2>&1; then
  echo 'version mismatch unexpectedly accepted' >&2
  exit 1
fi

if command -v pwsh >/dev/null 2>&1; then
  PS_PROJECT="$TEST_ROOT/ps-project"
  mkdir -p "$PS_PROJECT"
  printf '# PowerShell user rules\n' > "$PS_PROJECT/AGENTS.md"
  pwsh -NoProfile -File "$SOURCE/scripts/install-to-project.ps1" -ProjectPath "$PS_PROJECT" -SourcePath "$SOURCE" >/dev/null
  printf 'powershell-state-sentinel\n' > "$PS_PROJECT/.ai/PROJECT_STATE.md"
  if pwsh -NoProfile -File "$SOURCE/scripts/install-to-project.ps1" -ProjectPath "$PS_PROJECT" -SourcePath "$BAD_SOURCE" >/dev/null 2>&1; then
    echo 'PowerShell incomplete source unexpectedly installed' >&2
    exit 1
  fi
  pwsh -NoProfile -File "$SOURCE/scripts/install-to-project.ps1" -ProjectPath "$PS_PROJECT" -SourcePath "$GOOD_SOURCE" >/dev/null
  grep -q 'transaction-test-marker' "$PS_PROJECT/.ai/agent-project-kit/STARTUP.md"
  rm "$PS_PROJECT/AGENTS.md"
  mkdir "$PS_PROJECT/AGENTS.md"
  if pwsh -NoProfile -File "$SOURCE/scripts/install-to-project.ps1" -ProjectPath "$PS_PROJECT" -SourcePath "$FAIL_SOURCE" >/dev/null 2>&1; then
    echo 'PowerShell post-swap failure unexpectedly succeeded' >&2
    exit 1
  fi
  grep -q 'transaction-test-marker' "$PS_PROJECT/.ai/agent-project-kit/STARTUP.md"
  ! grep -q 'rollback-test-marker' "$PS_PROJECT/.ai/agent-project-kit/STARTUP.md"
  test -d "$PS_PROJECT/AGENTS.md"
  grep -q 'powershell-state-sentinel' "$PS_PROJECT/.ai/PROJECT_STATE.md"
  rm -rf "$PS_PROJECT/AGENTS.md"
  printf '# PowerShell user rules\n' > "$PS_PROJECT/AGENTS.md"
  pwsh -NoProfile -File "$SOURCE/scripts/install-from-git.ps1" -ProjectPath "$PS_PROJECT" -RepoUrl "$GIT_SOURCE" -Ref v100.1.0-pinned-test -CloneDir "$TEST_ROOT/ps-clone" -ExpectedVersion 100.1.0-pinned-test >/dev/null
  test "$(sed -n 's/^- Package version:[[:space:]]*//p' "$PS_PROJECT/.ai/COMPUTING_ENVIRONMENT_VERSION.md")" = '100.1.0-pinned-test'
  if pwsh -NoProfile -File "$SOURCE/scripts/install-from-git.ps1" -DryRun -ProjectPath "$PS_PROJECT" -RepoUrl "$GIT_SOURCE" -Ref main -CloneDir "$TEST_ROOT/ps-clone" -ExpectedVersion 100.1.0-pinned-test >/dev/null 2>&1; then
    echo 'PowerShell version mismatch unexpectedly accepted' >&2
    exit 1
  fi
fi

echo 'transactional update tests: PASS'
