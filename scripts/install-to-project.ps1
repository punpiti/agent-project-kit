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
$target = Join-Path $aiDir "agent-project-kit"
$previousTarget = Join-Path $aiDir "agent-project-kit.previous"
$olderPreviousTarget = Join-Path $aiDir "agent-project-kit.previous.old"
$stage = ""
$controlBackup = ""
$controlBackupReady = $false
$controlPaths = @()
$snapshotSwapped = $false
$hadTarget = $false
$previousRotated = $false

function Restore-SnapshotTransaction {
    if ($script:snapshotSwapped) {
        if (Test-Path -LiteralPath $script:target) {
            Remove-Item -LiteralPath $script:target -Recurse -Force
        }
        if ($script:hadTarget -and (Test-Path -LiteralPath $script:previousTarget)) {
            Move-Item -LiteralPath $script:previousTarget -Destination $script:target
        }
        Write-Warning "Install failed; restored the previous Agent Project Kit snapshot."
    }
    if ($script:previousRotated -and (Test-Path -LiteralPath $script:olderPreviousTarget)) {
        if (Test-Path -LiteralPath $script:previousTarget) {
            Remove-Item -LiteralPath $script:previousTarget -Recurse -Force
        }
        Move-Item -LiteralPath $script:olderPreviousTarget -Destination $script:previousTarget
    }
    if ($script:stage -and (Test-Path -LiteralPath $script:stage)) {
        Remove-Item -LiteralPath $script:stage -Recurse -Force
    }
    if ($script:controlBackupReady -and $script:controlBackup -and (Test-Path -LiteralPath $script:controlBackup)) {
        for ($index = 0; $index -lt $script:controlPaths.Count; $index++) {
            $path = $script:controlPaths[$index]
            if (Test-Path -LiteralPath $path) {
                Remove-Item -LiteralPath $path -Recurse -Force
            }
            $saved = Join-Path $script:controlBackup ([string]$index)
            if (Test-Path -LiteralPath $saved) {
                $parent = Split-Path -Parent $path
                New-Item -ItemType Directory -Force -Path $parent | Out-Null
                Copy-Item -LiteralPath $saved -Destination $path -Recurse -Force
            }
        }
    }
    if ($script:controlBackup -and (Test-Path -LiteralPath $script:controlBackup)) {
        Remove-Item -LiteralPath $script:controlBackup -Recurse -Force
    }
}

trap {
    Restore-SnapshotTransaction
    Write-Error $_
    exit 1
}

$firstInstall = if (Test-Path $target) { "no" } else { "yes" }
$machine = if ($env:COMPUTERNAME) { $env:COMPUTERNAME.ToLower() } else { "unknown" }
$environmentManager = "none (deferred; install user-local micromamba only when an environment is needed)"
foreach ($managerName in @("micromamba", "mamba", "microconda", "conda")) {
    $managerCommand = Get-Command $managerName -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($managerCommand) {
        $environmentManager = "$managerName ($($managerCommand.Source))"
        break
    }
}
if ($firstInstall -eq "yes") {
    Write-Host "Environment-manager preflight: $environmentManager"
}
New-Item -ItemType Directory -Force -Path $aiDir | Out-Null

if ((Resolve-Path $SourcePath).Path -eq (Resolve-Path -LiteralPath $target -ErrorAction SilentlyContinue).Path) {
    throw "Source path equals install target: $target. Clone Agent Project Kit into .ai/agent-project-kit-source or use a cache path, then rerun."
}

function Test-ManagedSnapshot {
    param([string]$Path)
    if (-not (Test-Path $Path)) { return $true }
    $manifestPath = Join-Path $Path "manifest.json"
    if (Test-Path $manifestPath) {
        try {
            $manifest = Get-Content $manifestPath -Raw | ConvertFrom-Json
            return ($manifest.name -eq "agent-project-kit" -or $manifest.name -eq "computing-environment")
        } catch {
            return $false
        }
    }
    return $false
}

function Assert-ManagedOrMissing {
    param([string]$Path, [string]$Purpose)
    if (-not (Test-ManagedSnapshot $Path)) {
        throw "Refusing to overwrite existing ${Purpose}: ${Path}. This path exists but does not look like an Agent Project Kit snapshot. Move or rename it first, then rerun the installer."
    }
}

function Test-KitMetadata {
    param([string]$Path)
    if (-not (Test-Path $Path)) { return $true }
    foreach ($line in Get-Content $Path -ErrorAction SilentlyContinue) {
        if ($line -match 'Package name:\s*(agent-project-kit|computing-environment)') { return $true }
        if ($line -match 'Computing environment source') { return $true }
        if ($line -match 'Agent Project Kit source') { return $true }
    }
    return $false
}

function Assert-MetadataSafe {
    param([string]$Path)
    if (-not (Test-KitMetadata $Path)) {
        throw "Refusing to overwrite existing user file: ${Path}. This file name is needed for Agent Project Kit metadata, but the existing file does not look like kit metadata. Move or rename it first, then rerun the installer."
    }
}

