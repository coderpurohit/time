import requests
import time

API = 'http://localhost:8000'

print("="*60)
print("COMPLETE TIMETABLE REGENERATION")
print("="*60)

# Generate with longer wait
print("\nGenerating timetable for ALL 14 classes...")
r = requests.post(f'{API}/api/solvers/generate', json={'method': 'csp'})
print(f"Started: {r.status_code}")

print("Waiting 20 seconds for solver to complete...")
for i in range(20, 0, -1):
    print(f"  {i}...", end='\r')
    time.sleep(1)

print("\n\nChecking result...")
r = requests.get(f'{API}/api/timetables/latest')
data = r.json()

print(f"Status: {data.get('status')}")
print(f"Total entries: {len(data.get('entries', []))}")

if data.get('entries'):
    groups = {}
    for entry in data['entries']:
        if entry.get('class_group'):
            name = entry['class_group']['name']
            groups[name] = groups.get(name, 0) + 1
    
    print(f"\nClasses in timetable: {len(groups)}")
    for name in sorted(groups.keys()):
        print(f"  ✓ {name}: {groups[name]} periods")
    
    if len(groups) < 11:
        print(f"\n⚠️  WARNING: Only {len(groups)}/11 classes scheduled!")
        print("Missing classes:")
        r2 = requests.get(f'{API}/api/operational/class-groups')
        all_groups = {g['name'] for g in r2.json()}
        missing = all_groups - set(groups.keys())
        for m in sorted(missing):
            print(f"  ❌ {m}")
    else:
        print(f"\n✅ ALL {len(groups)} CLASSES SCHEDULED!")
else:
    print("\n❌ NO ENTRIES GENERATED!")

print("\n" + "="*60)
print("NOW OPEN: http://localhost:8000/timetable_page.html")
print("Press Ctrl+Shift+R, then click 'Load Latest Timetable'")
print("="*60)
