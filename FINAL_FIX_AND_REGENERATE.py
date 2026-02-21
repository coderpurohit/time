import requests
import time

API = 'http://localhost:8000'

print("="*70)
print("FINAL FIX - REGENERATING WITH ALL CLASSES")
print("="*70)

print("\n1. Generating timetable...")
r = requests.post(f'{API}/api/solvers/generate', json={'method': 'csp'})
print(f"   Status: {r.status_code}")

if r.status_code != 200:
    print(f"   ERROR: {r.text}")
    exit(1)

print("\n2. Waiting 30 seconds for solver...")
for i in range(30, 0, -1):
    print(f"   {i} seconds remaining...", end='\r')
    time.sleep(1)

print("\n\n3. Checking result...")
r = requests.get(f'{API}/api/timetables/latest')
data = r.json()

entries = data.get('entries', [])
print(f"   Total entries: {len(entries)}")
print(f"   Status: {data.get('status')}")

if entries:
    groups = {}
    for entry in entries:
        if entry.get('class_group'):
            name = entry['class_group']['name']
            groups[name] = groups.get(name, 0) + 1
    
    print(f"\n4. Classes scheduled: {len(groups)}")
    for name in sorted(groups.keys()):
        print(f"   ✓ {name}: {groups[name]} periods")
    
    # Check if all 11 classes are there
    r2 = requests.get(f'{API}/api/operational/class-groups')
    all_groups = {g['name'] for g in r2.json()}
    
    if len(groups) == len(all_groups):
        print(f"\n✅ SUCCESS! ALL {len(groups)} CLASSES SCHEDULED!")
    else:
        missing = all_groups - set(groups.keys())
        print(f"\n⚠️  {len(missing)} classes still missing:")
        for m in sorted(missing):
            print(f"   ❌ {m}")
else:
    print("\n❌ NO ENTRIES GENERATED!")

print("\n" + "="*70)
print("OPEN: http://localhost:8000/timetable_page.html")
print("Press Ctrl+Shift+R, click 'Load Latest Timetable'")
print("All classes should now be in the dropdown!")
print("="*70)
