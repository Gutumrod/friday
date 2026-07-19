@echo off
cd /d "%~dp0"
set "PYTHONPATH=%~dp0src"
"C:\Users\Win10\miniconda3\envs\friday\python.exe" -m uvicorn friday.api:app --host 127.0.0.1 --port 8000
pause
