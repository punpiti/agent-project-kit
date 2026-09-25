# Install Agent Project Kit into a project from a Git ref.
# Thin wrapper: the core is scripts/apk_update.py (Python 3.8+).
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
. (Join-Path $PSScriptRoot "apk-python.ps1")
$arguments = @((Join-Path $PSScriptRoot "apk_update.py"), "from-git")
if ($DryRun) { $arguments += "--dry-run" }
$arguments += @($ProjectPath, $RepoUrl, $Ref, $CloneDir, $ExpectedVersion)
exit (Invoke-ApkPython $arguments)
