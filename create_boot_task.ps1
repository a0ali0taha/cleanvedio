$ScriptRoot = $PSScriptRoot
$StartupVbs = Join-Path $ScriptRoot "startup.vbs"
$Action = New-ScheduledTaskAction -Execute "wscript.exe" -Argument "`"$StartupVbs`"" -WorkingDirectory $ScriptRoot
$Trigger = New-ScheduledTaskTrigger -AtStartup
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
$Principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -RunLevel Highest -LogonType S4U

Register-ScheduledTask -TaskName "CleanVedio Server" -Action $Action -Trigger $Trigger -Settings $Settings -Principal $Principal -Force

Write-Host "Scheduled task 'CleanVedio Server' created - will run at boot without login." -ForegroundColor Green
