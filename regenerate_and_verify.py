import requests
import time

API_BASE = 'http://localhost:8000'

print("=== REGENERATING TIMETABLE ===")

# Generate new timetable
print("\n1. Generating timetable...")
response = requests.post(f'{API_BASE}/api/solvers/generate', json={'method': 'csp'})
if response.status_code == 200:
    print("✅ Timetable generation started")
    time.sleep(3)  # Wait for generation
else:
    print(f"❌ Generation failed: {response.status_code}")
    print(response.text)
    exit(1)

# Load latest timetable
print("\n2. Loading latest timetable...")
response = requests.get(f'{API_BASE}/api/timetables/latest')
if response.status_code == 200:
    timetable = response.json()
    print(f"✅ Timetable loaded: {timetable.get('name', 'Latest')}")
    print(f"   Status: {timetable.get('status', 'unknown')}")
    print(f"   Entries: {len(timetable.get('entries', []))}")
else:
    print(f"❌ Failed to load timetable: {response.status_code}")
    exit(1)

# Check load factor
print("\n3. Checking load factor...")
response = requests.get(f'{API_BASE}/api/analytics/load-factor')
if response.status_code == 200:
    data = response.json()
    print(f"✅ Load factor data retrieved")
    print(f"\n📊 Summary:")
    print(f"   Total Teachers: {data['summary']['total_teachers']}")
    print(f"   Total Classes: {data['summary']['total_classes']}")
    print(f"   Total Periods: {data['summary']['total_periods']}")
    print(f"   Avg Teacher Load: {data['summary']['avg_teacher_load']}")
    
    print(f"\n👨‍🏫 Teacher Assignments:")
    for teacher in data['teacher_load'][:15]:  # Show first 15
        print(f"   {teacher['name']}: {teacher['total_periods']} periods ({teacher['load_percentage']}%)")
    
    # Check if bharat and hari have assignments
    bharat = next((t for t in data['teacher_load'] if 'bharat' in t['name'].lower()), None)
    hari = next((t for t in data['teacher_load'] if 'hari' in t['name'].lower()), None)
    
    if bharat:
        print(f"\n✅ BHARAT: {bharat['total_periods']} periods assigned")
    else:
        print(f"\n⚠️  BHARAT: Not found in load factor data")
    
    if hari:
        print(f"✅ HARI: {hari['total_periods']} periods assigned")
    else:
        print(f"⚠️  HARI: Not found in load factor data")
        
else:
    print(f"❌ Failed to get load factor: {response.status_code}")

# Check class groups
print("\n4. Checking class groups...")
response = requests.get(f'{API_BASE}/api/operational/class-groups')
if response.status_code == 200:
    groups = response.json()
    print(f"✅ Class groups: {len(groups)}")
    for group in groups:
        print(f"   - {group['name']} ({group['student_count']} students)")
else:
    print(f"❌ Failed to get class groups: {response.status_code}")

print("\n✅ VERIFICATION COMPLETE!")
print("\nNow open: http://localhost:8000/timetable_page.html")
print("- Click 'Load Latest Timetable' to see the schedule")
print("- Go to 'Load Factor' tab to see teacher assignments")
print("- Go to 'Classes/Grades' tab to see all divisions")
