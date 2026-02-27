# Generate PDF reports from Markdown. Delegates to scripts/docs/generate-report-pdf.ps1.
# Usage (from project root): .\scripts\generate-report-pdf.ps1
$ErrorActionPreference = "Stop"
$scriptDir = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
$ps1 = Join-Path $scriptDir "docs\generate-report-pdf.ps1"
if (-not (Test-Path $ps1)) {
    Write-Error "Script not found: $ps1"
    exit 1
}
& $ps1 @args
exit $LASTEXITCODE
