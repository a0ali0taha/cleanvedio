@REM rm input_segments\*
@REM rm output\*
@REM rmdir -s -q output_folder\*


@echo off
set "folder_path=input_segments"
if not exist "%folder_path%" (
    echo Folder not found: "%folder_path%"
    exit /b 1
)
del /q "%folder_path%\*"
for /d %%i in ("%folder_path%\*") do (
    rmdir /s /q "%%i"
)

set "folder_path=output"
if not exist "%folder_path%" (
    echo Folder not found: "%folder_path%"
    exit /b 1
)
del /q "%folder_path%\*"
for /d %%i in ("%folder_path%\*") do (
    rmdir /s /q "%%i"
)

set "folder_path=output_folder"
if not exist "%folder_path%" (
    echo Folder not found: "%folder_path%"
    exit /b 1
)
del /q "%folder_path%\*"
for /d %%i in ("%folder_path%\*") do (
    rmdir /s /q "%%i"
)
python gui.py
python detach.py
python audio_split.py
python spleeter.py
python audio_merge.py
python attach.py
python process_mp4_files.py
PAUSE
