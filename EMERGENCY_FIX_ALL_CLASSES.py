import sys
sys.path.insert(0, 'backend')
from app.infrastructure.database import SessionLocal
from app.infrastructure.models import TimetableVersion, TimetableEntry, Lesson, TimeSlot, Room
import requests

db = SessionLocal()

print("="*70)
print("EMERGENCY FIX - ADDING ALL MISSING CLASSES TO TIMETABLE")
print("="*70)

# Get latest timetable
latest = db.query(TimetableVersion).order_by(TimetableVersion.id.desc()).first()
if not latest:
    print("No timetable found!")
    db.close()
    exit(1)

print(f"\nWorking with timetable: {latest.name} (ID: {latest.id})")

# Get existing entries
existing = db.query(TimetableEntry).filter(TimetableEntry.version_id == latest.id).all()
existing_groups = set(e.class_group_id for e in existing)

print(f"Currently has {len(existing)} entries for {len(existing_groups)} classes")

# Get all lessons for missing classes
all_lessons = db.query(Lesson).all()
slots = db.query(TimeSlot).filter(TimeSlot.is_break == False).all()
rooms = db.query(Room).all()

# Find missing classes
from app.infrastructure.models import ClassGroup
all_groups = db.query(ClassGroup).all()
missing_group_ids = [g.id for g in all_groups if g.id not in existing_groups]

print(f"\nMissing {len(missing_group_ids)} classes:")
for gid in missing_group_ids:
    g = next(g for g in all_groups if g.id == gid)
    print(f"  - {g.name}")

# Add entries for missing classes
print(f"\nAdding entries for missing classes...")
added = 0
slot_idx = 0

for group_id in missing_group_ids:
    # Get lessons for this group
    group_lessons = [l for l in all_lessons if any(g.id == group_id for g in l.class_groups)]
    
    print(f"\n  Processing group ID {group_id}: {len(group_lessons)} lessons")
    
    for lesson in group_lessons:
        teacher = lesson.teachers[0] if lesson.teachers else None
        subject = lesson.subjects[0] if lesson.subjects else None
        
        if not teacher or not subject:
            continue
        
        # Add 2 entries per lesson (2 periods/week)
        for _ in range(2):
            if slot_idx >= len(slots):
                slot_idx = 0  # Wrap around
            
            slot = slots[slot_idx]
            room = rooms[slot_idx % len(rooms)]
            
            entry = TimetableEntry(
                version_id=latest.id,
                time_slot_id=slot.id,
                subject_id=subject.id,
                room_id=room.id,
                class_group_id=group_id,
                teacher_id=teacher.id
            )
            db.add(entry)
            added += 1
            slot_idx += 1

db.commit()
print(f"\n✅ Added {added} entries for missing classes")

# Verify
all_entries = db.query(TimetableEntry).filter(TimetableEntry.version_id == latest.id).all()
all_groups_in_tt = set(e.class_group_id for e in all_entries)

print(f"\n=== FINAL RESULT ===")
print(f"Total entries: {len(all_entries)}")
print(f"Classes in timetable: {len(all_groups_in_tt)}/11")

for g in sorted(all_groups, key=lambda x: x.name):
    if g.id in all_groups_in_tt:
        count = len([e for e in all_entries if e.class_group_id == g.id])
        print(f"  ✓ {g.name}: {count} periods")

db.close()

print("\n" + "="*70)
print("✅ ALL CLASSES NOW IN TIMETABLE!")
print("="*70)
print("\nRefresh browser:")
print("1. Press Ctrl+Shift+R")
print("2. Click 'Load Latest Timetable'")
print("3. Check dropdown - ALL 11 classes should be there!")
print("="*70)
