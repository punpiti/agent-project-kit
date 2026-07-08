#!/usr/bin/env bash
set -euo pipefail

PROJECT_PATH="${1:-.}"
SOURCE_PATH="${2:-}"

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
script_source="$(cd "$script_dir/.." && pwd)"

find_source_path() {
  if [ -n "$SOURCE_PATH" ] && [ -d "$SOURCE_PATH" ]; then
    echo "$SOURCE_PATH"
    return 0
  fi

  local candidates=(
    "$script_source"
    "$HOME/OneDrive/agent-project-kit"
    "$HOME/OneDrive - Kasetsart University/agent-project-kit"
    "$HOME/OneDrive/computing-environment"
    "$HOME/OneDrive - Kasetsart University/computing-environment"
  )

  # Common WSL2 OneDrive mounts. Glob is intentional.
  for p in /mnt/c/Users/*/OneDrive/agent-project-kit \
           /mnt/c/Users/*/OneDrive\ -\ */agent-project-kit \
           /mnt/d/Users/*/OneDrive/agent-project-kit \
           /mnt/d/Users/*/OneDrive\ -\ */agent-project-kit \
           /mnt/c/Users/*/OneDrive/computing-environment \
           /mnt/c/Users/*/OneDrive\ -\ */computing-environment \
           /mnt/d/Users/*/OneDrive/computing-environment \
           /mnt/d/Users/*/OneDrive\ -\ */computing-environment; do
    [ -d "$p" ] && candidates+=("$p")
  done

  for p in "${candidates[@]}"; do
    if [ -d "$p" ] && [ -f "$p/START_HERE.md" ]; then
      echo "$p"
      return 0
    fi
  done

  return 1
}

SOURCE_PATH="$(find_source_path)" || {
  echo "SourcePath not found. Pass it explicitly:" >&2
  echo "  bash install-to-project.sh /path/to/project /path/to/agent-project-kit" >&2
  exit 1
}

PROJECT_PATH="$(cd "$PROJECT_PATH" && pwd)"
AI_DIR="$PROJECT_PATH/.ai"
TARGET="$AI_DIR/computing-environment"
MACHINE="$(hostname 2>/dev/null | tr '[:upper:]' '[:lower:]' || echo unknown)"
if grep -qi microsoft /proc/version 2>/dev/null || grep -qi wsl /proc/version 2>/dev/null; then
  IS_WSL2="yes"
else
  IS_WSL2="unknown/no"
fi

mkdir -p "$TARGET"

items=(
  manifest.json
  PACKAGE_CONTENTS.md
  README.md
  INSTALL_IN_PROJECT.md
  GIT_DISTRIBUTION.md
  OPEN_WITH_AGENT.md
  MARKDOWN_OVER_ARCHIVE_RECOVERY.md
  START_HERE.md
  SPEC_EVAL_LOOP_INSTRUCTION.md
  AGENTS.md
  CLAUDE.md
  ANTIGRAVITY.md
  AI_CLIENTS.md
  MACHINE_PROFILES.md
  TOKEN_DISCIPLINE.md
  DOCUMENT_PRODUCTION_POLICY.md
  MARKDOWN_ORGANIZATION_POLICY.md
  SECURITY_EXCLUSIONS.md
  MIGRATION_FROM_OLD.md
  ENVIRONMENT_POLICY.md
  GLOBAL_START_PROMPT.md
  bootstrap_ai_project.py
  prompts
  templates
  checklists
  scripts
)

manifest_value() {
  local key="$1"
  if [ -f "$SOURCE_PATH/manifest.json" ]; then
    sed -n "s/^[[:space:]]*\"$key\"[[:space:]]*:[[:space:]]*\"\\([^\"]*\\)\".*/\\1/p" "$SOURCE_PATH/manifest.json" | head -n 1
  fi
}

PACKAGE_NAME="$(manifest_value name)"
PACKAGE_DISPLAY_NAME="$(manifest_value display_name)"
PACKAGE_VERSION="$(manifest_value version)"
PACKAGE_UPDATED="$(manifest_value updated)"
STATE_SCHEMA_VERSION="$(manifest_value state_schema_version)"
MACHINE_PROFILE_SCHEMA_VERSION="$(manifest_value machine_profile_schema_version)"
PACKAGE_NAME="${PACKAGE_NAME:-agent-project-kit}"
PACKAGE_DISPLAY_NAME="${PACKAGE_DISPLAY_NAME:-Agent Project Kit}"
PACKAGE_VERSION="${PACKAGE_VERSION:-unknown}"
PACKAGE_UPDATED="${PACKAGE_UPDATED:-unknown}"
STATE_SCHEMA_VERSION="${STATE_SCHEMA_VERSION:-unknown}"
MACHINE_PROFILE_SCHEMA_VERSION="${MACHINE_PROFILE_SCHEMA_VERSION:-unknown}"

