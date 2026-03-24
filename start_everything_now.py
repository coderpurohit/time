#!/usr/bin/env python3

import subprocess
import time
import webbrowser
import os
import sys
from pathlib import Path

def start_backend():
    """Start the backend server"""
    print("🚀 Starting backend server...")
    backend_dir = Path("backend")
    
    if not backend_dir.exists():
        print("❌ Backend directory not found!")
        return None
    
    # Check if start.bat exists
    start_bat = backend_dir / "start.bat"
    if start_bat.exists():
        # Use start.bat
        process = subprocess.Popen(
            ["start.bat"], 
            cwd=backend_dir,
            shell=True,
            creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
        )
    else:
        # Fallback to direct uvicorn
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"
        ], cwd=backend_dir)
    
    return process

def start_file_server():
    """Start a simple HTTP server for frontend files"""
    print("🌐 Starting file server for frontend...")
    
    # Start HTTP server on port 3000
    process = subprocess.Popen([
        sys.executable, "-m", "http.server", "3000"
    ], cwd=".")
    
    return process

def main():
    print("=== STARTING TIMETABLE SYSTEM ===")
    
    # Start backend
    backend_process = start_backend()
    
    # Start file server
    file_server_process = start_file_server()
    
    # Wait for servers to start
    print("⏳ Waiting for servers to start...")
    time.sleep(5)
    
    # Open browser
    print("🌐 Opening browser...")
    webbrowser.open("http://localhost:3000/timetable_page.html")
    
    print("\n✅ SYSTEM STARTED!")
    print("📊 Timetable Page: http://localhost:3000/timetable_page.html")
    print("🔧 Backend API: http://localhost:8000/docs")
    print("📈 Dashboard: http://localhost:3000/dashboard.html")
    
    print("\n🎯 DATA STATUS: All data cleared - ready for new setup!")
    print("📝 Add your teachers, classes, subjects through the web interface")
    
    try:
        print("\n⌨️  Press Ctrl+C to stop all servers...")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping servers...")
        if backend_process:
            backend_process.terminate()
        if file_server_process:
            file_server_process.terminate()
        print("✅ All servers stopped!")

if __name__ == "__main__":
    main()