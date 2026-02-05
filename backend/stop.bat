@echo off
echo ============================================================
echo  STOPPING TIMETABLE BACKEND
echo ============================================================
echo.

:: Find and kill uvicorn processes
echo Searching for running backend processes...

:: Kill uvicorn processes
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *uvicorn*" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Backend server stopped
) else (
    :: Try alternative method
    for /f "tokens=2" %%a in ('tasklist /FI "IMAGENAME eq python.exe" /FO LIST ^| find "PID:"') do (
        netstat -ano | find ":8000" | find "%%a" >nul 2>&1
        if !errorlevel! equ 0 (
            taskkill /F /PID %%a
            echo ✓ Stopped backend server (PID: %%a)
        )
    )
)

echo.
echo Backend server stopped.
timeout /t 2 >nul
