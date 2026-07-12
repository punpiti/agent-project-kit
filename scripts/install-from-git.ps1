param(
    [switch]$DryRun,
    [Parameter(Position = 0)]
    [string]$ProjectPath = ".",
    [Parameter(Mandatory = $true, Position = 1)]
    [string]$RepoUrl,
    [Parameter(Position = 2)]
    [string]$Ref = "main",
    [Parameter(Position = 3)]
    [string]$CloneDir = ""
)

$ErrorActionPreference = "Stop"

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    throw "git not found. Install Git first."
}

$project = (Resolve-Path $ProjectPath).Path
$aiDir = Join-Path $project ".ai"
if (-not $CloneDir) {
    $CloneDir = Join-Path $aiDir "agent-project-kit"
}

New-Item -ItemType Directory -Force -Path $aiDir | Out-Null

if (Test-Path (Join-Path $CloneDir ".git")) {
    git -C $CloneDir remote set-url origin $RepoUrl
    git -C $CloneDir fetch --tags --prune origin
} else {
    if (Test-Path $CloneDir) { Remove-Item $CloneDir -Recurse -Force }
    git clone $RepoUrl $CloneDir
    git -C $CloneDir fetch --tags --prune origin
}

$tagExists = $false
try {
    git -C $CloneDir rev-parse -q --verify "refs/tags/$Ref" | Out-Null
    $tagExists = $true
} catch {
    $tagExists = $false
}

if ($tagExists) {
    git -C $CloneDir checkout -q "tags/$Ref"
} else {
    git -C $CloneDir checkout -q $Ref
    try { git -C $CloneDir pull --ff-only origin $Ref | Out-Null } catch {}
}

$commit = (git -C $CloneDir rev-parse --short=12 HEAD).Trim()

function Read-VersionLine {
    param([string]$Path, [string]$Label)
    if (-not (Test-Path $Path)) { return "" }
    $prefix = "- ${Label}:"
    foreach ($line in Get-Content $Path) {
        if ($line.StartsWith($prefix)) {
            return $line.Substring($prefix.Length).Trim()
        }
    }
    return ""
}

if ($DryRun) {
    $versionFile = Join-Path $aiDir "COMPUTING_ENVIRONMENT_VERSION.md"
    $manifestPath = Join-Path $CloneDir "manifest.json"
    $targetPackageVersion = "unknown"
    $targetStateSchema = "unknown"
    $targetMachineSchema = "unknown"
    if (Test-Path $manifestPath) {
        $manifest = Get-Content $manifestPath -Raw | ConvertFrom-Json
        if ($manifest.version) { $targetPackageVersion = [string]$manifest.version }
        if ($manifest.state_schema_version) { $targetStateSchema = [string]$manifest.state_schema_version }
        if ($manifest.machine_profile_schema_version) { $targetMachineSchema = [string]$manifest.machine_profile_schema_version }
    }

    Write-Host "Agent Project Kit update dry run"
    Write-Host "Project: $project"
    Write-Host "Repository: $RepoUrl"
    Write-Host "Ref: $Ref"
    Write-Host "Commit: $commit"
    Write-Host "Clone path: $CloneDir"
    Write-Host "Snapshot path that would be refreshed: $(Join-Path $aiDir 'computing-environment')"
    Write-Host "Current package version: $(Read-VersionLine $versionFile 'Package version')"
    Write-Host "Target package version: $targetPackageVersion"
    Write-Host "Current state schema: $(Read-VersionLine $versionFile 'State schema version')"
    Write-Host "Target state schema: $targetStateSchema"
    Write-Host "Current machine profile schema: $(Read-VersionLine $versionFile 'Machine profile schema version')"
    Write-Host "Target machine profile schema: $targetMachineSchema"
    Write-Host "Project-local state files would be preserved."
    Write-Host "No project files were updated."
    exit 0
}

powershell -ExecutionPolicy Bypass -File (Join-Path $CloneDir "scripts/install-to-project.ps1") -ProjectPath $project -SourcePath $CloneDir

$versionFile = Join-Path $aiDir "COMPUTING_ENVIRONMENT_VERSION.md"
if (Test-Path $versionFile) {
    Add-Content -Path $versionFile -Encoding UTF8 -Value @"

## Git Source

- Source type: git
- Repository: $RepoUrl
- Ref: $Ref
- Commit: $commit
- Clone path: $CloneDir
"@
}

Write-Host "Agent Project Kit cloned at: $CloneDir"
Write-Host "Installed into project: $project"
Write-Host "Ref: $Ref"
Write-Host "Commit: $commit"