for item in "${items[@]}"; do
  src="$SOURCE_PATH/$item"
  dst="$TARGET/$item"
  if [ -e "$src" ]; then
    rm -rf "$dst"
    cp -R "$src" "$dst"
  else
    echo "Warning: missing item $src" >&2
  fi
done

create_from_template() {
  local template="$1"
  local target="$2"
  if [ ! -f "$target" ]; then
    if [ -f "$SOURCE_PATH/templates/$template" ]; then
      cp "$SOURCE_PATH/templates/$template" "$target"
    else
      touch "$target"
    fi
  fi
}

mkdir -p "$AI_DIR"
create_from_template PROJECT_STATE.md "$AI_DIR/PROJECT_STATE.md"
create_from_template PROJECT_HIERARCHY.md "$AI_DIR/PROJECT_HIERARCHY.md"
create_from_template MACHINE_PROFILE.md "$AI_DIR/MACHINE_PROFILE.md"
create_from_template LOCAL_RESOURCES.md "$AI_DIR/LOCAL_RESOURCES.md"
create_from_template MACHINE_COMPATIBILITY.md "$AI_DIR/MACHINE_COMPATIBILITY.md"
create_from_template RUNBOOK.md "$AI_DIR/RUNBOOK.md"
create_from_template TOKEN_BUDGET.md "$AI_DIR/TOKEN_BUDGET.md"
create_from_template SESSION_LOG.md "$AI_DIR/SESSION_LOG.md"
create_from_template ENVIRONMENT_VARIABLES.md "$AI_DIR/ENVIRONMENT_VARIABLES.md"
create_from_template DOCUMENT_PIPELINE.md "$AI_DIR/DOCUMENT_PIPELINE.md"
create_from_template DOCUMENT_STYLE.md "$AI_DIR/DOCUMENT_STYLE.md"
create_from_template DOCUMENT_QA.md "$AI_DIR/DOCUMENT_QA.md"
create_from_template MARKDOWN_INVENTORY.md "$AI_DIR/MARKDOWN_INVENTORY.md"

PREVIOUS_PACKAGE_VERSION=""
PREVIOUS_MACHINE_PROFILE_SCHEMA_VERSION=""
if [ -f "$AI_DIR/COMPUTING_ENVIRONMENT_VERSION.md" ]; then
  PREVIOUS_PACKAGE_VERSION="$(sed -n 's/^- Package version:[[:space:]]*//p' "$AI_DIR/COMPUTING_ENVIRONMENT_VERSION.md" | head -n 1)"
  PREVIOUS_MACHINE_PROFILE_SCHEMA_VERSION="$(sed -n 's/^- Machine profile schema version:[[:space:]]*//p' "$AI_DIR/COMPUTING_ENVIRONMENT_VERSION.md" | head -n 1)"
fi
PREVIOUS_PACKAGE_VERSION="${PREVIOUS_PACKAGE_VERSION:-none}"
PREVIOUS_MACHINE_PROFILE_SCHEMA_VERSION="${PREVIOUS_MACHINE_PROFILE_SCHEMA_VERSION:-none}"

cat > "$AI_DIR/COMPUTING_ENVIRONMENT_VERSION.md" <<EOF2
# COMPUTING_ENVIRONMENT_VERSION

- Package name: $PACKAGE_NAME
- Package display name: $PACKAGE_DISPLAY_NAME
- Legacy package names: computing-environment
- Package version: $PACKAGE_VERSION
- Package updated: $PACKAGE_UPDATED
- State schema version: $STATE_SCHEMA_VERSION
- Machine profile schema version: $MACHINE_PROFILE_SCHEMA_VERSION
- Previous package version: $PREVIOUS_PACKAGE_VERSION
- Previous machine profile schema version: $PREVIOUS_MACHINE_PROFILE_SCHEMA_VERSION
- Installed/updated: $(date -Iseconds)
- Source path: $SOURCE_PATH
- Installer: install-to-project.sh
- Machine: $MACHINE
- WSL2 detected: $IS_WSL2

## Update Rule

