$WshShell = New-Object -ComObject WScript.Shell
$StartupPath = [System.IO.Path]::Combine($env:APPDATA, "Microsoft\Windows\Start Menu\Programs\Startup")
$Shortcut = $WshShell.CreateShortcut("$StartupPath\CleanVedio Server.lnk")
$ScriptRoot = $PSScriptRoot
$Shortcut.TargetPath = Join-Path $ScriptRoot "startup.vbs"
$Shortcut.WorkingDirectory = $ScriptRoot
$Shortcut.Description = "Start CleanVedio Server"
$Shortcut.Save()
Write-Host "Startup shortcut created at: $StartupPath\CleanVedio Server.lnk" -ForegroundColor Green
