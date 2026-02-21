"""
Generate a complete timetable using the backend API
"""
import requests

try:
    print("🚀 Triggering timetable generation...")
    response = requests.post(
        "http://localhost:8000/api/solvers/generate",
        params={
            "method": "csp",
            "name": "Complete Weekly Schedule"
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ Generation started successfully!")
        print(f"   Version ID: {data['id']}")
        print(f"   Name: {data['name']}")
        print(f"   Algorithm: {data['algorithm']}")
        print(f"   Status: {data['status']}")
        print(f"\n⏳ Waiting for generation to complete...")
        
        # Wait a moment for generation
        import time
        time.sleep(8)
        
        # Check the latest timetable
        latest = requests.get("http://localhost:8000/api/timetables/latest")
        if latest.status_code == 200:
            timetable = latest.json()
            print(f"\n📊 Latest Timetable:")
            print(f"   Name: {timetable['name']}")
            print(f"   Status: {timetable['status']}")
            print(f"   Valid: {timetable['is_valid']}")
            print(f"   Entries: {len(timetable['entries'])}")
            print(f"\n🎉 Timetable generated! Refresh your browser to see it.")
        else:
            print(f"⚠️  Could not fetch latest timetable")
    else:
        print(f"❌ Generation failed: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"❌ Error: {e}")
