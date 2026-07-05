@echo off
cd /d "%~dp0"

echo Starting local video studio...
start "" http://localhost:5050

python studio_server.py

pause
