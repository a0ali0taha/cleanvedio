param(
    [ValidateSet("all", "out", "err")]
    [string]$Log = "all",
    [int]$Lines = 30
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$dataRoot = if ($env:CLEANVEDIO_DATA_DIR) {
    $env:CLEANVEDIO_DATA_DIR
} elseif ($env:LOCALAPPDATA) {
    Join-Path $env:LOCALAPPDATA "CleanVedio"
} else {
    $scriptDir
}
$logDir = Join-Path $dataRoot "logs"
$outLog = Join-Path $logDir "server.log"
$errLog = Join-Path $logDir "server.err.log"

if (-not (Test-Path $outLog)) {
    $outLog = Join-Path $scriptDir "server.log"
}
if (-not (Test-Path $errLog)) {
    $errLog = Join-Path $scriptDir "server.err.log"
}

function Tail-File($path, $label, $color) {
    if (-not (Test-Path $path)) {
        Write-Host "[$label] File not found: $path" -ForegroundColor DarkGray
        return
    }
    $content = Get-Content $path -Tail $Lines
    Write-Host "`n=== $label ===" -ForegroundColor $color
    $content | ForEach-Object { Write-Host $_ -ForegroundColor $color }
}

if ($Log -eq "all" -or $Log -eq "out") {
    Tail-File $outLog "server.log" "White"
}
if ($Log -eq "all" -or $Log -eq "err") {
    Tail-File $errLog "server.err.log" "Red"
}

Write-Host "`n--- Watching for changes (Ctrl+C to stop) ---`n" -ForegroundColor Yellow

$jobs = @()
if ($Log -eq "all" -or $Log -eq "out") {
    $jobs += Start-Job -ScriptBlock {
        param($p)
        Get-Content $p -Wait -Tail 0
    } -ArgumentList $outLog
}
if ($Log -eq "all" -or $Log -eq "err") {
    $jobs += Start-Job -ScriptBlock {
        param($p)
        Get-Content $p -Wait -Tail 0
    } -ArgumentList $errLog
}

try {
    while ($true) {
        foreach ($job in $jobs) {
            $output = Receive-Job $job -ErrorAction SilentlyContinue
            if ($output) {
                $color = if ($job -eq $jobs[-1] -and $Log -ne "out") { "Red" } else { "White" }
                $output | ForEach-Object { Write-Host $_ -ForegroundColor $color }
            }
        }
        Start-Sleep -Milliseconds 200
    }
} finally {
    $jobs | Stop-Job -PassThru | Remove-Job
}
