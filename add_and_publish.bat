@echo off
setlocal
cd /d "%~dp0"

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

echo.
echo === Downloading and converting ===
python "%~dp0add_video.py" "%URL%"

if errorlevel 1 (
    echo.
    echo Download/convert failed - not pushing anything.
    pause
    exit /b 1
)

echo.
echo === Pushing to GitHub ===
git add .
git commit -m "Add video %date% %time%"
git push

echo.
echo All done! Give GitHub Pages a minute or two to update.
pause
