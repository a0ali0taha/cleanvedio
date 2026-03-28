param(
    [switch]$Clean
)

$ErrorActionPreference = "Stop"
$ScriptRoot = $PSScriptRoot
Set-Location $ScriptRoot

if ($Clean) {
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue (Join-Path $ScriptRoot "build")
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue (Join-Path $ScriptRoot "dist")
}

$python = if ($env:CLEANVEDIO_PYTHON) { $env:CLEANVEDIO_PYTHON } else { "python" }

Write-Host "Using Python: $python" -ForegroundColor Cyan
& $python -m pip install --upgrade pip
& $python -m pip install -r requirements.txt pyinstaller

Write-Host "Building Windows package with PyInstaller..." -ForegroundColor Cyan
& $python -m PyInstaller --noconfirm --clean CleanVedio.spec

if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller build failed."
}

Write-Host "Build complete: dist/CleanVedio.exe" -ForegroundColor Green
