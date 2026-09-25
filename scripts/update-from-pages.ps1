# Update Agent Project Kit from the published GitHub Pages manifest.
# Thin wrapper: the core is scripts/apk_update.py (Python 3.9+).
param(
    [switch]$DryRun,
    [Parameter(Position = 0)]
    [string]$ProjectPath = ".",
    [Parameter(Position = 1)]
    [string]$PagesManifestUrl = "https://punpiti.github.io/agent-project-kit/manifest.json",
    [Parameter(Position = 2)]
    [string]$RepoUrl = "https://github.com/punpiti/agent-project-kit.git",
    [Parameter(Position = 3)]
    [string]$Ref = "",
    [Parameter(Position = 4)]
    [string]$CloneDir = ""
)
$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "apk-python.ps1")
$arguments = @((Join-Path $PSScriptRoot "apk_update.py"), "from-pages")
if ($DryRun) { $arguments += "--dry-run" }
$arguments += @($ProjectPath, $PagesManifestUrl, $RepoUrl, $Ref, $CloneDir)
exit (Invoke-ApkPython $arguments)
