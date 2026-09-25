# Install or update Agent Project Kit in a project.
# Thin wrapper: the installer core is scripts/apk_install.py (Python 3.8+).
#   .\install-to-project.ps1 -ProjectPath C:\path\to\project -SourcePath C:\path\to\agent-project-kit
param(
    [string]$ProjectPath = ".",
    [string]$SourcePath = ""
)

$ErrorActionPreference = "Stop"

function Find-Python {
    # The Windows py launcher first; "python" may be the Microsoft Store stub,
    # which only opens the Store, so every candidate must actually run.
    foreach ($candidate in @(@("py", "-3"), @("python3"), @("python"))) {
        $command = Get-Command $candidate[0] -ErrorAction SilentlyContinue
        if (-not $command) { continue }
        $arguments = @($candidate | Select-Object -Skip 1)
        & $command.Source @arguments -c "import sys; sys.exit(sys.version_info < (3, 8))" 2>$null
        if ($LASTEXITCODE -eq 0) { return @($command.Source) + $arguments }
    }
    throw "Agent Project Kit needs Python 3.8 or newer. Install it from https://www.python.org/downloads/ (the Python install manager provides 'py')."
}

$python = Find-Python
$pythonArgs = @($python | Select-Object -Skip 1)
$core = Join-Path $PSScriptRoot "apk_install.py"
$installArgs = @("-B", $core, $ProjectPath)
if ($SourcePath) { $installArgs += $SourcePath }
# Python reports progress and failures on stderr; Windows PowerShell 5.1 would
# turn that into a terminating error under "Stop", so pass it through as-is.
$ErrorActionPreference = "Continue"
& $python[0] @pythonArgs @installArgs --installer-name install-to-project.ps1
exit $LASTEXITCODE
