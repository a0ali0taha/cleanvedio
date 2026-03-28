param(
    [string]$OutDir = "portable\CleanVedioPortable",
    [ValidateSet("full", "lean")]
    [string]$BundleMode = "full",
    [string]$FfmpegBin = "",
    [string]$SpleeterRoot = "",
    [string]$EmRoot = ""
)

$ErrorActionPreference = "Stop"
$ScriptRoot = $PSScriptRoot
Set-Location $ScriptRoot

function Copy-IfExists($src, $dst) {
    if (Test-Path $src) {
        Copy-Item -Path $src -Destination $dst -Recurse -Force
        return $true
    }
    return $false
}

function Test-CommandInPath {
    param(
        [string]$CommandName,
        [string]$PathPrefix
    )
    $oldPath = $env:PATH
    try {
        $env:PATH = "$PathPrefix;$oldPath"
        $cmd = Get-Command $CommandName -ErrorAction SilentlyContinue
        if (-not $cmd) { return $false }
        if ($CommandName -ieq "ffmpeg") {
            & $cmd.Source -version *> $null
        } else {
            & $cmd.Source --help *> $null
        }
        return $LASTEXITCODE -eq 0
    } catch {
        return $false
    } finally {
        $env:PATH = $oldPath
    }
}

function Resolve-FfmpegBin {
    param([string]$Provided)
    if ($Provided -and (Test-Path $Provided)) { return $Provided }
    $ffmpegCmd = Get-Command ffmpeg -ErrorAction SilentlyContinue
    if ($ffmpegCmd) { return (Split-Path $ffmpegCmd.Source -Parent) }
    return $null
}

function Resolve-SpleeterRoot {
    param([string]$Provided)
    if ($Provided -and (Test-Path $Provided)) { return $Provided }
    $spleeterCmd = Get-Command spleeter -ErrorAction SilentlyContinue
    if (-not $spleeterCmd) { return $null }

    $cmdPath = $spleeterCmd.Source
    $parent = Split-Path $cmdPath -Parent
    $leaf = Split-Path $parent -Leaf

    if ($leaf -ieq "Scripts" -or $leaf -ieq "bin") {
        return (Split-Path $parent -Parent)
    }
    return $parent
}

function Resolve-EmRoot {
    param([string]$Provided)
    if ($Provided -and (Test-Path $Provided)) { return $Provided }
    $candidates = @(
        (Join-Path $ScriptRoot "em-runtime"),
        (Join-Path $ScriptRoot "runtime\em"),
        "C:\Program Files\Em"
    )
    foreach ($candidate in $candidates) {
        if (Test-Path $candidate) { return $candidate }
    }
    return $null
}

$distExe = Join-Path $ScriptRoot "dist\CleanVedio.exe"
if (-not (Test-Path $distExe)) {
    throw "Build missing: $distExe. Run .\build_windows.ps1 -Clean first."
}

$bundleDir = Join-Path $ScriptRoot $OutDir
$runtimeDir = Join-Path $bundleDir "runtime"
$ffmpegTarget = Join-Path $runtimeDir "ffmpeg\bin"
$spleeterTarget = Join-Path $runtimeDir "spleeter"
$emTarget = Join-Path $runtimeDir "em"

Remove-Item -Recurse -Force -ErrorAction SilentlyContinue $bundleDir
New-Item -ItemType Directory -Path $bundleDir | Out-Null
New-Item -ItemType Directory -Path $ffmpegTarget -Force | Out-Null
if ($BundleMode -eq "full") {
    New-Item -ItemType Directory -Path $spleeterTarget -Force | Out-Null
} else {
    New-Item -ItemType Directory -Path $emTarget -Force | Out-Null
}

Copy-Item $distExe (Join-Path $bundleDir "CleanVedio.exe")
Copy-Item (Join-Path $ScriptRoot "server.bat") $bundleDir
Copy-Item (Join-Path $ScriptRoot "server.ps1") $bundleDir
Copy-Item (Join-Path $ScriptRoot "tail.ps1") $bundleDir
Copy-Item (Join-Path $ScriptRoot "export_support_bundle.ps1") $bundleDir
Copy-Item (Join-Path $ScriptRoot "startup.vbs") $bundleDir

$ffmpegResolved = Resolve-FfmpegBin -Provided $FfmpegBin
$spleeterResolved = Resolve-SpleeterRoot -Provided $SpleeterRoot
$emResolved = Resolve-EmRoot -Provided $EmRoot

$ffmpegCopied = $false
if ($ffmpegResolved) {
    $ffmpegCopied = Copy-IfExists (Join-Path $ffmpegResolved "*") $ffmpegTarget
}

