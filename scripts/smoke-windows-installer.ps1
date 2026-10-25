[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$ArtifactDirectory,
    [Parameter(Mandatory = $true)][ValidatePattern('^\d+\.\d+\.\d+$')][string]$Version,
    [ValidateSet("x64", "arm64")][string]$Architecture = "x64"
)

$ErrorActionPreference = "Stop"
$artifacts = (Resolve-Path -LiteralPath $ArtifactDirectory).Path
$installer = Join-Path $artifacts "leomoon-quickcrypt-$Version-windows-$Architecture-setup.exe"
$checksums = Join-Path $artifacts "SHA256SUMS"
if (-not (Test-Path -LiteralPath $installer -PathType Leaf)) { throw "Windows installer is missing" }
if (-not (Test-Path -LiteralPath $checksums -PathType Leaf)) { throw "SHA256SUMS is missing" }
foreach ($line in Get-Content -LiteralPath $checksums) {
    if ($line -notmatch '^([0-9a-f]{64}) \*(.+)$') { throw "Invalid SHA256SUMS entry: $line" }
    $actual = (Get-FileHash -LiteralPath (Join-Path $artifacts $Matches[2]) -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($actual -ne $Matches[1]) { throw "Checksum mismatch for $($Matches[2])" }
}

function Invoke-CheckedProcess([string]$FilePath, [string[]]$Arguments, [int]$TimeoutSeconds = 60) {
    $process = Start-Process -FilePath $FilePath -ArgumentList $Arguments -PassThru
    if (-not $process.WaitForExit($TimeoutSeconds * 1000)) {
        $process.Kill($true)
        throw "$FilePath did not finish within $TimeoutSeconds seconds"
    }
    if ($process.ExitCode -ne 0) { throw "$FilePath failed with exit code $($process.ExitCode)" }
}

function Assert-RegistryValue([string]$Path, [string]$Expected) {
    if (-not (Test-Path -LiteralPath $Path)) { throw "Registry key is missing: $Path" }
    $actual = (Get-Item -LiteralPath $Path).GetValue("")
    if ($actual -ne $Expected) { throw "Registry value mismatch at $Path" }
}

$testRoot = Join-Path $env:RUNNER_TEMP "leomoon-quickcrypt-windows-installer-smoke"
$installDirectory = Join-Path $testRoot "application"
$installLog = Join-Path $env:RUNNER_TEMP "leomoon-quickcrypt-install.log"
$uninstallLog = Join-Path $env:RUNNER_TEMP "leomoon-quickcrypt-uninstall.log"
$classes = "Registry::HKEY_CURRENT_USER\Software\Classes"
$progId = "LeoMoon.QuickCrypt.aes"
try {
    Remove-Item -LiteralPath $testRoot -Recurse -Force -ErrorAction SilentlyContinue
    New-Item -ItemType Directory -Path $testRoot | Out-Null
    $installArguments = @("/SP-", "/VERYSILENT", "/SUPPRESSMSGBOXES", "/NORESTART", "/LOG=`"$installLog`"", "/DIR=`"$installDirectory`"")
    Invoke-CheckedProcess $installer $installArguments 600
    $application = Join-Path $installDirectory "LeoMoon QuickCrypt.exe"
    if (-not (Test-Path -LiteralPath $application -PathType Leaf)) { throw "Installed application is missing" }
    & (Join-Path $PSScriptRoot "verify-windows-build.ps1") -ApplicationPath $application -Architecture $Architecture
    if (Get-ChildItem -LiteralPath $installDirectory -Recurse -File -Include msvcp100.dll,msvcr100.dll,istask.dll) { throw "Installer deployed an obsolete binary" }

    Assert-RegistryValue "$classes\.aes" $progId
    Assert-RegistryValue "$classes\$progId\shell\open\command" "`"$application`" -d `"%1`""
    Assert-RegistryValue "$classes\*\shell\LeoMoonQuickCryptEncrypt\command" "`"$application`" -e `"%1`""
    Assert-RegistryValue "$classes\$progId\shell\LeoMoonQuickCryptDecrypt\command" "`"$application`" -d `"%1`""

    $spacedFile = Join-Path $testRoot "file with spaces.txt"
    Set-Content -LiteralPath $spacedFile -Value "QuickCrypt smoke input" -Encoding utf8NoBOM
    $launch = Start-Process -FilePath $application -ArgumentList @("-e", "`"$spacedFile`"") -PassThru
    Start-Sleep -Seconds 3
    if ($launch.HasExited) { throw "Installed application did not launch with an encrypt context-menu argument" }
    $launch.Kill($true)

    Invoke-CheckedProcess $installer $installArguments 600
    $uninstaller = Join-Path $installDirectory "unins000.exe"
    if (-not (Test-Path -LiteralPath $uninstaller -PathType Leaf)) { throw "Windows uninstaller is missing" }
    Invoke-CheckedProcess $uninstaller @("/VERYSILENT", "/SUPPRESSMSGBOXES", "/NORESTART", "/LOG=`"$uninstallLog`"") 600
    $deadline = [DateTime]::UtcNow.AddSeconds(60)
    while (Test-Path -LiteralPath $installDirectory) {
        if ([DateTime]::UtcNow -ge $deadline) { throw "Application directory remains after uninstall" }
        Start-Sleep -Milliseconds 200
    }
    foreach ($path in @("$classes\.aes", "$classes\$progId", "$classes\*\shell\LeoMoonQuickCryptEncrypt")) {
        if (Test-Path -LiteralPath $path) { throw "Registry key remains after uninstall: $path" }
    }
} finally {
    Remove-Item -LiteralPath $testRoot -Recurse -Force -ErrorAction SilentlyContinue
}

Write-Host "Windows installer install, upgrade, registry, launch, and uninstall checks passed"
