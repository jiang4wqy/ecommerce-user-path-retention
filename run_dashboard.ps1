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

if (Test-Path "C:\tmp") {
    $env:TMP = "C:\tmp"
    $env:TEMP = "C:\tmp"
}

$env:PYTHONDONTWRITEBYTECODE = "1"
$python = Resolve-ProjectPython
& $python -m streamlit run app/dashboard.py
