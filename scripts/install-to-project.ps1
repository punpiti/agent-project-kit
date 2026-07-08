param(
    [string]$ProjectPath = ".",
    [string]$SourcePath = ""
)

$ErrorActionPreference = "Stop"

function Find-SourcePath {
    param([string]$GivenSourcePath)

    if ($GivenSourcePath -and (Test-Path $GivenSourcePath)) {
        return (Resolve-Path $GivenSourcePath).Path
    }

    $scriptSource = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
    $candidates = @(
        $scriptSource,
        (Join-Path $env:OneDrive "agent-project-kit"),
        (Join-Path $env:OneDriveCommercial "agent-project-kit"),
        (Join-Path $env:OneDriveConsumer "agent-project-kit"),
        (Join-Path $env:OneDrive "computing-environment"),
        (Join-Path $env:OneDriveCommercial "computing-environment"),
        (Join-Path $env:OneDriveConsumer "computing-environment")
    ) | Where-Object { $_ -and $_ -ne "\computing-environment" }

    if ($env:USERPROFILE) {
        Get-ChildItem -Path $env:USERPROFILE -Directory -Filter "OneDrive*" -ErrorAction SilentlyContinue | ForEach-Object {
            $candidates += (Join-Path $_.FullName "agent-project-kit")
            $candidates += (Join-Path $_.FullName "computing-environment")
        }
    }

    foreach ($p in $candidates) {
        if ($p -and (Test-Path (Join-Path $p "START_HERE.md"))) {
            return (Resolve-Path $p).Path
        }
    }

    throw "SourcePath not found. Pass -SourcePath explicitly."
}

$SourcePath = Find-SourcePath $SourcePath
$project = (Resolve-Path $ProjectPath).Path
$aiDir = Join-Path $project ".ai"
$target = Join-Path $aiDir "computing-environment"
$machine = ($env:COMPUTERNAME).ToLower()

New-Item -ItemType Directory -Force -Path $target | Out-Null

$items = @(
    "manifest.json",
    "PACKAGE_CONTENTS.md",
    "README.md",
    "INSTALL_IN_PROJECT.md",
    "GIT_DISTRIBUTION.md",
    "OPEN_WITH_AGENT.md",
    "MARKDOWN_OVER_ARCHIVE_RECOVERY.md",
    "START_HERE.md",
    "SPEC_EVAL_LOOP_INSTRUCTION.md",
    "AGENTS.md",
    "CLAUDE.md",
    "ANTIGRAVITY.md",
    "AI_CLIENTS.md",
    "MACHINE_PROFILES.md",
    "TOKEN_DISCIPLINE.md",
    "DOCUMENT_PRODUCTION_POLICY.md",
    "ENVIRONMENT_POLICY.md",
    "GLOBAL_START_PROMPT.md",
    "bootstrap_ai_project.py",
    "prompts",
    "templates",
    "checklists"
)

foreach ($item in $items) {
    $src = Join-Path $SourcePath $item
    $dst = Join-Path $target $item
    if (Test-Path $src) {
        if (Test-Path $dst) { Remove-Item $dst -Recurse -Force }
        Copy-Item -Path $src -Destination $dst -Recurse -Force
    } else {
        Write-Warning "Missing item: $src"
    }
}

New-Item -ItemType Directory -Force -Path $aiDir | Out-Null

function Copy-TemplateIfMissing($TemplateName, $TargetName) {
    $dst = Join-Path $aiDir $TargetName
    if (-not (Test-Path $dst)) {
        $src = Join-Path (Join-Path $SourcePath "templates") $TemplateName
        if (Test-Path $src) {
            Copy-Item $src $dst
        } else {
            New-Item -ItemType File -Path $dst | Out-Null
        }
    }
}

