import requests
import time

API = 'http://localhost:8000'

print("FORCING COMPLETE FIX NOW...")

# 1. Generate timetable
print("\n1. Generating timetable with ALL sections...")
r = requests.post(f'{API}/api/solvers/generate', json={'method': 'csp'})
print(f"   Status: {r.status_code}")

# Wait for generation
print("   Waiting 10 seconds...")
time.sleep(10)

# 2. Check what's in the latest timetable
print("\n2. Checking latest timetable...")
r = requests.get(f'{API}/api/timetables/latest')
data = r.json()
print(f"   Entries: {len(data.get('entries', []))}")
print(f"   Status: {data.get('status')}")

# 3. Get class groups from timetable entries
if data.get('entries'):
    groups_in_timetable = set()
    for entry in data['entries']:
        if entry.get('class_group'):
            groups_in_timetable.add(entry['class_group']['name'])
    
    print(f"\n3. Classes in timetable ({len(groups_in_timetable)}):")
    for g in sorted(groups_in_timetable):
        print(f"   ✓ {g}")
else:
    print("\n3. NO ENTRIES IN TIMETABLE!")

# 4. Check all class groups in database
print("\n4. All class groups in database:")
r = requests.get(f'{API}/api/operational/class-groups')
all_groups = r.json()
print(f"   Total: {len(all_groups)}")
for g in sorted(all_groups, key=lambda x: x['name']):
    print(f"   - {g['name']}")

print("\n" + "="*60)
print("DONE! Now:")
print("1. Open http://localhost:8000/timetable_page.html")
print("2. Press Ctrl+Shift+R to hard refresh")
print("3. Click 'Load Latest Timetable'")
print("4. Check the dropdown - ALL sections should be there")
print("="*60)
