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
