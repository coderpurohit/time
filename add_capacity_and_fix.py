import sys
sys.path.insert(0, 'backend')
from app.infrastructure.database import SessionLocal
from app.infrastructure.models import TimeSlot, Room
import requests
import time

db = SessionLocal()

print("=== ADDING CAPACITY ===")

# 1. Add Saturday slots
print("\n1. Adding Saturday time slots...")
existing_saturday = db.query(TimeSlot).filter(TimeSlot.day == 'Saturday').count()
if existing_saturday == 0:
    for period in range(1, 8):
        start_hour = 9 + (period - 1)
        slot = TimeSlot(
            day='Saturday',
            period=period,
            start_time=f'{start_hour:02d}:00',
            end_time=f'{start_hour+1:02d}:00',
            is_break=False
        )
        db.add(slot)
    db.commit()
    print(f"   ✅ Added 7 Saturday periods")
else:
    print(f"   ⏭️  Saturday already has {existing_saturday} slots")

# 2. Add more rooms
print("\n2. Adding more rooms...")
existing_rooms = db.query(Room).count()
print(f"   Current rooms: {existing_rooms}")

if existing_rooms < 15:
    rooms_to_add = [
        ('Room 201', 60, 'Lecture'),
        ('Room 202', 60, 'Lecture'),
        ('Room 203', 60, 'Lecture'),
        ('Lab 301', 40, 'Lab'),
        ('Lab 302', 40, 'Lab'),
    ]
    
    for name, capacity, room_type in rooms_to_add:
        existing = db.query(Room).filter(Room.name == name).first()
        if not existing:
            room = Room(name=name, capacity=capacity, room_type=room_type)
            db.add(room)
    
    db.commit()
    new_count = db.query(Room).count()
    print(f"   ✅ Now have {new_count} rooms")
else:
    print(f"   ✅ Already have {existing_rooms} rooms")

# 3. Check capacity
slots = db.query(TimeSlot).filter(TimeSlot.is_break == False).count()
rooms = db.query(Room).count()
days = len(set(s.day for s in db.query(TimeSlot).all()))

print(f"\n3. New capacity:")
print(f"   Days: {days}")
print(f"   Slots: {slots}")
print(f"   Rooms: {rooms}")
print(f"   Total: {slots * rooms} slot-room combinations")

db.close()

# 4. Regenerate timetable
print("\n4. Regenerating timetable with new capacity...")
r = requests.post('http://localhost:8000/api/solvers/generate', json={'method': 'csp'})
print(f"   Started: {r.status_code}")

print("   Waiting 20 seconds...")
time.sleep(20)

# 5. Check result
r = requests.get('http://localhost:8000/api/timetables/latest')
data = r.json()
entries = data.get('entries', [])
groups = set(e['class_group']['name'] for e in entries if e.get('class_group'))

print(f"\n5. Result:")
print(f"   Total entries: {len(entries)}")
print(f"   Classes scheduled: {len(groups)}/11")
for g in sorted(groups):
    print(f"     ✓ {g}")

if len(groups) < 11:
    print(f"\n   ⚠️  Still missing {11 - len(groups)} classes")
    r2 = requests.get('http://localhost:8000/api/operational/class-groups')
    all_groups = {g['name'] for g in r2.json()}
    missing = all_groups - groups
    for m in sorted(missing):
        print(f"     ❌ {m}")
else:
    print(f"\n   ✅ ALL CLASSES SCHEDULED!")

print("\n" + "="*60)
print("DONE! Refresh browser and load latest timetable")
print("="*60)
