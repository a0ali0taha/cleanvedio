Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
WshShell.CurrentDirectory = scriptDir
WshShell.Run "powershell -ExecutionPolicy Bypass -WindowStyle Hidden -File """ & scriptDir & "\server.ps1"" start", 0, False
