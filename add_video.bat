@echo off
setlocal

if "%~1"=="" (
    set /p URL=Paste YouTube URL: 
) else (
    set URL=%~1
)

if "%URL%"=="" (
    echo No URL given.
    pause
    exit /b 1
)

python "%~dp0add_video.py" "%URL%"

if errorlevel 1 (
    echo.
    echo Something went wrong - check the messages above.
    pause
    exit /b 1
)

pause
