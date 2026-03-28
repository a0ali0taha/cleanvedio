param(
    [Parameter(Position=0)]
    [ValidateSet("start","stop","status","restart")]
    [string]$Action = "status",
    [switch]$OpenBrowser
)

$ScriptRoot = $PSScriptRoot
$ServerScript = Join-Path $PSScriptRoot "server.py"
$ExeCandidates = @(
    (Join-Path $PSScriptRoot "CleanVedio.exe"),
    (Join-Path $PSScriptRoot "dist\CleanVedio.exe"),
    (Join-Path $PSScriptRoot "dist\CleanVedio\CleanVedio.exe")
)
$DefaultDataRoot = if ($env:CLEANVEDIO_DATA_DIR) {
    $env:CLEANVEDIO_DATA_DIR
} elseif ($env:LOCALAPPDATA) {
    Join-Path $env:LOCALAPPDATA "CleanVedio"
} else {
    $ScriptRoot
}
New-Item -Path $DefaultDataRoot -ItemType Directory -Force | Out-Null
$LogDir = Join-Path $DefaultDataRoot "logs"
New-Item -Path $LogDir -ItemType Directory -Force | Out-Null

$PidFile = Join-Path $DefaultDataRoot "server.pid"
$HostAddr = if ($env:CLEANVEDIO_HOST) { $env:CLEANVEDIO_HOST } else { "127.0.0.1" }
$PortNumber = if ($env:CLEANVEDIO_PORT) { [int]$env:CLEANVEDIO_PORT } else { 8787 }

function Add-ToPath($candidate) {
    if (Test-Path $candidate) {
        if (-not $env:PATH.Split(';') -contains $candidate) {
            $env:PATH = "$candidate;$env:PATH"
        }
    }
}

function Configure-PortableRuntime {
    $runtimeRoot = Join-Path $ScriptRoot "runtime"
    $ffmpegBin = Join-Path $runtimeRoot "ffmpeg\bin"
    $spleeterRoot = Join-Path $runtimeRoot "spleeter"
    $spleeterScripts = Join-Path $spleeterRoot "Scripts"
    $spleeterBin = Join-Path $spleeterRoot "bin"
    $emRoot = Join-Path $runtimeRoot "em"
    $emModels = Join-Path $emRoot "models\2stems"

    Add-ToPath $ffmpegBin
    Add-ToPath $spleeterScripts
    Add-ToPath $spleeterBin
    Add-ToPath $spleeterRoot
    Add-ToPath $emRoot

    if (-not $env:CLEANVEDIO_EM_EXE) {
        $emExe = Join-Path $emRoot "SpleeterExe.exe"
        if (Test-Path $emExe) {
            $env:CLEANVEDIO_EM_EXE = $emExe
        }
    }
    if (-not $env:CLEANVEDIO_EM_MODEL_DIR -and (Test-Path $emModels)) {
        $env:CLEANVEDIO_EM_MODEL_DIR = $emModels
    }
}

function Get-LaunchInfo {
    foreach ($candidate in $ExeCandidates) {
        if (Test-Path $candidate) {
            return @{
                FilePath = $candidate
                Arguments = @()
                Mode = "packaged"
            }
        }
    }

    if ($env:CLEANVEDIO_PYTHON) {
        return @{
            FilePath = $env:CLEANVEDIO_PYTHON
            Arguments = @($ServerScript)
            Mode = "python"
        }
    }

    $py = Get-Command py -ErrorAction SilentlyContinue
    if ($py) {
        return @{
            FilePath = $py.Source
            Arguments = @("-3", $ServerScript)
            Mode = "python"
        }
    }

    return @{
        FilePath = "python"
        Arguments = @($ServerScript)
        Mode = "python"
    }
}

function Get-LocalIPv4 {
    $addr = Get-NetIPAddress -AddressFamily IPv4 -ErrorAction SilentlyContinue |
        Where-Object {
            $_.IPAddress -notlike "127.*" -and
            $_.IPAddress -notlike "169.254.*"
        } |
        Select-Object -First 1 -ExpandProperty IPAddress
    if ($addr) {
        return $addr
    }
    return "127.0.0.1"
}

function Resolve-ServerBinding($mode) {
    $resolvedHost = if ($env:CLEANVEDIO_HOST) {
        $env:CLEANVEDIO_HOST
    } elseif ($env:CLEANVEDIO_ALLOW_LAN -eq "1" -and $mode -eq "packaged") {
        Get-LocalIPv4
    } else {
        "127.0.0.1"
    }

    if ($env:CLEANVEDIO_PORT) {
        $resolvedPort = [int]$env:CLEANVEDIO_PORT
    } else {
        $resolvedPort = 8787
    }

    return @{
        Host = $resolvedHost
        Port = $resolvedPort
    }
}