function Assert-StagedItemIntegrity {
    param([string]$SourceRoot, [string]$StageRoot, [string]$Item)
    $sourceItem = Join-Path $SourceRoot $Item
    $stageItem = Join-Path $StageRoot $Item
    $sourceFiles = if ((Get-Item -LiteralPath $sourceItem).PSIsContainer) {
        @(Get-ChildItem -LiteralPath $sourceItem -File -Recurse)
    } else {
        @(Get-Item -LiteralPath $sourceItem)
    }
    foreach ($sourceFile in $sourceFiles) {
        $relative = $sourceFile.FullName.Substring($SourceRoot.Length).TrimStart([IO.Path]::DirectorySeparatorChar, [IO.Path]::AltDirectorySeparatorChar)
        $stageFile = Join-Path $StageRoot $relative
        if (-not (Test-Path -LiteralPath $stageFile -PathType Leaf)) {
            throw "Staged file missing during SHA-256 verification: $relative"
        }
        $sourceHash = (Get-FileHash -LiteralPath $sourceFile.FullName -Algorithm SHA256).Hash
        $stageHash = (Get-FileHash -LiteralPath $stageFile -Algorithm SHA256).Hash
        if ($sourceHash -ne $stageHash) {
            throw "Staged SHA-256 mismatch: $relative"
        }
    }
}

$versionPath = Join-Path $aiDir "COMPUTING_ENVIRONMENT_VERSION.md"
$installInfoPath = Join-Path $aiDir "INSTALLATION_INFO.md"
Assert-MetadataSafe $versionPath
Assert-MetadataSafe $installInfoPath
Assert-ManagedOrMissing $target ".ai/agent-project-kit snapshot"
Assert-ManagedOrMissing $previousTarget ".ai/agent-project-kit.previous snapshot"

