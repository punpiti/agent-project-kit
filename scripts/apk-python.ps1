# Dot-sourced by the Agent Project Kit PowerShell wrappers.
function Find-ApkPython {
    # The Windows py launcher first; "python" may be the Microsoft Store stub,
    # which only opens the Store, so every candidate must actually run.
    foreach ($candidate in @(@("py", "-3"), @("python3"), @("python"))) {
        $command = Get-Command $candidate[0] -ErrorAction SilentlyContinue
        if (-not $command) { continue }
        $arguments = @($candidate | Select-Object -Skip 1)
        & $command.Source @arguments -c "import sys; sys.exit(sys.version_info < (3, 9))" 2>$null
        if ($LASTEXITCODE -eq 0) { return @($command.Source) + $arguments }
    }
    throw "Agent Project Kit needs Python 3.9 or newer. Install it from https://www.python.org/downloads/ (the Python install manager provides 'py')."
}

function Invoke-ApkPython {
    param([string[]]$Arguments)
    # @() keeps a single-element result (e.g. /usr/bin/python3) an array.
    $python = @(Find-ApkPython)
    $prefix = @($python | Select-Object -Skip 1)
    # Python reports progress and failures on stderr; Windows PowerShell 5.1
    # would turn that into a terminating error under "Stop".
    $ErrorActionPreference = "Continue"
    # Out-Host keeps Python's output on screen instead of in the return value.
    & $python[0] @prefix -B @Arguments | Out-Host
    return $LASTEXITCODE
}
