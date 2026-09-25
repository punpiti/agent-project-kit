param(
    [string]$SourcePath = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
)

$ErrorActionPreference = "Stop"
$testRoot = Join-Path $env:TEMP ("apk shared v2 windows " + [guid]::NewGuid().ToString("N"))
$sharedRoot = Join-Path $testRoot "synced generic package"
$machineHome = Join-Path $testRoot "machine local state"
$project = Join-Path $testRoot "self host project"

function Invoke-Python {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Arguments)
    & py -3 @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Python command failed with exit code ${LASTEXITCODE}: $Arguments"
    }
}

try {
    New-Item -ItemType Directory -Force -Path $project | Out-Null
    & (Join-Path $SourcePath "scripts\install-to-project.ps1") `
        -ProjectPath $project -SourcePath $SourcePath

    # An injected failure while activating the stage must restore the active
    # snapshot (Windows holds handles on just-renamed folders; see apk_install.py).
    $startup = Join-Path $project ".ai\agent-project-kit\STARTUP.md"
    $before = (Get-FileHash -LiteralPath $startup -Algorithm SHA256).Hash
    $env:APK_INSTALL_TEST_FAULT = "activate"
    # PowerShell 5.1 turns native stderr into a terminating error under Stop.
    $ErrorActionPreference = "Continue"
    try {
        & (Join-Path $SourcePath "scripts\install-to-project.ps1") -ProjectPath $project -SourcePath $SourcePath 2>&1 | Out-Null
        $faultExit = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = "Stop"
        Remove-Item Env:APK_INSTALL_TEST_FAULT -ErrorAction SilentlyContinue
    }
    if ($faultExit -eq 0) { throw "Injected install failure unexpectedly succeeded" }
    if (-not (Test-Path -LiteralPath $startup) -or (Get-FileHash -LiteralPath $startup -Algorithm SHA256).Hash -ne $before) {
        throw "Rollback did not restore the active snapshot"
    }
    if (Get-ChildItem -LiteralPath (Join-Path $project ".ai") -Force -Filter ".agent-project-kit.*") {
        throw "Rollback left staging or control-backup folders"
    }

    $statePath = Join-Path $project ".ai\PROJECT_STATE.md"
    Add-Content -Path $statePath -Value "`nAPK_WINDOWS_PROJECT_SECRET_81d7a4"

    Invoke-Python (Join-Path $SourcePath "scripts\install-shared.py") `
        --source $SourcePath --shared-root $sharedRoot `
        --machine-home $machineHome --bind-project $project

    $bindingPath = Join-Path $project ".ai\apk.json"
    $binding = Get-Content $bindingPath -Raw | ConvertFrom-Json
    if ($binding.schema_version -ne 2) { throw "Expected schema-v2 binding" }
    if ($binding.PSObject.Properties.Name -contains "shared_root") {
        throw "Project binding leaked the physical shared root"
    }

    $runtime = Join-Path $sharedRoot ("versions\" + $binding.version)
    $leak = Get-ChildItem -File -Recurse $runtime | Select-String `
        -SimpleMatch "APK_WINDOWS_PROJECT_SECRET_81d7a4" -ErrorAction SilentlyContinue
    if ($leak) { throw "Project content leaked into the shared runtime" }

    $env:APK_MACHINE_HOME = $machineHome
    $launcher = Join-Path $machineHome "bin\apk"
    $resolvePath = Join-Path $testRoot "resolve.json"
    $contextPath = Join-Path $testRoot "context.json"
    Invoke-Python $launcher --project $project resolve | Set-Content -Path $resolvePath
    Invoke-Python $launcher --project $project context `
        "fix the media importer Python code" --output $contextPath
    $context = Get-Content $contextPath -Raw | ConvertFrom-Json
    if ($context.routing.domain -ne "software") { throw "Unexpected shared route" }
    if (Get-ChildItem -Directory -Recurse -Force $runtime -Filter "__pycache__") {
        throw "Running the shared runtime wrote bytecode into it"
    }

    # Thai output through a pipe must not fail on the Windows console codepage.
    # Build the request from code points: this file has no BOM, so Windows
    # PowerShell 5.1 would misread a literal Thai string.
    $thaiRequest = -join ([char[]]@(0x0E40,0x0E02,0x0E35,0x0E22,0x0E19,0x0E2B,0x0E19,0x0E31,0x0E07,0x0E2A,0x0E37,0x0E2D,0x0E23,0x0E32,0x0E0A,0x0E01,0x0E32,0x0E23,0x0E16,0x0E36,0x0E07,0x0E04,0x0E13,0x0E30))
    $savedEncoding = [Console]::OutputEncoding
    try {
        [Console]::OutputEncoding = [Text.UTF8Encoding]::new($false)
        $thaiRoute = (Invoke-Python -B (Join-Path $runtime "scripts\route_task.py") $thaiRequest) -join "`n"
    } finally {
        [Console]::OutputEncoding = $savedEncoding
    }
    if (($thaiRoute | ConvertFrom-Json).primary_pipeline -ne "administrative-professional-operations") {
        throw "Unexpected Thai route on Windows"
    }

    Invoke-Python $launcher --project $project rollback
    $disabled = Join-Path $project ".ai\apk.json.disabled"
    if ((Test-Path $bindingPath) -or -not (Test-Path $disabled)) {
        throw "Rollback did not disable the project binding"
    }

    $snapshotContext = Join-Path $testRoot "snapshot-context.json"
    Invoke-Python (Join-Path $project ".ai\agent-project-kit\scripts\context.py") `
        --project $project "fix the media importer Python code" --output $snapshotContext
    Move-Item -LiteralPath $disabled -Destination $bindingPath
    Invoke-Python $launcher --project $project resolve | Out-Null

    Write-Output "shared runtime v2 native Windows tests: PASS"
}
finally {
    Remove-Item Env:APK_MACHINE_HOME -ErrorAction SilentlyContinue
    if (Test-Path $testRoot) { Remove-Item -LiteralPath $testRoot -Recurse -Force }
}
