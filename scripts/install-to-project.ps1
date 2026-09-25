# Install or update Agent Project Kit in a project.
# Thin wrapper: the installer core is scripts/apk_install.py (Python 3.8+).
#   .\install-to-project.ps1 -ProjectPath C:\path\to\project -SourcePath C:\path\to\agent-project-kit
param(
    [string]$ProjectPath = ".",
    [string]$SourcePath = ""
)
$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "apk-python.ps1")
$arguments = @((Join-Path $PSScriptRoot "apk_install.py"), $ProjectPath)
if ($SourcePath) { $arguments += $SourcePath }
exit (Invoke-ApkPython ($arguments + @("--installer-name", "install-to-project.ps1")))
