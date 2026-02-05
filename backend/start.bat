@echo off
setlocal enabledelayedexpansion

echo ============================================================
echo  TIMETABLE BACKEND - AUTOMATED STARTUP
echo ============================================================
echo.

:: Navigate to backend directory
cd /d "%~dp0"

:: Step 1: Check if Python is installed
echo [1/5] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from python.org
    pause
    exit /b 1
)
echo ✓ Python found

:: Step 2: Check/Create virtual environment
echo.
echo [2/5] Checking virtual environment...
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo ✓ Virtual environment created
) else (
    echo ✓ Virtual environment exists
)

:: Step 3: Activate virtual environment and install dependencies
echo.
echo [3/5] Installing dependencies...
call venv\Scripts\activate.bat

:: Check if requirements are already installed
pip show fastapi >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing required packages...
    pip install -q -r requirements.txt
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
    echo ✓ Dependencies installed
) else (
    echo ✓ Dependencies already installed
)

:: Step 4: Initialize database if needed
echo.
echo [4/5] Checking database...
if not exist "timetable.db" (
    echo Database not found. Initializing...
    python setup_database.py
    if %errorlevel% neq 0 (
        echo ERROR: Failed to initialize database
        pause
        exit /b 1
    )
    echo ✓ Database initialized with sample data
) else (
    echo ✓ Database exists
)

:: Step 5: Start the server
echo.
echo [5/5] Starting Backend Server...
echo.
echo ============================================================
echo  SERVER STARTING
echo ============================================================
echo  Backend URL: http://localhost:8000
echo  API Docs:    http://localhost:8000/docs
echo  Health:      http://localhost:8000/
echo ============================================================
echo.
echo Press Ctrl+C to stop the server
echo.

:: Start uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

:: This will only execute when the server stops
echo.
echo Server stopped.
pause