Copy-TemplateIfMissing "PROJECT_STATE.md" "PROJECT_STATE.md"
Copy-TemplateIfMissing "PROJECT_HIERARCHY.md" "PROJECT_HIERARCHY.md"
Copy-TemplateIfMissing "MACHINE_PROFILE.md" "MACHINE_PROFILE.md"
Copy-TemplateIfMissing "COMPUTING_ENVIRONMENT_VERSION.md" "COMPUTING_ENVIRONMENT_VERSION.md"
Copy-TemplateIfMissing "LOCAL_RESOURCES.md" "LOCAL_RESOURCES.md"
Copy-TemplateIfMissing "MACHINE_COMPATIBILITY.md" "MACHINE_COMPATIBILITY.md"
Copy-TemplateIfMissing "RUNBOOK.md" "RUNBOOK.md"
Copy-TemplateIfMissing "TOKEN_BUDGET.md" "TOKEN_BUDGET.md"
Copy-TemplateIfMissing "SESSION_LOG.md" "SESSION_LOG.md"
Copy-TemplateIfMissing "ENVIRONMENT_VARIABLES.md" "ENVIRONMENT_VARIABLES.md"

$manifestPath = Join-Path $SourcePath "manifest.json"
$packageName = "agent-project-kit"
$packageDisplayName = "Agent Project Kit"
$legacyNames = "computing-environment"
$packageVersion = "unknown"
$packageUpdated = "unknown"
$stateSchema = "unknown"
$profileSchema = "unknown"
if (Test-Path $manifestPath) {
    try {
        $manifest = Get-Content $manifestPath -Raw | ConvertFrom-Json
        if ($manifest.name) { $packageName = [string]$manifest.name }
        if ($manifest.display_name) { $packageDisplayName = [string]$manifest.display_name }
        if ($manifest.legacy_names) { $legacyNames = ($manifest.legacy_names -join ", ") }
        if ($manifest.version) { $packageVersion = [string]$manifest.version }
        if ($manifest.updated) { $packageUpdated = [string]$manifest.updated }
        if ($manifest.state_schema_version) { $stateSchema = [string]$manifest.state_schema_version }
        if ($manifest.machine_profile_schema_version) { $profileSchema = [string]$manifest.machine_profile_schema_version }
    } catch {
        Write-Warning "Could not parse manifest.json: $_"
    }
}

function Read-VersionLine($Path, $Label) {
    if (-not (Test-Path $Path)) { return "none" }
    $prefix = "- ${Label}:"
    foreach ($line in Get-Content $Path -ErrorAction SilentlyContinue) {
        if ($line.StartsWith($prefix)) {
            $value = $line.Substring($prefix.Length).Trim()
            if ($value) { return $value }
            return "none"
        }
    }
    return "none"
}

$versionPath = Join-Path $aiDir "COMPUTING_ENVIRONMENT_VERSION.md"
$previousPackageVersion = Read-VersionLine $versionPath "Package version"
$previousProfileSchema = Read-VersionLine $versionPath "Machine profile schema version"

$versionInfo = @"
# COMPUTING_ENVIRONMENT_VERSION

- Package name: $packageName
- Package display name: $packageDisplayName
- Legacy package names: $legacyNames
- Package version: $packageVersion
- Package updated: $packageUpdated
- State schema version: $stateSchema
- Machine profile schema version: $profileSchema
- Previous package version: $previousPackageVersion
- Previous machine profile schema version: $previousProfileSchema
- Installed/updated: $(Get-Date -Format o)
- Source path: $SourcePath
- Installer: install-to-project.ps1
- Machine: $machine
- WSL2 detected: no / Windows PowerShell

## Update Rule

If package version changes but machine profile schema version is unchanged,
reuse `.ai/MACHINE_PROFILE.md`; do not rerun first-use discovery unless
hostname/platform/path style changed.

Project-local state files are preserved by the installer. Update package
snapshots and missing template files without overwriting project-specific state.
"@
Set-Content -Path (Join-Path $aiDir "COMPUTING_ENVIRONMENT_VERSION.md") -Value $versionInfo -Encoding UTF8

$installInfo = @"
# INSTALLATION_INFO

- Package version: $packageVersion
- State schema version: $stateSchema
- Machine profile schema version: $profileSchema
- Installed/updated: $(Get-Date -Format o)
- Project path: $project
- Computing environment source: $SourcePath
- Machine detected: $machine
- WSL2 detected: no / Windows PowerShell

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
"@
Set-Content -Path (Join-Path $aiDir "INSTALLATION_INFO.md") -Value $installInfo -Encoding UTF8

$projectAgents = Join-Path $project "AGENTS.md"
$managedBlock = "<!-- BEGIN COMPUTING-ENVIRONMENT -->"
$agentsBlock = @"
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

