"""
Populate database with comprehensive data for complete timetable generation
"""
from app.infrastructure.database import SessionLocal
from app.infrastructure import models

db = SessionLocal()

try:
    # Clear existing data for fresh start
    print("🗑️  Clearing existing timetable data...")
    db.query(models.TimetableEntry).delete()
    db.query(models.TimetableVersion).delete()
    db.commit()
    
    # Ensure we have enough teachers (at least 10)
    teacher_count = db.query(models.Teacher).count()
    if teacher_count < 10:
        print(f"📚 Adding more teachers (current: {teacher_count})...")
        additional_teachers = [
            models.Teacher(name="Dr. Meena Joshi", email="meena.joshi@college.edu", max_hours_per_week=20),
            models.Teacher(name="Prof. Karan Mehta", email="karan.mehta@college.edu", max_hours_per_week=18),
            models.Teacher(name="Dr. Sunita Reddy", email="sunita.reddy@college.edu", max_hours_per_week=20),
            models.Teacher(name="Prof. Arjun Nair", email="arjun.nair@college.edu", max_hours_per_week=18),
        ]
        db.add_all(additional_teachers)
        db.commit()
    
    # Ensure we have enough subjects (at least 8)
    subject_count = db.query(models.Subject).count()
    print(f"📖 Current subjects: {subject_count}")
    
    # Ensure we have enough rooms (at least 8)
    room_count = db.query(models.Room).count()
    if room_count < 8:
        print(f"🏫 Adding more rooms (current: {room_count})...")
        additional_rooms = [
            models.Room(name="Room 201", capacity=50, type="LectureHall", resources=["Projector", "Whiteboard"]),
            models.Room(name="Room 202", capacity=50, type="LectureHall", resources=["Projector", "Whiteboard"]),
            models.Room(name="Lab 501", capacity=30, type="ComputerLab", resources=["Computers", "Projector"]),
        ]
        db.add_all(additional_rooms)
        db.commit()
    
    # Check class groups
    group_count = db.query(models.ClassGroup).count()
    print(f"👥 Class groups: {group_count}")
    
    # Check time slots
    slot_count = db.query(models.TimeSlot).count()
    print(f"⏰ Time slots: {slot_count}")
    
    print("\n" + "="*50)
    print("✅ Database populated successfully!")
    print("="*50)
    print(f"\n📊 Final counts:")
    print(f"   Teachers: {db.query(models.Teacher).count()}")
    print(f"   Subjects: {db.query(models.Subject).count()}")
    print(f"   Rooms: {db.query(models.Room).count()}")
    print(f"   Class Groups: {db.query(models.ClassGroup).count()}")
    print(f"   Time Slots: {db.query(models.TimeSlot).count()}")
    print(f"\n💡 Now generate a new timetable from the frontend!")
    print(f"   It should create approximately {group_count * 6 * 5} entries")
    print(f"   (3 classes × 6 periods/day × 5 days = ~90 entries)")
    
except Exception as e:
    print(f"❌ Error: {e}")
    db.rollback()
finally:
    db.close()
