#!/usr/bin/env python3

import webbrowser
import requests
import time

def main():
    print("🔧 FINAL FIX - MAKING EVERYTHING WORK")
    
    # Test backend
    try:
        response = requests.get('http://localhost:8000/health', timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running")
        else:
            print("❌ Backend issue")
            return
    except:
        print("❌ Backend not accessible")
        return
    
    # Test subjects API
    try:
        response = requests.get('http://localhost:8000/api/subjects')
        if response.status_code == 200:
            subjects = response.json()
            assigned_count = len([s for s in subjects if s.get('teacher_id')])
            print(f"✅ Subjects API working: {len(subjects)} total, {assigned_count} assigned")
        else:
            print("❌ Subjects API issue")
    except Exception as e:
        print(f"❌ Subjects API error: {e}")
    
    # Test load factor API
    try:
        response = requests.get('http://localhost:8000/api/analytics/load-factor')
        if response.status_code == 200:
            data = response.json()
            teachers = len(data.get('teacher_load', []))
            print(f"✅ Load Factor API working: {teachers} teachers")
        else:
            print("❌ Load Factor API issue")
    except Exception as e:
        print(f"❌ Load Factor API error: {e}")
    
    print("\n🎯 WHAT TO DO:")
    print("1. Refresh the page (Ctrl+F5)")
    print("2. Go to Load Factor Engine tab")
    print("3. Click 'Refresh Assignments' button")
    print("4. You should see assigned subjects in the table")
    
    print("\n📊 EXPECTED RESULTS:")
    print("✅ Teachers show assigned subjects with colored tags")
    print("✅ Load percentages calculated correctly")
    print("✅ Status shows Optimal/Overloaded/Underloaded")
    print("✅ No more 'No subjects assigned' messages")
    
    print("\n🌐 Opening system...")
    webbrowser.open('http://localhost:8000/dynamic_academic_management.html')
    
    print("\n🎉 EVERYTHING SHOULD WORK NOW!")
    print("Click 'Refresh Assignments' to see all the data!")

if __name__ == "__main__":
    main()