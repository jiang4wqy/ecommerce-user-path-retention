param(
    [switch]$RefreshData
)

$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot

function Resolve-ProjectPython {
    $bundled = "C:\Users\lenovo\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
    if (Test-Path $bundled) {
        return $bundled
    }

    $candidate = Get-Command python -ErrorAction SilentlyContinue
    if ($candidate) {
        return $candidate.Source
    }

    throw "Python was not found. Install Python 3.10+ and run: pip install -r requirements.txt"
}

function Clear-GeneratedPythonFiles {
    $projectRoot = (Resolve-Path $PSScriptRoot).Path
    $projectRootPrefix = $projectRoot.TrimEnd("\") + "\"
    Get-ChildItem -Path $projectRoot -Recurse -Directory -Filter "__pycache__" | ForEach-Object {
        if (-not $_.FullName.StartsWith($projectRootPrefix, [StringComparison]::OrdinalIgnoreCase)) {
            throw "Refusing to remove path outside project: $($_.FullName)"
        }
        Remove-Item -LiteralPath $_.FullName -Recurse -Force
    }
    Get-ChildItem -Path $projectRoot -Recurse -File -Include "*.pyc", "*.pyo", "*.pyd", "*.log" | ForEach-Object {
        if (-not $_.FullName.StartsWith($projectRootPrefix, [StringComparison]::OrdinalIgnoreCase)) {
            throw "Refusing to remove path outside project: $($_.FullName)"
        }
        Remove-Item -LiteralPath $_.FullName -Force
    }
    if (Test-Path ".pytest_cache") {
        $pytestCache = (Resolve-Path ".pytest_cache").Path
        if (-not $pytestCache.StartsWith($projectRootPrefix, [StringComparison]::OrdinalIgnoreCase)) {
            throw "Refusing to remove path outside project: $pytestCache"
        }
        Remove-Item -LiteralPath $pytestCache -Recurse -Force
    }
}

if (Test-Path "C:\tmp") {
    $env:TMP = "C:\tmp"
    $env:TEMP = "C:\tmp"
}

$env:PYTHONDONTWRITEBYTECODE = "1"
$python = Resolve-ProjectPython
$sampleCsv = Join-Path $PSScriptRoot "data\processed\events_sample.csv"
$sampleParquet = Join-Path $PSScriptRoot "data\processed\events_sample.parquet"

function Invoke-PythonModule {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$Arguments
    )

    & $python @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Python command failed: $python $($Arguments -join ' ')"
    }
}

if ($RefreshData -or -not (Test-Path $sampleCsv)) {
    Invoke-PythonModule -Arguments @("-m", "src.prepare_data", "--rows", "6000")
}
elseif (-not (Test-Path $sampleParquet)) {
    Invoke-PythonModule -Arguments @("-m", "src.prepare_data", "--source", $sampleCsv, "--rows", "6000")
}
else {
    Write-Host "Using existing real public sample. Pass -RefreshData to download fresh rows."
}

Invoke-PythonModule -Arguments @("-m", "src.build_database")
Invoke-PythonModule -Arguments @("-m", "src.export_outputs")
Invoke-PythonModule -Arguments @("-m", "pytest", "-q", "-p", "no:cacheprovider")
Clear-GeneratedPythonFiles
Invoke-PythonModule -Arguments @("-m", "src.project_audit")
