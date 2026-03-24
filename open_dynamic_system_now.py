#!/usr/bin/env python3

import webbrowser
import time
import requests

def open_dynamic_system():
    """Open the Dynamic Academic Management System"""
    
    url = "http://localhost:8000/dynamic_academic_management.html"
    
    # Check if backend is running
    try:
        response = requests.get("http://localhost:8000/api/teachers", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running")
        else:
            print("⚠️ Backend responded but with error")
    except:
        print("❌ Backend not running! Start it with: cd backend && .\\start.bat")
        return False
    
    print(f"🌐 Opening: {url}")
    webbrowser.open(url)
    
    print("\n📋 INSTRUCTIONS:")
    print("1. Click on 'Load Factor Engine' tab")
    print("2. Click 'Bulk Import' button")
    print("3. Click 'Direct Import' button (now working!)")
    print("4. Click 'Refresh Assignments' button (now working!)")
    print("5. You should see all 7 teachers with their assigned subjects")
    
    return True

if __name__ == "__main__":
    print("🚀 OPENING DYNAMIC ACADEMIC MANAGEMENT SYSTEM")
    open_dynamic_system()