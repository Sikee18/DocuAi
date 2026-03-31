@echo off
echo Stopping any existing Python/Node processes...
taskkill /F /IM python.exe /T 2>nul
taskkill /F /IM node.exe /T 2>nul
timeout /t 3 /nobreak >nul

echo Freeing port 8000...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000 " ^| findstr "LISTENING"') do taskkill /F /PID %%a 2>nul
timeout /t 2 /nobreak >nul

echo Starting DocuAI...
set PYTHONUTF8=1
cd /d %~dp0
.\venv\Scripts\python.exe -m reflex run
pause
