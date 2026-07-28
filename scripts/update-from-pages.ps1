param(
    [switch]$DryRun,
    [Parameter(Position = 0)]
    [string]$ProjectPath = ".",
    [Parameter(Position = 1)]
    [string]$PagesManifestUrl = "https://punpiti.github.io/agent-project-kit/manifest.json",
    [Parameter(Position = 2)]
    [string]$RepoUrl = "https://github.com/punpiti/agent-project-kit.git",
    [Parameter(Position = 3)]
    [string]$Ref = "main",
    [Parameter(Position = 4)]
    [string]$CloneDir = ""
)

$ErrorActionPreference = "Stop"

$project = (Resolve-Path $ProjectPath).Path
$aiDir = Join-Path $project ".ai"
$versionFile = Join-Path $aiDir "COMPUTING_ENVIRONMENT_VERSION.md"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$installer = Join-Path $scriptDir "install-from-git.ps1"

if (-not (Test-Path $installer)) {
    throw "install-from-git.ps1 not found next to update-from-pages.ps1."
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

function Get-VersionKey {
    param([string]$Version)
    $main = ($Version -replace '^[vV]', '') -replace '[^0-9.].*$', ''
    $parts = @($main.Split("."))
    $major = if ($parts.Length -gt 0 -and $parts[0]) { [int]$parts[0] } else { 0 }
    $minor = if ($parts.Length -gt 1 -and $parts[1]) { [int]$parts[1] } else { 0 }
    $patch = if ($parts.Length -gt 2 -and $parts[2]) { [int]$parts[2] } else { 0 }
    return (($major * 1000000000000) + ($minor * 1000000) + $patch)
}

function Test-NewerOrDifferent {
    param(
        [string]$Current,
        [string]$Latest,
        [string]$CurrentUpdated,
        [string]$LatestUpdated
    )
    if (-not $Latest) { return $false }
    if ($Current -eq $Latest) { return $false }

    $currentKey = Get-VersionKey $Current
    $latestKey = Get-VersionKey $Latest
    if ($latestKey -gt $currentKey) { return $true }
    if ($latestKey -eq $currentKey -and $LatestUpdated -and $CurrentUpdated -and $LatestUpdated.CompareTo($CurrentUpdated) -gt 0) {
        return $true
    }
    return ($Current -ne $Latest)
}

New-Item -ItemType Directory -Force -Path $aiDir | Out-Null

$manifest = Invoke-RestMethod -Uri $PagesManifestUrl
$latestVersion = if ($manifest.version) { [string]$manifest.version } else { "unknown" }
$latestUpdated = if ($manifest.updated) { [string]$manifest.updated } else { "" }
$latestStateSchema = if ($manifest.state_schema_version) { [string]$manifest.state_schema_version } else { "unknown" }
$latestMachineSchema = if ($manifest.machine_profile_schema_version) { [string]$manifest.machine_profile_schema_version } else { "unknown" }

$currentVersion = Read-VersionLine $versionFile "Package version"
$currentUpdated = Read-VersionLine $versionFile "Package updated"
$currentStateSchema = Read-VersionLine $versionFile "State schema version"
$currentMachineSchema = Read-VersionLine $versionFile "Machine profile schema version"
if (-not $currentVersion) { $currentVersion = "none" }

Write-Host "Agent Project Kit GitHub Pages update check"
Write-Host "Project: $project"
Write-Host "Manifest: $PagesManifestUrl"
Write-Host "Repository: $RepoUrl"
Write-Host "Ref: $Ref"
Write-Host "Current package version: $currentVersion"
Write-Host "Latest package version: $latestVersion"
Write-Host "Current package updated: $(if ($currentUpdated) { $currentUpdated } else { 'unknown' })"
Write-Host "Latest package updated: $(if ($latestUpdated) { $latestUpdated } else { 'unknown' })"
Write-Host "Current state schema: $(if ($currentStateSchema) { $currentStateSchema } else { 'none' })"
Write-Host "Latest state schema: $latestStateSchema"
Write-Host "Current machine profile schema: $(if ($currentMachineSchema) { $currentMachineSchema } else { 'none' })"
Write-Host "Latest machine profile schema: $latestMachineSchema"

$hasUpdate = Test-NewerOrDifferent $currentVersion $latestVersion $currentUpdated $latestUpdated
if (-not $hasUpdate) {
    Write-Host "Result: no newer package version found."
    if (-not $DryRun -and (Test-Path $versionFile)) {
        $text = Get-Content $versionFile -Raw
        $text = $text -replace '(?m)^- Last update check:.*$', "- Last update check: $((Get-Date).ToString('o'))"
        $text = $text -replace '(?m)^- Latest known upstream version:.*$', "- Latest known upstream version: $latestVersion"
        $text = $text -replace '(?m)^- Update check source:.*$', "- Update check source: $PagesManifestUrl"
        Set-Content -Path $versionFile -Value $text -Encoding UTF8
    }
    exit 0
}

Write-Host "Result: newer or different package version found."
Write-Host "Project-local state files will be preserved by install-from-git."

if ($DryRun) {
    if ($CloneDir) {
        powershell -ExecutionPolicy Bypass -File $installer -DryRun -ProjectPath $project -RepoUrl $RepoUrl -Ref $Ref -CloneDir $CloneDir
    } else {
        powershell -ExecutionPolicy Bypass -File $installer -DryRun -ProjectPath $project -RepoUrl $RepoUrl -Ref $Ref
    }
    exit 0
}

if ($CloneDir) {
    powershell -ExecutionPolicy Bypass -File $installer -ProjectPath $project -RepoUrl $RepoUrl -Ref $Ref -CloneDir $CloneDir
} else {
    powershell -ExecutionPolicy Bypass -File $installer -ProjectPath $project -RepoUrl $RepoUrl -Ref $Ref
}

if (Test-Path $versionFile) {
    $text = Get-Content $versionFile -Raw
    $text = $text -replace '(?m)^- Last update check:.*$', "- Last update check: $((Get-Date).ToString('o'))"
    $text = $text -replace '(?m)^- Latest known upstream version:.*$', "- Latest known upstream version: $latestVersion"
    $text = $text -replace '(?m)^- Update check source:.*$', "- Update check source: $PagesManifestUrl"
    Set-Content -Path $versionFile -Value $text -Encoding UTF8
}
