@echo off
echo ============================================================
echo  TIMETABLE BACKEND - QUICK START (BACKGROUND)
echo ============================================================
echo.

cd /d "%~dp0"

:: Check if server is already running
netstat -ano | find ":8000" | find "LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo Backend server is already running at http://localhost:8000
    echo Run 'stop.bat' to stop it first.
    timeout /t 3 >nul
    exit /b 0
)

echo Starting backend server in background...

:: Start server in a new hidden window
start /B "" cmd /c "call venv\Scripts\activate.bat && uvicorn app.main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1"

:: Wait and check if server started
timeout /t 3 >nul

netstat -ano | find ":8000" | find "LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo.
    echo ✓ Backend server started successfully!
    echo.
    echo ============================================================
    echo  Backend URL:  http://localhost:8000
    echo  API Docs:     http://localhost:8000/docs
    echo  Logs:         backend.log
    echo ============================================================
    echo.
    echo Run 'stop.bat' to stop the server
) else (
    echo.
    echo × Failed to start server. Check backend.log for errors.
)

timeout /t 2 >nul
