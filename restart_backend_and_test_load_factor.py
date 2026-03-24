#!/usr/bin/env python3

import subprocess
import time
import requests
import os
import signal

def restart_backend():
    """Restart the backend server"""
    print("=== RESTARTING BACKEND SERVER ===")
    
    # Kill any existing uvicorn processes
    try:
        subprocess.run(["taskkill", "/f", "/im", "python.exe"], capture_output=True)
        time.sleep(2)
    except:
        pass
    
    # Start the backend server
    os.chdir("backend")
    process = subprocess.Popen(
        ["python", "-m", "uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    print("Backend server starting...")
    time.sleep(5)  # Give it time to start
    
    return process

def test_load_factor():
    """Test the load factor API"""
    try:
        print("=== TESTING LOAD FACTOR API ===")
        response = requests.get("http://localhost:8000/api/analytics/load-factor")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Load Factor API working!")
            print(f"Teachers: {data['summary']['total_teachers']}")
            print(f"Classes: {data['summary']['total_classes']}")
            print(f"Conflicts: {data['validation']['total_conflicts']}")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def main():
    process = restart_backend()
    
    try:
        if test_load_factor():
            print("\n🎉 Load Factor API is working!")
            print("You can now refresh your browser and the Load Factor section should work.")
        else:
            print("\n❌ Load Factor API still not working")
            
        input("\nPress Enter to stop the server...")
        
    finally:
        process.terminate()
        process.wait()

if __name__ == "__main__":
    main()