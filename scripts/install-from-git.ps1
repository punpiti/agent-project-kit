param(
    [string]$ProjectPath = ".",
    [Parameter(Mandatory = $true)][string]$RepoUrl,
    [string]$Ref = "main",
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
