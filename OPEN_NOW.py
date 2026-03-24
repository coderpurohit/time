#!/usr/bin/env python3
import webbrowser
import os

# Force open the URL immediately
url = 'http://localhost:8000/dynamic_academic_management.html'
print(f"🚀 OPENING: {url}")

# Try multiple methods to open
try:
    webbrowser.open(url)
    print("✅ OPENED!")
except:
    os.system(f'start {url}')
    print("✅ OPENED WITH START!")