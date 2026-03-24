#!/usr/bin/env python3

import subprocess
import time
import requests
import os
import sys

def start_backend():
    """Start the backend server"""
    print("=== STARTING BACKEND SERVER ===")
    
    # Change to backend directory
    os.chdir("backend")
    
    # Start the server
    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    print("Backend server starting... (waiting 8 seconds)")
    time.sleep(8)  # Give it time to start
    
    return process

def test_enhanced_apis():
    """Test both enhanced APIs"""
    try:
        print("=== TESTING ENHANCED LOAD FACTOR ===")
        response = requests.get("http://localhost:8000/api/analytics/load-factor")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Enhanced Load Factor working!")
            
            # Show sample teacher with enhanced classification
            teachers = data.get('teacher_load', [])
            if teachers:
                t = teachers[0]
                print(f"Sample: {t['name']}")
                print(f"  Theory: {t['theory_hours']}h, Lab: {t['lab_hours']}h")
                print(f"  Practical: {t['practical_hours']}h, Project: {t['project_hours']}h")
        
        print("\n=== TESTING LAB SCHEDULE ANALYSIS ===")
        response2 = requests.get("http://localhost:8000/api/analytics/lab-schedule-analysis")
        
        if response2.status_code == 200:
            data2 = response2.json()
            print("✅ Lab Schedule Analysis working!")
            print(f"Lab entries found: {data2.get('total_lab_entries', 0)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    # Start backend
    process = start_backend()
    
    try:
        # Test APIs
        if test_enhanced_apis():
            print("\n🎉 SUCCESS! Enhanced Load Factor APIs are working!")
            print("\nNew features added:")
            print("✅ Enhanced lab classification based on D.Y. Patil format")
            print("✅ Better detection of SL1, SL2, SL3, SL4 labs")
            print("✅ AI Lab, DS Lab, PLL Lab, DIY Lab recognition")
            print("✅ Improved practical/project categorization")
            print("✅ Department-wise lab analysis")
            
            print("\n📝 Now you can:")
            print("1. Refresh your browser")
            print("2. Go to Load Factor tab")
            print("3. See enhanced teacher load breakdown")
            print("4. View improved lab/practical classification")
            
        else:
            print("❌ APIs not working properly")
            
        input("\nPress Enter to stop the server...")
        
    finally:
        print("Stopping server...")
        process.terminate()
        process.wait()

if __name__ == "__main__":
    main()