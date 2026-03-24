#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.infrastructure.database import SessionLocal
from backend.app.infrastructure import models
from backend.app.services.timetable_service import TimetableService
import random

def generate_simple_timetable():
    """Generate a simple timetable using the service"""
    db = SessionLocal()
    try:
        print("🔧 GENERATING SIMPLE TIMETABLE")
        
        # Get data
        teachers = db.query(models.Teacher).all()
        subjects = db.query(models.Subject).all()
        classes = db.query(models.ClassGroup).all()
        rooms = db.query(models.Room).all()
        time_slots = db.query(models.TimeSlot).all()
        
        print(f"📊 Available data:")
        print(f"   - Teachers: {len(teachers)}")
        print(f"   - Subjects: {len(subjects)}")
        print(f"   - Classes: {len(classes)}")
        print(f"   - Rooms: {len(rooms)}")
        print(f"   - Time slots: {len(time_slots)}")
        
        if not all([teachers, subjects, classes, rooms, time_slots]):
            print("❌ Missing required data")
            return False
        
        # Create timetable version
        version = models.TimetableVersion(
            name="Simple Generated Timetable"
        )
        db.add(version)
        db.flush()
        
        # Generate entries using simple assignment
        entries_created = 0
        
        for class_group in classes:
            for subject in subjects[:6]:  # Limit to 6 subjects per class
                for slot in time_slots[:5]:  # Use first 5 time slots
                    # Find available teacher
                    teacher = random.choice([t for t in teachers if t.id == subject.teacher_id] or teachers[:3])
                    room = random.choice(rooms)
                    
                    entry = models.TimetableEntry(
                        version_id=version.id,
                        class_group_id=class_group.id,
                        subject_id=subject.id,
                        teacher_id=teacher.id,
                        room_id=room.id,
                        time_slot_id=slot.id
                    )
                    db.add(entry)
                    entries_created += 1
                    
                    if entries_created >= 30:  # Limit total entries
                        break
                if entries_created >= 30:
                    break
            if entries_created >= 30:
                break
        
        db.commit()
        
        print(f"✅ Timetable generated successfully!")
        print(f"   - Version ID: {version.id}")
        print(f"   - Entries created: {entries_created}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    if generate_simple_timetable():
        print("\n🎉 TIMETABLE READY!")
        print("✅ Load Factor Engine should now show data")
        print("🔄 Refresh the page to see the results!")
    else:
        print("\n❌ Generation failed")