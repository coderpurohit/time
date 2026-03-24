"""
Force Generate a Working Timetable
"""

import requests
import time

API_BASE = 'http://localhost:8000/api'

print("=" * 60)
print("FORCE GENERATING TIMETABLE")
print("=" * 60)

# Step 1: Check prerequisites
print("\n1. Checking prerequisites...")
checks = {
    'teachers': f'{API_BASE}/teachers',
    'subjects': f'{API_BASE}/subjects',
    'classes': f'{API_BASE}/class-groups',
    'rooms': f'{API_BASE}/rooms',
    'time_slots': f'{API_BASE}/operational/time-slots',
    'lessons': f'{API_BASE}/lessons'
}

for name, url in checks.items():
    try:
        resp = requests.get(url)
        if resp.ok:
            data = resp.json()
            count = len(data) if isinstance(data, list) else data.get('total', 0)
            print(f"   ✓ {name}: {count}")
        else:
            print(f"   ❌ {name}: Failed")
    except Exception as e:
        print(f"   ❌ {name}: {e}")

# Step 2: Generate timetable
print("\n2. Generating timetable...")
try:
    response = requests.post(f'{API_BASE}/solvers/generate?method=csp', timeout=60)
    print(f"   Status: {response.status_code}")
    
    if response.ok:
        result = response.json()
        print(f"   ✓ Generation started")
        print(f"   Status: {result.get('status')}")
    else:
        print(f"   ❌ Failed: {response.text}")
        
except Exception as e:
    print(f"   ❌ Error: {e}")

# Step 3: Wait and check result
print("\n3. Waiting for generation to complete...")
time.sleep(5)

try:
    response = requests.get(f'{API_BASE}/timetables/latest')
    if response.ok:
        data = response.json()
        entries = data.get('entries', [])
        print(f"   ✓ Timetable ID: {data.get('id')}")
        print(f"   ✓ Status: {data.get('status')}")
        print(f"   ✓ Entries: {len(entries)}")
        
        if len(entries) == 0:
            print("\n   ❌ TIMETABLE IS EMPTY!")
            print("   This means the solver failed to create any schedule entries.")
            print("\n   Possible causes:")
            print("   - Lessons don't have proper teacher/subject/class associations")
            print("   - Not enough time slots available")
            print("   - Constraints are too strict")
            print("   - Solver encountered an error")
    else:
        print(f"   ❌ Failed to get timetable: {response.text}")
        
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 60)
