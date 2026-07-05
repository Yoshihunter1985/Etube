@echo off
cd /d "%~dp0"

echo Adding files...
git add .

echo Committing...
git commit -m "Add videos %date% %time%"

echo Pushing to GitHub...
git push

echo.
echo Done! Give GitHub Pages a minute or two to update.
pause