$separatorCopied = $false
$separatorLabel = if ($BundleMode -eq "full") { "spleeter runtime" } else { "em runtime" }
if ($BundleMode -eq "full") {
    if ($spleeterResolved) {
        $separatorCopied = Copy-IfExists (Join-Path $spleeterResolved "*") $spleeterTarget
    }
} else {
    if ($emResolved) {
        $separatorCopied = Copy-IfExists (Join-Path $emResolved "*") $emTarget
    }
}

if ($BundleMode -eq "full") {
    $runBat = @"
@echo off
cd /d "%~dp0"
set "CLEANVEDIO_HOST=127.0.0.1"
set "CLEANVEDIO_PORT=8787"
set "CLEANVEDIO_SEPARATOR_BACKEND=spleeter"
call server.bat start
"@
} else {
    $runBat = @"
@echo off
cd /d "%~dp0"
set "CLEANVEDIO_HOST=127.0.0.1"
set "CLEANVEDIO_PORT=8787"
set "PATH=%~dp0runtime\ffmpeg\bin;%~dp0runtime\em;%PATH%"
set "CLEANVEDIO_SEPARATOR_BACKEND=em"
if exist "%~dp0runtime\em\SpleeterExe.exe" set "CLEANVEDIO_EM_EXE=%~dp0runtime\em\SpleeterExe.exe"
if exist "%~dp0runtime\em\models\2stems" set "CLEANVEDIO_EM_MODEL_DIR=%~dp0runtime\em\models\2stems"
call server.bat start
"@
}
Set-Content -Path (Join-Path $bundleDir "Run_CleanVedio.bat") -Value $runBat -Encoding ASCII

if ($BundleMode -eq "full") {
    $portablePathPrefix = @(
        (Join-Path $bundleDir "runtime\ffmpeg\bin"),
        (Join-Path $bundleDir "runtime\spleeter\Scripts"),
        (Join-Path $bundleDir "runtime\spleeter\bin"),
        (Join-Path $bundleDir "runtime\spleeter")
    ) -join ";"
    $separatorCommand = "spleeter"
} else {
    $portablePathPrefix = @(
        (Join-Path $bundleDir "runtime\ffmpeg\bin"),
        (Join-Path $bundleDir "runtime\em")
    ) -join ";"
    $separatorCommand = "SpleeterExe.exe"
}

$ffmpegRunnable = Test-CommandInPath -CommandName "ffmpeg" -PathPrefix $portablePathPrefix
if ($BundleMode -eq "full") {
    $separatorRunnable = Test-CommandInPath -CommandName $separatorCommand -PathPrefix $portablePathPrefix
} else {
    $separatorRunnable = (Test-Path (Join-Path $bundleDir "runtime\em\SpleeterExe.exe")) -and
        (Test-Path (Join-Path $bundleDir "runtime\em\models\2stems"))
}
$backendValue = if ($BundleMode -eq "full") { "spleeter" } else { "em" }

$notes = @"
CleanVedio Portable Bundle
==========================

Bundle mode:
- $BundleMode

1) Double-click Run_CleanVedio.bat
2) Open http://127.0.0.1:8787 if browser does not open automatically.

Bundled runtime status:
- ffmpeg bundled: $ffmpegCopied
- $separatorLabel bundled: $separatorCopied
- ffmpeg runnable from bundle: $ffmpegRunnable
- separator runnable from bundle: $separatorRunnable

Selected separator backend:
- CLEANVEDIO_SEPARATOR_BACKEND=$backendValue

Helpful support commands:
- tail logs: .\tail.ps1
- export support bundle: .\export_support_bundle.ps1

If either runnable check is false, copy runtime manually:
- runtime\ffmpeg\bin\ffmpeg.exe
- runtime\spleeter\... (full mode), or runtime\em\... (lean mode)
"@
Set-Content -Path (Join-Path $bundleDir "PORTABLE_README.txt") -Value $notes -Encoding ASCII

Write-Host "Portable bundle created: $bundleDir" -ForegroundColor Green
Write-Host "bundle mode: $BundleMode" -ForegroundColor Cyan
Write-Host "ffmpeg bundled: $ffmpegCopied" -ForegroundColor Cyan
Write-Host "$separatorLabel bundled: $separatorCopied" -ForegroundColor Cyan
Write-Host "ffmpeg runnable from bundle: $ffmpegRunnable" -ForegroundColor Cyan
Write-Host "separator runnable from bundle: $separatorRunnable" -ForegroundColor Cyan