If package version changes but machine profile schema version is unchanged,
reuse \`.ai/MACHINE_PROFILE.md\`; do not rerun first-use discovery unless
hostname/platform/path style changed.

Project-local state files are preserved by the installer. Update package
snapshots and missing template files without overwriting project-specific state.
EOF2

cat > "$AI_DIR/INSTALLATION_INFO.md" <<EOF2
# INSTALLATION_INFO

- Package version: $PACKAGE_VERSION
- State schema version: $STATE_SCHEMA_VERSION
- Machine profile schema version: $MACHINE_PROFILE_SCHEMA_VERSION
- Installed/updated: $(date -Iseconds)
- Project path: $PROJECT_PATH
- Computing environment source: $SOURCE_PATH
- Machine detected: $MACHINE
- WSL2 detected: $IS_WSL2

Read this project with:

1. AGENTS.md
2. .ai/computing-environment/START_HERE.md
3. .ai/PROJECT_STATE.md
4. .ai/PROJECT_HIERARCHY.md
5. .ai/MACHINE_PROFILE.md
6. .ai/LOCAL_RESOURCES.md
7. .ai/MACHINE_COMPATIBILITY.md
8. .ai/RUNBOOK.md
9. .ai/TOKEN_BUDGET.md
10. .ai/COMPUTING_ENVIRONMENT_VERSION.md
EOF2

PROJECT_AGENTS="$PROJECT_PATH/AGENTS.md"
MANAGED_BLOCK='<!-- BEGIN COMPUTING-ENVIRONMENT -->'
if [ ! -f "$PROJECT_AGENTS" ]; then
  cat > "$PROJECT_AGENTS" <<'EOF2'
# AGENTS.md

<!-- BEGIN COMPUTING-ENVIRONMENT -->
Before working on this project, read the project-local AI working rules:

If this project is the Agent Project Kit source repository itself, including the
legacy `computing-environment` folder, use the root-level governance files as
canonical and treat `.ai/computing-environment/` as a packaged downstream
snapshot. Do not recurse into another Agent Project Kit / `computing-environment`
layer unless explicitly requested.

- `.ai/computing-environment/START_HERE.md`
- `.ai/computing-environment/SPEC_EVAL_LOOP_INSTRUCTION.md`
- `.ai/computing-environment/AGENTS.md`
- `.ai/computing-environment/MACHINE_PROFILES.md`
- `.ai/computing-environment/TOKEN_DISCIPLINE.md`
- `.ai/computing-environment/DOCUMENT_PRODUCTION_POLICY.md`
- `.ai/computing-environment/MARKDOWN_ORGANIZATION_POLICY.md`
- `.ai/computing-environment/ENVIRONMENT_POLICY.md`

Then read project state:

- `.ai/PROJECT_STATE.md`
- `.ai/PROJECT_HIERARCHY.md`
- `.ai/MACHINE_PROFILE.md`
- `.ai/LOCAL_RESOURCES.md`
- `.ai/MACHINE_COMPATIBILITY.md`
- `.ai/RUNBOOK.md`
- `.ai/TOKEN_BUDGET.md`
- `.ai/SESSION_LOG.md`
- `.ai/DOCUMENT_PIPELINE.md`
- `.ai/DOCUMENT_STYLE.md`
- `.ai/DOCUMENT_QA.md`
- `.ai/MARKDOWN_INVENTORY.md`
- `.ai/COMPUTING_ENVIRONMENT_VERSION.md`

Use Spec–Eval–Loop Workflow:

- L1 = AI execution: code, test, debug, draft, analyze
- L2 = human context: product direction, audience, UX, academic judgment, stakeholder risk
- L3 = external feedback: users, reviewers, students, stakeholders, data, experiments

Record machine identity/storage assumptions in `.ai/MACHINE_PROFILE.md`.

For non-trivial tasks, respond with:

1. Loop Diagnosis
2. Working Spec
3. Evals / Acceptance Criteria
4. Execution
5. Review Gate, including machine/local-resource and token notes when relevant

Do not pretend L2 or L3 has been resolved by L1 alone.
Do not pretend files outside the project/shared source tree exist on every machine.
For document work, start with Markdown, use project style sheets, and run final PDF QA before calling a document final.
Do not create loose Markdown scratch files; put AI working notes in `.ai/` and register document sources in `.ai/DOCUMENT_PIPELINE.md`.
<!-- END COMPUTING-ENVIRONMENT -->
EOF2
else
  if ! grep -q "$MANAGED_BLOCK" "$PROJECT_AGENTS"; then
    cat >> "$PROJECT_AGENTS" <<'EOF2'

<!-- BEGIN COMPUTING-ENVIRONMENT -->

## Computing Environment Rules

Self-hosting guard: if this project is the Agent Project Kit source repository
itself, including the legacy `computing-environment` folder, use root-level
governance files as canonical and treat `.ai/computing-environment/` as a
packaged downstream snapshot. Do not recurse into another Agent Project Kit /
`computing-environment` layer unless explicitly requested.

Before working on this project, read:

- `.ai/computing-environment/START_HERE.md`
- `.ai/computing-environment/SPEC_EVAL_LOOP_INSTRUCTION.md`
- `.ai/computing-environment/AGENTS.md`
- `.ai/computing-environment/MACHINE_PROFILES.md`
- `.ai/computing-environment/TOKEN_DISCIPLINE.md`
- `.ai/computing-environment/DOCUMENT_PRODUCTION_POLICY.md`
- `.ai/computing-environment/MARKDOWN_ORGANIZATION_POLICY.md`
- `.ai/computing-environment/ENVIRONMENT_POLICY.md`
- `.ai/computing-environment/MARKDOWN_ORGANIZATION_POLICY.md`
- `.ai/PROJECT_STATE.md`
- `.ai/PROJECT_HIERARCHY.md`
- `.ai/MACHINE_PROFILE.md`
- `.ai/LOCAL_RESOURCES.md`
- `.ai/MACHINE_COMPATIBILITY.md`
- `.ai/RUNBOOK.md`
- `.ai/TOKEN_BUDGET.md`

Use Spec–Eval–Loop Workflow, record machine identity/storage assumptions in `.ai/MACHINE_PROFILE.md`, record non-portable local resources, and keep AI Markdown in the `.ai/` pipeline.
Do not pretend L2/L3 or non-portable resources are solved by L1 alone.

<!-- END COMPUTING-ENVIRONMENT -->
EOF2
  fi
fi

create_adapter_file() {
  local target_file="$1"
  local title="$2"
  local marker='<!-- BEGIN AGENT-PROJECT-KIT-ADAPTER -->'
  if [ ! -f "$target_file" ]; then
    cat > "$target_file" <<EOF2
# $title

$marker
This project uses Agent Project Kit.

Read these first:

1. \`AGENTS.md\`
2. \`.ai/PROJECT_STATE.md\`
3. \`.ai/PROJECT_HIERARCHY.md\`
4. \`.ai/COMPUTING_ENVIRONMENT_VERSION.md\`
5. \`.ai/MACHINE_PROFILE.md\`
6. \`.ai/LOCAL_RESOURCES.md\`
7. \`.ai/MACHINE_COMPATIBILITY.md\`
8. \`.ai/RUNBOOK.md\`
9. \`.ai/TOKEN_BUDGET.md\`

Follow the Spec-Eval-Loop workflow in \`AGENTS.md\`.
Do not overwrite project-local \`.ai/\` state when updating Agent Project Kit.
<!-- END AGENT-PROJECT-KIT-ADAPTER -->
EOF2
  elif ! grep -q "$marker" "$target_file"; then
    cat >> "$target_file" <<EOF2

$marker
Agent Project Kit adapter: read \`AGENTS.md\` and project-local \`.ai/\` state
before acting. Do not overwrite project-local \`.ai/\` state when updating the
kit.
<!-- END AGENT-PROJECT-KIT-ADAPTER -->
EOF2
  fi
}

create_adapter_file "$PROJECT_PATH/CLAUDE.md" "CLAUDE.md"
create_adapter_file "$PROJECT_PATH/ANTIGRAVITY.md" "ANTIGRAVITY.md"

if [ -f "$AI_DIR/SESSION_LOG.md" ]; then
  cat >> "$AI_DIR/SESSION_LOG.md" <<EOF2

## $(date +%F) — $MACHINE — Agent Project Kit installed/updated
- Objective: Install/update Agent Project Kit workflow files.
- Mode: T0 Quick
- Files touched: AGENTS.md, .ai/computing-environment/, .ai project templates if missing
- Commands/tests run: install-to-project.sh
- Result: Installed from $SOURCE_PATH
- Local resources used: none
- Decisions made: none
- Open questions: Fill PROJECT_HIERARCHY.md to declare whether this directory is a project/subproject/plain subdir; fill MACHINE_PROFILE.md for new machines; if package version changed but machine profile schema did not, reuse the existing profile; fill LOCAL_RESOURCES.md and DOCUMENT_PIPELINE.md if project uses non-portable cache/data/build files; run organize-project-markdown.py if scattered Markdown exists
- Next action: Resume project via PROJECT_STATE.md
- Token note: Future sessions should read PROJECT_STATE.md before scanning broadly.
EOF2
fi

echo "Installed Agent Project Kit into: $TARGET"
echo "Created/updated project AGENTS.md: $PROJECT_AGENTS"
echo "Project AI state directory: $AI_DIR"
echo "Detected machine: $MACHINE"
echo "WSL2 detected: $IS_WSL2"
