
import sys
import os
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend directory to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.infrastructure.database import Base
from app.infrastructure.models import TimetableVersion, TimetableEntry, Teacher, Subject, Room, ClassGroup, TimeSlot
from app.solver.csp_solver import CspTimetableSolver

def generate_and_save():
    print("🔧 Connecting to database...")
    # Force usage of backend/timetable.db
    SQLALCHEMY_DATABASE_URL = "sqlite:///backend/timetable.db"
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        # Load Data
        print("📥 Loading data...")
        teachers = db.query(Teacher).all()
        subjects = db.query(Subject).all()
        rooms = db.query(Room).all()
        groups = db.query(ClassGroup).all()
        slots = db.query(TimeSlot).all()

        print(f"Loaded: {len(teachers)} Teachers, {len(subjects)} Subjects, {len(rooms)} Rooms, {len(groups)} Groups, {len(slots)} Slots")

        # Initialize Solver
        print("🧠 Initializing Solver...")
        solver = CspTimetableSolver(teachers, subjects, rooms, groups, slots)

        # Solve
        print("🧩 Solving...")
        schedule = solver.solve()

        if schedule:
            print(f"✅ Solution Found! {len(schedule)} assignments.")
            
            # Create new version
            version = TimetableVersion(
                created_at=datetime.now(),
                name=f"Generated {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                algorithm="CSP",
                status="active",
                is_valid=True
            )
            db.add(version)
            db.commit()
            db.refresh(version)
            print(f"💾 Created Timetable Version: {version.id}")

            # Save entries
            count = 0
            for entry in schedule:
                # Entry keys: class_group_id, subject_id, room_id, time_slot_id, teacher_id
                
                db_entry = TimetableEntry(
                    version_id=version.id,
                    time_slot_id=entry['time_slot_id'],
                    class_group_id=entry['class_group_id'],
                    subject_id=entry['subject_id'],
                    room_id=entry['room_id'],
                    teacher_id=entry['teacher_id']
                )
                db.add(db_entry)
                count += 1
            
            db.commit()
            print(f"💾 Saved {count} entries to database.")
            
            # Print a snippet of the timetable
            print("\n📋 Timetable Snippet (Monday):")
            
            # Helper to get slot details
            def get_slot_details(tid):
                return next((s for s in slots if s.id == tid), None)

            # Sort and filter
            monday_entries = []
            for e in schedule:
                slot = get_slot_details(e['time_slot_id'])
                if slot and slot.day == 'Monday':
                    monday_entries.append((e, slot))
            
            monday_entries.sort(key=lambda x: (x[0]['class_group_id'], x[1].period))
            
            for e, slot in monday_entries[:10]: # Print first 10
                 # Find names
                g_name = next((g.name for g in groups if g.id == e['class_group_id']), "Unknown")
                s_name = next((s.name for s in subjects if s.id == e['subject_id']), "Unknown")
                r_name = next((r.name for r in rooms if r.id == e['room_id']), "Unknown")
                print(f"  {g_name} | Period {slot.period} | {s_name} | {r_name}")

        else:
            print("❌ No Solution Found")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    generate_and_save()
