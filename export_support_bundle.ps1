param(
    [string]$OutDir = "",
    [switch]$IncludeFinalVideos
)

$ErrorActionPreference = "Stop"
$ScriptRoot = $PSScriptRoot
$DataRoot = if ($env:CLEANVEDIO_DATA_DIR) {
    $env:CLEANVEDIO_DATA_DIR
} elseif ($env:LOCALAPPDATA) {
    Join-Path $env:LOCALAPPDATA "CleanVedio"
} else {
    $ScriptRoot
}

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
if (-not $OutDir) {
    $OutDir = Join-Path $ScriptRoot "support"
}
New-Item -Path $OutDir -ItemType Directory -Force | Out-Null

$bundleRoot = Join-Path $OutDir "CleanVedioSupport_$timestamp"
New-Item -Path $bundleRoot -ItemType Directory -Force | Out-Null

function Copy-IfExists($src, $dst) {
    if (Test-Path $src) {
        Copy-Item -Path $src -Destination $dst -Recurse -Force
    }
}

$manifest = @{
    generated_at = (Get-Date).ToString("s")
    machine_name = $env:COMPUTERNAME
    user_name = $env:USERNAME
    data_root = $DataRoot
    cleanvedio_host = $env:CLEANVEDIO_HOST
    cleanvedio_port = $env:CLEANVEDIO_PORT
    separator_backend = $env:CLEANVEDIO_SEPARATOR_BACKEND
    include_final_videos = [bool]$IncludeFinalVideos
}
$manifest | ConvertTo-Json -Depth 4 | Set-Content -Path (Join-Path $bundleRoot "manifest.json") -Encoding UTF8

Copy-IfExists (Join-Path $DataRoot "jobs.json") (Join-Path $bundleRoot "jobs.json")
Copy-IfExists (Join-Path $DataRoot "logger.log") (Join-Path $bundleRoot "logger.log")
Copy-IfExists (Join-Path $DataRoot "logs") (Join-Path $bundleRoot "logs")
Copy-IfExists (Join-Path $ScriptRoot "server.log") (Join-Path $bundleRoot "legacy_server.log")
Copy-IfExists (Join-Path $ScriptRoot "server.err.log") (Join-Path $bundleRoot "legacy_server.err.log")

if ($IncludeFinalVideos) {
    Copy-IfExists (Join-Path $DataRoot "final") (Join-Path $bundleRoot "final")
}

$zipPath = Join-Path $OutDir "CleanVedioSupport_$timestamp.zip"
if (Test-Path $zipPath) {
    Remove-Item $zipPath -Force
}
Compress-Archive -Path (Join-Path $bundleRoot "*") -DestinationPath $zipPath -Force

Write-Host "Support bundle created: $zipPath" -ForegroundColor Green
Write-Host "Share this file for troubleshooting." -ForegroundColor Cyan
