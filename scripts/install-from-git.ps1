param(
    [switch]$DryRun,
    [Parameter(Position = 0)]
    [string]$ProjectPath = ".",
    [Parameter(Mandatory = $true, Position = 1)]
    [string]$RepoUrl,
    [Parameter(Position = 2)]
    [string]$Ref = "main",
    [Parameter(Position = 3)]
    [string]$CloneDir = "",
    [string]$ExpectedVersion = ""
)

$ErrorActionPreference = "Stop"
$hostExecutable = (Get-Process -Id $PID).Path

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    throw "git not found. Install Git first."
}

$project = (Resolve-Path $ProjectPath).Path
$aiDir = Join-Path $project ".ai"
if (-not $CloneDir) {
    $CloneDir = Join-Path $aiDir "agent-project-kit-source"
}

New-Item -ItemType Directory -Force -Path $aiDir | Out-Null

if (Test-Path (Join-Path $CloneDir ".git")) {
    git -C $CloneDir remote set-url origin $RepoUrl
    if ($LASTEXITCODE -ne 0) { throw "Could not set git remote for $CloneDir" }
    git -C $CloneDir fetch --tags --prune origin
    if ($LASTEXITCODE -ne 0) { throw "Could not fetch Agent Project Kit from $RepoUrl" }
} else {
    if (Test-Path $CloneDir) {
        throw "Refusing to overwrite existing non-git clone path: $CloneDir. Move or rename it first, or pass a different CloneDir argument."
    }
    git clone $RepoUrl $CloneDir
    if ($LASTEXITCODE -ne 0) { throw "Could not clone Agent Project Kit from $RepoUrl" }
    git -C $CloneDir fetch --tags --prune origin
    if ($LASTEXITCODE -ne 0) { throw "Could not fetch Agent Project Kit tags from $RepoUrl" }
}

git -C $CloneDir rev-parse -q --verify "refs/tags/$Ref" | Out-Null
$tagExists = ($LASTEXITCODE -eq 0)

if ($tagExists) {
    git -C $CloneDir checkout -q "tags/$Ref"
    if ($LASTEXITCODE -ne 0) { throw "Could not check out tag $Ref" }
} else {
    git -C $CloneDir checkout -q $Ref
    if ($LASTEXITCODE -ne 0) { throw "Could not check out ref $Ref" }
    try { git -C $CloneDir pull --ff-only origin $Ref | Out-Null } catch {}
}

$commit = (git -C $CloneDir rev-parse --short=12 HEAD).Trim()
if ($LASTEXITCODE -ne 0) { throw "Could not resolve checked-out commit for $Ref" }

$checkedOutManifestPath = Join-Path $CloneDir "manifest.json"
$checkedOutVersion = ""
if (Test-Path $checkedOutManifestPath) {
    $checkedOutManifest = Get-Content $checkedOutManifestPath -Raw | ConvertFrom-Json
    if ($checkedOutManifest.version) { $checkedOutVersion = [string]$checkedOutManifest.version }
}
if ($ExpectedVersion -and $checkedOutVersion -ne $ExpectedVersion) {
    throw "Refusing package version mismatch: manifest advertised $ExpectedVersion but ref $Ref contains $(if ($checkedOutVersion) { $checkedOutVersion } else { 'unknown' })."
}

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
    Write-Host "Snapshot path that would be refreshed: $(Join-Path $aiDir 'agent-project-kit')"
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

& $hostExecutable -NoProfile -ExecutionPolicy Bypass -File (Join-Path $CloneDir "scripts/install-to-project.ps1") -ProjectPath $project -SourcePath $CloneDir
if ($LASTEXITCODE -ne 0) { throw "Agent Project Kit transactional installer failed." }

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
