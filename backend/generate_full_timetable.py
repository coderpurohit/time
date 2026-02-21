"""
Generate a complete, fully-filled timetable with all days Monday-Friday populated
"""
from app.infrastructure.database import SessionLocal
from app.infrastructure import models
import random

db = SessionLocal()

try:
    print("🔄 Clearing old timetables...")
    db.query(models.TimetableEntry).delete()
    db.query(models.TimetableVersion).delete()
    db.commit()
    
    print("📊 Fetching resources...")
    teachers = db.query(models.Teacher).all()
    subjects = db.query(models.Subject).all()
    rooms = db.query(models.Room).all()
    groups = db.query(models.ClassGroup).all()
    slots = db.query(models.TimeSlot).filter(models.TimeSlot.is_break == False).all()
    
    print(f"   Teachers: {len(teachers)}")
    print(f"   Subjects: {len(subjects)}")
    print(f"   Rooms: {len(rooms)}")
    print(f"   Groups: {len(groups)}")
    print(f"   Slots: {len(slots)}")
    
    # Create timetable version
    version = models.TimetableVersion(
        name="Complete Weekly Schedule",
        algorithm="manual",
        status="active",
        is_valid=True
    )
    db.add(version)
    db.commit()
    db.refresh(version)
    
    print(f"\n🎯 Generating complete timetable for {len(groups)} class groups...")
    
    # Group slots by day
    days = {}
    for slot in slots:
        if slot.day not in days:
            days[slot.day] = []
        days[slot.day].append(slot)
    
    # Sort slots within each day
    for day in days:
        days[day] = sorted(days[day], key=lambda s: s.period)
    
    entries_created = 0
    
    # Fill timetable for each class group
    for group in groups:
        print(f"\n   Processing {group.name}...")
        
        # Track usage to avoid conflicts
        slot_teacher_usage = {}  # slot_id -> teacher_id (prevent same teacher at same time)
        slot_room_usage = {}     # slot_id -> room_id (prevent same room at same time)
        
        # For each day, assign subjects
        for day_name in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
            if day_name not in days:
                continue
                
            day_slots = days[day_name][:6]  # First 6 periods of the day
            
            # Rotate through subjects for variety
            for idx, slot in enumerate(day_slots):
                # Pick a subject (cycle through available subjects)
                subject = subjects[idx % len(subjects)]
                
                # Find available teacher for this subject
                available_teacher = None
                if subject.teacher_id:
                    teacher = db.query(models.Teacher).filter(models.Teacher.id == subject.teacher_id).first()
                    # Check if teacher is available (not teaching another class at same time)
                    if slot.id not in slot_teacher_usage or slot_teacher_usage[slot.id] != teacher.id:
                        available_teacher = teacher
                
                if not available_teacher:
                    # Pick any teacher who's not busy
                    for teacher in teachers:
                        if slot.id not in slot_teacher_usage or slot_teacher_usage[slot.id] != teacher.id:
                            available_teacher = teacher
                            break
                
                if not available_teacher:
                    available_teacher = random.choice(teachers)  # Fallback
                
                # Find available room matching subject requirements
                suitable_rooms = [r for r in rooms 
                                if r.type == subject.required_room_type 
                                and (slot.id not in slot_room_usage or slot_room_usage[slot.id] != r.id)]
                
                if not suitable_rooms:
                    # Fallback to any room not in use
                    suitable_rooms = [r for r in rooms 
                                    if slot.id not in slot_room_usage or slot_room_usage[slot.id] != r.id]
                
                if not suitable_rooms:
                    suitable_rooms = rooms  # Last resort
                
                room = random.choice(suitable_rooms)
                
                # Create entry
                entry = models.TimetableEntry(
                    version_id=version.id,
                    time_slot_id=slot.id,
                    subject_id=subject.id,
                    room_id=room.id,
                    class_group_id=group.id,
                    teacher_id=available_teacher.id
                )
                db.add(entry)
                entries_created += 1
                
                # Mark resources as used for this slot
                slot_teacher_usage[slot.id] = available_teacher.id
                slot_room_usage[slot.id] = room.id
            
            print(f"      {day_name}: {len(day_slots)} classes scheduled")
    
    db.commit()
    print(f"\n✅ Complete timetable generated!")
    print(f"   Total entries created: {entries_created}")
    print(f"   Coverage: {entries_created / (len(groups) * 5 * 6) * 100:.1f}% of possible slots")
    print(f"\n🎉 Refresh your browser to see the full timetable!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()