$controlPaths = @(
    $versionPath,
    $installInfoPath,
    (Join-Path $aiDir "SESSION_LOG.md"),
    (Join-Path $project "AGENTS.md"),
    (Join-Path $project "CLAUDE.md"),
    (Join-Path $project "ANTIGRAVITY.md")
)
$controlBackup = Join-Path $aiDir (".agent-project-kit.control-backup." + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $controlBackup | Out-Null
for ($index = 0; $index -lt $controlPaths.Count; $index++) {
    $path = $controlPaths[$index]
    if (Test-Path -LiteralPath $path) {
        Copy-Item -LiteralPath $path -Destination (Join-Path $controlBackup ([string]$index)) -Recurse -Force
    }
}
$controlBackupReady = $true

$items = @(
    "manifest.json",
    "PACKAGE_CONTENTS.md",
    "CHANGELOG.md",
    "README.md",
    "README.th.md",
    "UPDATE_EXISTING_PROJECT.md",
    "INSTALL_IN_PROJECT.md",
    "index.md",
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
    "MARKDOWN_ORGANIZATION_POLICY.md",
    "SECURITY_EXCLUSIONS.md",
    "MIGRATION_FROM_OLD.md",
    "ENVIRONMENT_POLICY.md",
    "GLOBAL_START_PROMPT.md",
    "STARTUP.md",
    "SHARED_RUNTIME_EXPERIMENT.md",
    "bootstrap_ai_project.py",
    "prompts",
    "templates",
    "checklists",
    "config",
    "environments",
    "scripts"
)

$stage = Join-Path $aiDir (".agent-project-kit.stage." + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $stage | Out-Null
foreach ($item in $items) {
    $src = Join-Path $SourcePath $item
    $dst = Join-Path $stage $item
    if (-not (Test-Path -LiteralPath $src)) {
        throw "Missing required package item: $src"
    }
    Copy-Item -LiteralPath $src -Destination $dst -Recurse -Force
    Assert-StagedItemIntegrity -SourceRoot $SourcePath -StageRoot $stage -Item $item
}

if (-not (Test-ManagedSnapshot $stage) -or
    -not (Test-Path -LiteralPath (Join-Path $stage "STARTUP.md")) -or
    -not (Test-Path -LiteralPath (Join-Path $stage "scripts/context.py"))) {
    throw "Staged package validation failed: $stage"
}

if (Test-Path -LiteralPath $previousTarget) {
    if (Test-Path -LiteralPath $olderPreviousTarget) {
        Remove-Item -LiteralPath $olderPreviousTarget -Recurse -Force
    }
    Move-Item -LiteralPath $previousTarget -Destination $olderPreviousTarget
    $previousRotated = $true
}
if (Test-Path -LiteralPath $target) {
    $hadTarget = $true
    Move-Item -LiteralPath $target -Destination $previousTarget
}
Move-Item -LiteralPath $stage -Destination $target
$stage = ""
$snapshotSwapped = $true

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
Copy-TemplateIfMissing "project.json" "project.json"
Copy-TemplateIfMissing "state.json" "state.json"
Copy-TemplateIfMissing "local-resources.json" "local-resources.json"
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
- Update check cadence: report installed version every startup; check GitHub Pages manifest when last check is missing, older than 14 days, before package-level/release work, or when explicitly asked
- Last update check: not checked by installer
- Latest known upstream version: unknown
- Update check source: $SourcePath
- Source path: $SourcePath
- Installer: install-to-project.ps1
- Machine: $machine
- WSL2 detected: no / Windows PowerShell
- First install: $firstInstall
- Conda-family manager: $environmentManager

## Update Rule

If package version changes but machine profile schema version is unchanged,
reuse `.ai/MACHINE_PROFILE.md`; do not rerun first-use discovery unless
hostname/platform/path style changed.

Project-local state files are preserved by the installer. Update package
snapshots and missing template files without overwriting project-specific state.
On first install, same-name paths that do not look like Agent Project Kit
content are left untouched and the installer stops before writing kit-owned files.

## Update Check Rule

Every startup should report the installed Agent Project Kit package name and
version from this file. Do not fetch/pull package updates every time. Check the
GitHub Pages manifest with `scripts/update-from-pages.ps1 -DryRun` when
`Last update check` is missing/stale, before package-level or release work, or
when explicitly asked. Apply updates through `scripts/update-from-pages.ps1` so
project-local state is preserved.
"@
Set-Content -Path $versionPath -Value $versionInfo -Encoding UTF8

$installInfoPath = Join-Path $aiDir "INSTALLATION_INFO.md"

$installInfo = @"
# INSTALLATION_INFO

- Package version: $packageVersion
- State schema version: $stateSchema
- Machine profile schema version: $profileSchema
- Installed/updated: $(Get-Date -Format o)
- Project path: $project
- Agent Project Kit source: $SourcePath
- Machine detected: $machine
- WSL2 detected: no / Windows PowerShell
- First install: $firstInstall
- Conda-family manager: $environmentManager

Minimal startup (read other files only when STARTUP.md triggers them):

1. AGENTS.md
2. .ai/PROJECT_STATE.md
3. .ai/agent-project-kit/STARTUP.md
"@
Set-Content -Path $installInfoPath -Value $installInfo -Encoding UTF8

$projectAgents = Join-Path $project "AGENTS.md"
$managedBlock = "<!-- BEGIN COMPUTING-ENVIRONMENT -->"
$agentsBlock = @"
<!-- BEGIN COMPUTING-ENVIRONMENT -->
This project uses Agent Project Kit. On each request:

1. Read `.ai/PROJECT_STATE.md` and `.ai/agent-project-kit/STARTUP.md`.
2. Classify the task and load only the routed prompt/state files.
3. If the task is clear, proceed; ask one outcome question only when materially ambiguous.

Do not scan the managed snapshot or rerun onboarding, machine discovery, update
checks, or repository scans merely because a new session started. Follow the
cadence and run-once guidance in STARTUP.md. Keep L1 execution distinct from L2
human judgment and L3 external evidence.
<!-- END COMPUTING-ENVIRONMENT -->
"@

if (-not (Test-Path $projectAgents)) {
    Set-Content -Path $projectAgents -Value "# AGENTS.md`n`n$agentsBlock" -Encoding UTF8
} else {
    $existing = Get-Content $projectAgents -Raw
    if ($existing -match [regex]::Escape($managedBlock)) {
        $pattern = "(?s)" + [regex]::Escape($managedBlock) + ".*?" + [regex]::Escape("<!-- END COMPUTING-ENVIRONMENT -->")
        $updated = [regex]::Replace($existing, $pattern, $agentsBlock)
        Set-Content -Path $projectAgents -Value $updated -Encoding UTF8
    } else {
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
3. `.ai/agent-project-kit/STARTUP.md`

Classify the task, then load only the files routed by STARTUP.md.
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
$installLogMarker = "Agent Project Kit installation first recorded"
if ((Test-Path $sessionLog) -and -not (Select-String -Path $sessionLog -SimpleMatch $installLogMarker -Quiet)) {
    Add-Content -Path $sessionLog -Encoding UTF8 -Value @"

## $(Get-Date -Format yyyy-MM-dd) — $machine — $installLogMarker
- Objective: Install/update Agent Project Kit workflow files.
- Mode: T0 Quick
- Files touched: AGENTS.md, .ai/agent-project-kit/, .ai project templates if missing; existing user files with conflicting metadata/snapshot names are not overwritten
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

if (Test-Path -LiteralPath $olderPreviousTarget) {
    Remove-Item -LiteralPath $olderPreviousTarget -Recurse -Force
}
if (Test-Path -LiteralPath $controlBackup) {
    Remove-Item -LiteralPath $controlBackup -Recurse -Force
}
$controlBackupReady = $false
$snapshotSwapped = $false
