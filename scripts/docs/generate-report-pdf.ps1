# Generate PDF reports from Markdown (config: config/report.yaml).
# Uses Python script scripts/docs/generate-report-pdf.py.
#
# Usage (from project root):
#   .\scripts\docs\generate-report-pdf.ps1
#
# Or from any folder:
#   .\scripts\docs\generate-report-pdf.ps1

$ErrorActionPreference = "Stop"

$repoRoot = Join-Path $PSScriptRoot "..\.."
$scriptPy = Join-Path $PSScriptRoot "generate-report-pdf.py"

if (-not (Test-Path $scriptPy)) {
    Write-Host "Error: Python script not found: $scriptPy" -ForegroundColor Red
    exit 1
}

Push-Location $repoRoot
try {
    Write-Host "Generating report PDFs (config: config/report.yaml)..." -ForegroundColor Cyan
    python $scriptPy @args
    exit $LASTEXITCODE
} finally {
    Pop-Location
}
