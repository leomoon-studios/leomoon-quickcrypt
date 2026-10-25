[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$StageDirectory,
    [Parameter(Mandatory = $true)][string]$DistDirectory,
    [Parameter(Mandatory = $true)][ValidatePattern('^\d+\.\d+\.\d+$')][string]$Version,
    [Parameter(Mandatory = $true)][ValidatePattern('^\d{4}-\d{2}-\d{2}T')][string]$ReleaseDate,
    [Parameter(Mandatory = $true)][ValidatePattern('^[0-9a-fA-F]{7,64}$')][string]$Commit,
    [ValidateSet("x64", "arm64")][string]$Architecture = "x64",
    [string]$IsccPath = ""
)

$ErrorActionPreference = "Stop"
$repoDirectory = Split-Path -Parent $PSScriptRoot
$sourceStage = (Resolve-Path -LiteralPath $StageDirectory).Path
if (-not (Test-Path -LiteralPath (Join-Path $sourceStage "LeoMoon QuickCrypt.exe") -PathType Leaf)) { throw "StageDirectory must contain LeoMoon QuickCrypt.exe" }

if (-not $IsccPath) {
    $command = Get-Command ISCC.exe -ErrorAction SilentlyContinue
    $IsccPath = if ($command) { $command.Source } else { "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" }
}
if (-not (Test-Path -LiteralPath $IsccPath -PathType Leaf)) { throw "Inno Setup compiler was not found at $IsccPath" }

$packageDirectory = Join-Path $repoDirectory "build\package\windows"
$stage = Join-Path $packageDirectory "stage"
$installerScript = Join-Path $repoDirectory "packaging\windows\quickcrypt.iss"
Remove-Item -LiteralPath $packageDirectory -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path $stage -Force | Out-Null
Copy-Item -Path (Join-Path $sourceStage "*") -Destination $stage -Recurse -Force
New-Item -ItemType Directory -Path (Join-Path $stage "licenses") -Force | Out-Null
Copy-Item -LiteralPath (Join-Path $repoDirectory "THIRD_PARTY_NOTICES.md") -Destination (Join-Path $stage "licenses\THIRD_PARTY_NOTICES.md")

& $IsccPath "/Qp" "/DAppVersion=$Version" "/DAppArchitecture=$Architecture" "/DStageDir=$stage" "/DOutputDir=$packageDirectory" $installerScript
if ($LASTEXITCODE -ne 0) { throw "Inno Setup failed with exit code $LASTEXITCODE" }
$installer = Join-Path $packageDirectory "leomoon-quickcrypt-$Version-windows-$Architecture-setup.exe"
& (Join-Path $PSScriptRoot "verify-windows-package.ps1") -StageDirectory $stage -InstallerPath $installer -Version $Version -Architecture $Architecture

$dist = [System.IO.Path]::GetFullPath($DistDirectory)
if ($dist -eq [System.IO.Path]::GetPathRoot($dist) -or $dist -eq $repoDirectory) { throw "Refusing to replace unsafe artifact directory: $dist" }
if (Test-Path -LiteralPath $dist) { Remove-Item -LiteralPath $dist -Recurse -Force }
New-Item -ItemType Directory -Path $dist | Out-Null
Copy-Item -LiteralPath $installer -Destination $dist

$manifest = [ordered]@{ application = "LeoMoon QuickCrypt"; version = $Version; releaseDate = $ReleaseDate; commit = $Commit; platform = "windows"; architecture = $Architecture; format = "Inno Setup" }
$manifest | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $dist "release-manifest.json") -Encoding utf8NoBOM
Get-ChildItem -LiteralPath $dist -File | Sort-Object Name | ForEach-Object { "{0} *{1}" -f (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant(), $_.Name } | Set-Content -LiteralPath (Join-Path $dist "SHA256SUMS") -Encoding ascii
Write-Host "Windows release artifacts are ready in $dist"
