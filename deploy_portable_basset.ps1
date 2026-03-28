# Build dist\CleanVedio.exe (optional) and create portable\CleanVedioPortable with Em (lean bundle).
# Requires at repo root: SpleeterExe.exe, models\2stems\, ffmpeg.exe, ffprobe.exe
param(
    [switch]$SkipBuild,
    [string]$OutDir = "portable\CleanVedioPortable"
)

$ErrorActionPreference = "Stop"
$ScriptRoot = $PSScriptRoot
Set-Location $ScriptRoot

$emRuntime = Join-Path $ScriptRoot "em-runtime"
$ffmpegOnly = Join-Path $ScriptRoot "_portable_ffmpeg\bin"

Write-Host "Staging $emRuntime ..." -ForegroundColor Cyan
Remove-Item -Recurse -Force -ErrorAction SilentlyContinue $emRuntime
New-Item -ItemType Directory -Path $emRuntime -Force | Out-Null

if (-not (Test-Path (Join-Path $ScriptRoot "SpleeterExe.exe"))) {
    throw "Missing SpleeterExe.exe at repo root."
}
if (-not (Test-Path (Join-Path $ScriptRoot "models\2stems\saved_model.pb"))) {
    throw "Missing models\2stems\ (need saved_model.pb)."
}

Copy-Item (Join-Path $ScriptRoot "SpleeterExe.exe") $emRuntime -Force
foreach ($f in @("tensorflow.dll", "spleeter.lib")) {
    $p = Join-Path $ScriptRoot $f
    if (Test-Path $p) { Copy-Item $p $emRuntime -Force }
}
Copy-Item (Join-Path $ScriptRoot "models") $emRuntime -Recurse -Force

Write-Host "Staging $ffmpegOnly ..." -ForegroundColor Cyan
Remove-Item -Recurse -Force -ErrorAction SilentlyContinue (Split-Path $ffmpegOnly -Parent)
New-Item -ItemType Directory -Path $ffmpegOnly -Force | Out-Null
foreach ($exe in @("ffmpeg.exe", "ffprobe.exe")) {
    $p = Join-Path $ScriptRoot $exe
    if (-not (Test-Path $p)) {
        throw "Missing $p. Place ffmpeg.exe and ffprobe.exe next to this script."
    }
    Copy-Item $p $ffmpegOnly -Force
}

if (-not $SkipBuild) {
    Write-Host "Running build_windows.ps1 ..." -ForegroundColor Cyan
    & (Join-Path $ScriptRoot "build_windows.ps1") -Clean
}

$distExe = Join-Path $ScriptRoot "dist\CleanVedio.exe"
if (-not (Test-Path $distExe)) {
    throw "Missing $distExe. Run without -SkipBuild or run .\build_windows.ps1"
}

Write-Host "Running make_portable_bundle.ps1 (lean / Em) ..." -ForegroundColor Cyan
& (Join-Path $ScriptRoot "make_portable_bundle.ps1") `
    -BundleMode lean `
    -OutDir $OutDir `
    -EmRoot $emRuntime `
    -FfmpegBin $ffmpegOnly

Write-Host ""
Write-Host "Done. Test: $(Join-Path $ScriptRoot $OutDir)\Run_CleanVedio.bat then http://127.0.0.1:8787" -ForegroundColor Green
