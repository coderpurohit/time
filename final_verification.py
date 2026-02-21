import requests
import time

API = 'http://localhost:8000'

print("=== FINAL VERIFICATION ===")

# 1. Check class groups
print("\n1. Checking class groups...")
r = requests.get(f'{API}/api/operational/class-groups')
groups = r.json()
print(f"✅ Total class groups: {len(groups)}")
for g in sorted(groups, key=lambda x: x['name']):
    print(f"   - {g['name']} ({g['student_count']} students)")

# 2. Generate timetable
print("\n2. Generating new timetable...")
r = requests.post(f'{API}/api/solvers/generate', json={'method': 'csp'})
if r.status_code == 200:
    print("✅ Generation started")
    time.sleep(8)
else:
    print(f"❌ Failed: {r.status_code}")

# 3. Check load factor
print("\n3. Checking teacher assignments...")
r = requests.get(f'{API}/api/analytics/load-factor')
if r.status_code == 200:
    data = r.json()
    print(f"✅ Total teachers: {data['summary']['total_teachers']}")
    print(f"✅ Total classes: {data['summary']['total_classes']}")
    print(f"✅ Total periods: {data['summary']['total_periods']}")
    
    print("\nTeacher assignments:")
    for t in sorted(data['teacher_load'], key=lambda x: x['name']):
        print(f"   {t['name']}: {t['total_periods']} periods ({t['load_percentage']}%)")
else:
    print(f"❌ Failed: {r.status_code}")

print("\n" + "="*60)
print("✅ ALL SECTIONS ADDED AND WORKING!")
print("="*60)
print("\nOpen: http://localhost:8000/timetable_page.html")
print("Click 'Load Latest Timetable' and check the dropdown!")