Then read project state:

- `.ai/PROJECT_STATE.md`
- `.ai/PROJECT_HIERARCHY.md`
- `.ai/MACHINE_PROFILE.md`
- `.ai/LOCAL_RESOURCES.md`
- `.ai/MACHINE_COMPATIBILITY.md`
- `.ai/RUNBOOK.md`
- `.ai/TOKEN_BUDGET.md`
- `.ai/SESSION_LOG.md`
- `.ai/COMPUTING_ENVIRONMENT_VERSION.md`

Use Spec–Eval–Loop Workflow.
Do not pretend L2 or L3 has been resolved by L1 alone.
Record machine identity/storage assumptions in `.ai/MACHINE_PROFILE.md`.
Do not pretend files outside the project/shared source tree exist on every machine.
<!-- END COMPUTING-ENVIRONMENT -->
"@

if (-not (Test-Path $projectAgents)) {
    Set-Content -Path $projectAgents -Value "# AGENTS.md`n`n$agentsBlock" -Encoding UTF8
} else {
    $existing = Get-Content $projectAgents -Raw
    if ($existing -notmatch [regex]::Escape($managedBlock)) {
        Add-Content -Path $projectAgents -Value "`n$agentsBlock" -Encoding UTF8
    }
}

function Update-AdapterFile($FileName) {
    $path = Join-Path $project $FileName
    $marker = "<!-- BEGIN AGENT-PROJECT-KIT-ADAPTER -->"
    $block = @"
# $FileName

$marker
This project uses Agent Project Kit.

Read these first:

1. `AGENTS.md`
2. `.ai/PROJECT_STATE.md`
3. `.ai/PROJECT_HIERARCHY.md`
4. `.ai/COMPUTING_ENVIRONMENT_VERSION.md`
5. `.ai/MACHINE_PROFILE.md`
6. `.ai/LOCAL_RESOURCES.md`
7. `.ai/MACHINE_COMPATIBILITY.md`
8. `.ai/RUNBOOK.md`
9. `.ai/TOKEN_BUDGET.md`

Follow the Spec-Eval-Loop workflow in `AGENTS.md`.
Do not overwrite project-local `.ai/` state when updating Agent Project Kit.
<!-- END AGENT-PROJECT-KIT-ADAPTER -->
"@
    if (-not (Test-Path $path)) {
        Set-Content -Path $path -Value $block -Encoding UTF8
    } else {
        $existing = Get-Content $path -Raw
        if ($existing -notmatch [regex]::Escape($marker)) {
            Add-Content -Path $path -Encoding UTF8 -Value @"

$marker
Agent Project Kit adapter: read `AGENTS.md` and project-local `.ai/` state
before acting. Do not overwrite project-local `.ai/` state when updating the
kit.
<!-- END AGENT-PROJECT-KIT-ADAPTER -->
"@
        }
    }
}

Update-AdapterFile "CLAUDE.md"
Update-AdapterFile "ANTIGRAVITY.md"

$sessionLog = Join-Path $aiDir "SESSION_LOG.md"
if (Test-Path $sessionLog) {
    Add-Content -Path $sessionLog -Encoding UTF8 -Value @"

## $(Get-Date -Format yyyy-MM-dd) — $machine — Agent Project Kit installed/updated
- Objective: Install/update Agent Project Kit workflow files.
- Mode: T0 Quick
- Files touched: AGENTS.md, .ai/computing-environment/, .ai project templates if missing
- Commands/tests run: install-to-project.ps1
- Result: Installed from $SourcePath
- Local resources used: none
- Decisions made: none
- Open questions: Fill PROJECT_HIERARCHY.md to declare whether this directory is a project/subproject/plain subdir; fill MACHINE_PROFILE.md for new machines; if package version changed but machine profile schema did not, reuse the existing profile; fill LOCAL_RESOURCES.md if project uses non-portable cache/data
- Next action: Resume project via PROJECT_STATE.md
- Token note: Future sessions should read PROJECT_STATE.md before scanning broadly.
"@
}

Write-Host "Installed Agent Project Kit into: $target"
Write-Host "Created/updated project AGENTS.md: $projectAgents"
Write-Host "Project AI state directory: $aiDir"
Write-Host "Detected machine: $machine"
