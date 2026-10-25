[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$StageDirectory,
    [Parameter(Mandatory = $true)][string]$InstallerPath,
    [Parameter(Mandatory = $true)][ValidatePattern('^\d+\.\d+\.\d+$')][string]$Version,
    [Parameter(Mandatory = $true)][ValidateSet("x64", "arm64")][string]$Architecture
)

$ErrorActionPreference = "Stop"
$stage = (Resolve-Path -LiteralPath $StageDirectory).Path
$installer = (Resolve-Path -LiteralPath $InstallerPath).Path
$application = Join-Path $stage "LeoMoon QuickCrypt.exe"
if (-not (Test-Path -LiteralPath $application -PathType Leaf)) { throw "Expected application executable was not found: $application" }
if ((Split-Path -Leaf $installer) -ne "leomoon-quickcrypt-$Version-windows-$Architecture-setup.exe") { throw "Installer filename does not match the requested version and architecture" }

foreach ($forbidden in @("msvcp100.dll", "msvcr100.dll", "istask.dll")) {
    if (Get-ChildItem -LiteralPath $stage -Recurse -File -Filter $forbidden) { throw "Obsolete binary is present in the staged application: $forbidden" }
}

& (Join-Path $PSScriptRoot "verify-windows-build.ps1") -ApplicationPath $application -Architecture $Architecture
Write-Host "Verified $installer"
