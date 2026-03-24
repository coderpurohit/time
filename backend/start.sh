#!/bin/bash

echo "============================================================"
echo " TIMETABLE BACKEND - AUTOMATED STARTUP"
echo "============================================================"
echo ""

# Navigate to backend directory
cd "$(dirname "$0")"

# Step 1: Check if Python is installed
echo "[1/5] Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.8+ from python.org"
    exit 1
fi
echo "✓ Python found"

# Step 2: Check/Create virtual environment
echo ""
echo "[2/5] Checking virtual environment..."
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to create virtual environment"
        exit 1
    fi
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment exists"
fi

# Step 3: Activate virtual environment and install dependencies
echo ""
echo "[3/5] Installing dependencies..."
source venv/bin/activate

# Check if requirements are already installed
if ! pip show fastapi &> /dev/null; then
    echo "Installing required packages..."
    pip install -q -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install dependencies"
        exit 1
    fi
    echo "✓ Dependencies installed"
else
    echo "✓ Dependencies already installed"
fi

# Step 4: Initialize database if needed
echo ""
echo "[4/5] Checking database..."
if [ ! -f "timetable.db" ]; then
    echo "Database not found. Initializing..."
    python setup_database.py
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to initialize database"
        exit 1
    fi
    echo "✓ Database initialized with sample data"
else
    echo "✓ Database exists"
fi

# Step 5: Start the server
echo ""
echo "[5/5] Starting Backend Server..."
echo ""
echo "============================================================"
echo " SERVER STARTING"
echo "============================================================"
echo " Backend URL: http://localhost:8000"
echo " API Docs:    http://localhost:8000/docs"
echo " Health:      http://localhost:8000/"
echo "============================================================"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# This will only execute when the server stops
echo ""
echo "Server stopped."
