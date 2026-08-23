@echo off
setlocal
cd /d %~dp0

if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate.bat
pip install -q -r requirements.txt

echo Starting DEPMAP API on http://localhost:8000 ...
start "DEPMAP API" cmd /k uvicorn api.main:app --reload

timeout /t 2 /nobreak > nul

echo Opening frontend...
start "" "%~dp0frontend\index.html"

echo.
echo DEPMAP is running. Close the "DEPMAP API" window to stop the server.
pause