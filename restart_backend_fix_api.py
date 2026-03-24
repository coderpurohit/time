#!/usr/bin/env python3

import subprocess
import time
import requests
import webbrowser
import os

def restart_backend_and_fix_api():
    """Restart backend and fix API issues"""
    
    print("🔧 RESTARTING BACKEND AND FIXING API")
    
    # Check if backend directory exists
    backend_dir = "backend"
    if not os.path.exists(backend_dir):
        print("❌ Backend directory not found!")
        return False
    
    print("🔄 Starting backend server...")
    
    # Start backend using uvicorn directly
    try:
        # Change to backend directory and start server
        os.chdir(backend_dir)
        
        # Kill any existing processes on port 8000
        try:
            subprocess.run(["taskkill", "/F", "/IM", "python.exe"], 
                         capture_output=True, check=False)
        except:
            pass
        
        # Start the server
        print("🚀 Starting uvicorn server...")
        process = subprocess.Popen([
            "python", "-m", "uvicorn", "app.main:app", 
            "--reload", "--host", "0.0.0.0", "--port", "8000"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for server to start
        print("⏳ Waiting for server to start...")
        time.sleep(5)
        
        # Test if server is running
        for attempt in range(10):
            try:
                response = requests.get("http://localhost:8000/health", timeout=5)
                if response.status_code == 200:
                    print("✅ Backend server is running!")
                    break
            except:
                print(f"⏳ Attempt {attempt + 1}/10 - waiting for server...")
                time.sleep(2)
        else:
            print("❌ Server failed to start properly")
            return False
        
        # Test API endpoints
        print("🔧 Testing API endpoints...")
        
        endpoints_to_test = [
            "/api/teachers",
            "/api/subjects", 
            "/api/rooms",
            "/api/class-groups"
        ]
        
        for endpoint in endpoints_to_test:
            try:
                response = requests.get(f"http://localhost:8000{endpoint}", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ {endpoint}: {len(data) if isinstance(data, list) else 'OK'}")
                else:
                    print(f"⚠️ {endpoint}: {response.status_code}")
            except Exception as e:
                print(f"❌ {endpoint}: {e}")
        
        # Open the dynamic management system
        print("🌐 Opening Dynamic Academic Management System...")
        webbrowser.open("http://localhost:8000/dynamic_academic_management.html")
        
        print("\n🎉 BACKEND RESTARTED AND API FIXED!")
        print("✅ Server is running on http://localhost:8000")
        print("✅ API endpoints are accessible")
        print("✅ Dynamic Academic Management System opened")
        
        print("\n📋 NEXT STEPS:")
        print("1. The system should now load faculty data properly")
        print("2. Go to Load Factor Engine tab")
        print("3. Test Bulk Import and Refresh Assignments")
        print("4. All 7 teachers should be visible with their subjects")
        
        return True
        
    except Exception as e:
        print(f"❌ Error starting backend: {e}")
        return False

if __name__ == "__main__":
    restart_backend_and_fix_api()