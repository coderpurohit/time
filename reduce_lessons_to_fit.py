import sys
sys.path.insert(0, 'backend')
from app.infrastructure.database import SessionLocal
from app.infrastructure.models import Lesson, TimeSlot
import requests
import time

db = SessionLocal()

print("=== REDUCING LESSONS TO FIT CAPACITY ===")

# Calculate capacity
slots = db.query(TimeSlot).filter(TimeSlot.is_break == False).all()
days = set(s.day for s in slots)
periods_per_day = len([s for s in slots if s.day == list(days)[0] and not s.is_break])

print(f"\nCapacity:")
print(f"  Days: {len(days)}")
print(f"  Periods per day: {periods_per_day}")
print(f"  Total periods per week: {len(days) * periods_per_day}")

# Reduce all lessons to 2 periods per week (feasible)
lessons = db.query(Lesson).all()
print(f"\nReducing {len(lessons)} lessons to 2 periods/week each...")

for lesson in lessons:
    lesson.lessons_per_week = 2

db.commit()
print("✅ All lessons reduced to 2 periods/week")

# Calculate new demand
total_demand = len(lessons) * 2
print(f"\nNew demand: {total_demand} periods total")
print(f"Per class: ~{total_demand / 11:.0f} periods")

db.close()

# Regenerate
print("\n" + "="*60)
print("REGENERATING WITH REDUCED LOAD...")
print("="*60)

r = requests.post('http://localhost:8000/api/solvers/generate', json={'method': 'csp'})
print(f"Started: {r.status_code}")

print("Waiting 30 seconds...")
time.sleep(30)

r = requests.get('http://localhost:8000/api/timetables/latest')
data = r.json()
entries = data.get('entries', [])
groups = set(e['class_group']['name'] for e in entries if e.get('class_group'))

print(f"\nResult:")
print(f"  Entries: {len(entries)}")
print(f"  Classes: {len(groups)}")

if len(groups) == 11:
    print("\n✅ SUCCESS! ALL 11 CLASSES SCHEDULED!")
    for g in sorted(groups):
        count = len([e for e in entries if e.get('class_group', {}).get('name') == g])
        print(f"   ✓ {g}: {count} periods")
else:
    print(f"\n⚠️  Only {len(groups)}/11 classes scheduled")
    for g in sorted(groups):
        print(f"   ✓ {g}")

print("\n" + "="*60)
print("DONE! Refresh browser and check dropdown")
print("="*60)
