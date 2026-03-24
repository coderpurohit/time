#!/usr/bin/env python3
import webbrowser
import time
import subprocess
import sys

def force_open():
    url = 'http://localhost:8000/dynamic_academic_management.html'
    print(f"🚀 FORCE OPENING: {url}")
    
    # Method 1: Default browser
    try:
        webbrowser.open(url, new=2)
        print("✅ Opened with webbrowser")
    except Exception as e:
        print(f"❌ webbrowser failed: {e}")
    
    # Method 2: Windows start command
    try:
        subprocess.run(['cmd', '/c', 'start', url], check=True)
        print("✅ Opened with cmd start")
    except Exception as e:
        print(f"❌ cmd start failed: {e}")
    
    # Method 3: Direct browser launch
    browsers = [
        r'C:\Program Files\Google\Chrome\Application\chrome.exe',
        r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
        r'C:\Program Files\Mozilla Firefox\firefox.exe',
        r'C:\Program Files (x86)\Mozilla Firefox\firefox.exe',
        r'C:\Program Files\Microsoft\Edge\Application\msedge.exe'
    ]
    
    for browser in browsers:
        try:
            subprocess.Popen([browser, url])
            print(f"✅ Opened with {browser}")
            break
        except:
            continue
    
    print(f"\n🌐 URL: {url}")
    print("📋 If browser doesn't open, manually copy the URL above")
    print("🔧 Make sure backend is running: cd backend && start.bat")

if __name__ == "__main__":
    force_open()