function Test-PortAvailable([string]$BindHost, [int]$Port) {
    $listener = $null
    try {
        $ip = [System.Net.IPAddress]::Parse($BindHost)
        $listener = [System.Net.Sockets.TcpListener]::new($ip, $Port)
        $listener.Start()
        return $true
    } catch {
        return $false
    } finally {
        if ($listener) {
            $listener.Stop()
        }
    }
}

function Get-AvailablePort([string]$BindHost, [int]$StartPort) {
    for ($i = 0; $i -lt 30; $i++) {
        $candidate = $StartPort + $i
        if (Test-PortAvailable -BindHost $BindHost -Port $candidate) {
            return $candidate
        }
    }
    return $StartPort
}

function Get-ServerProcess {
    if (Test-Path $PidFile) {
        $pid_val = [int](Get-Content $PidFile -Raw).Trim()
        $proc = Get-Process -Id $pid_val -ErrorAction SilentlyContinue
        if ($proc) { return $proc }
        Remove-Item $PidFile -Force
    }
    return $null
}

function Start-Server {
    $proc = Get-ServerProcess
    if ($proc) {
        Write-Host "Server is already running (PID: $($proc.Id))" -ForegroundColor Yellow
        return
    }

    $launch = Get-LaunchInfo
    $binding = Resolve-ServerBinding $launch.Mode
    $script:HostAddr = $binding.Host
    $requestedPort = $binding.Port
    $script:PortNumber = Get-AvailablePort -BindHost $HostAddr -StartPort $requestedPort
    Configure-PortableRuntime
    $env:CLEANVEDIO_HOST = $HostAddr
    $env:CLEANVEDIO_PORT = $PortNumber.ToString()
    $env:CLEANVEDIO_DEBUG = "0"
    $env:CLEANVEDIO_DATA_DIR = $DefaultDataRoot

    if ($PortNumber -ne $requestedPort) {
        Write-Host "Port $requestedPort is busy. Switching to $PortNumber." -ForegroundColor Yellow
    }

    Write-Host "Starting server ($($launch.Mode))..." -ForegroundColor Cyan
    $startArgs = @{
        FilePath = $launch.FilePath
        WorkingDirectory = $PSScriptRoot
        WindowStyle = "Hidden"
        PassThru = $true
        RedirectStandardOutput = (Join-Path $LogDir "server.log")
        RedirectStandardError = (Join-Path $LogDir "server.err.log")
    }
    if ($launch.Arguments -and $launch.Arguments.Count -gt 0) {
        $startArgs.ArgumentList = $launch.Arguments
    }
    $p = Start-Process @startArgs

    $p.Id | Out-File $PidFile -NoNewline
    Start-Sleep -Seconds 3

    $check = Get-Process -Id $p.Id -ErrorAction SilentlyContinue
    if ($check) {
        Write-Host "Server started (PID: $($p.Id))" -ForegroundColor Green
        Write-Host "URL: http://${HostAddr}:${PortNumber}" -ForegroundColor Green
        if ($OpenBrowser -or $Action -eq "start") {
            Start-Process "http://${HostAddr}:${PortNumber}" | Out-Null
        }
    } else {
        Write-Host "Server failed to start. Check logs in $LogDir" -ForegroundColor Red
        Remove-Item $PidFile -Force -ErrorAction SilentlyContinue
    }
}

function Stop-Server {
    $proc = Get-ServerProcess
    if (-not $proc) {
        Write-Host "Server is not running." -ForegroundColor Yellow
        return
    }
    Write-Host "Stopping server (PID: $($proc.Id))..." -ForegroundColor Cyan
    Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
    Get-NetTCPConnection -LocalPort $PortNumber -ErrorAction SilentlyContinue |
        ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
    Remove-Item $PidFile -Force -ErrorAction SilentlyContinue
    Write-Host "Server stopped." -ForegroundColor Green
}

function Get-ServerStatus {
    $proc = Get-ServerProcess
    if ($proc) {
        $uptime = (Get-Date) - $proc.StartTime
        Write-Host "Server is running (PID: $($proc.Id), uptime: $([math]::Floor($uptime.TotalMinutes)) min)" -ForegroundColor Green
    } else {
        Write-Host "Server is not running." -ForegroundColor Yellow
    }
}

switch ($Action) {
    "start"   { Start-Server }
    "stop"    { Stop-Server }
    "status"  { Get-ServerStatus }
    "restart" { Stop-Server; Start-Sleep -Seconds 2; Start-Server }
}
