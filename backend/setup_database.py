"""
Complete database initialization and seeding script
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.infrastructure import models
from app.infrastructure.database import SQLALCHEMY_DATABASE_URL

def init_and_seed():
    # Create engine and session
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
    
    # Drop all tables and recreate (fresh start)
    print("🔄 Resetting database...")
    models.Base.metadata.drop_all(bind=engine)
    models.Base.metadata.create_all(bind=engine)
    print("✅ Database tables created!")
    
    # Create session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        print("\n📊 Adding sample data...")
        
        # 1. Time Slots (Mon-Fri, 9AM-5PM)
        print("  ⏰ Adding time slots...")
        slots = []
        for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
            for i in range(1, 9):  # 8 periods
                slots.append(models.TimeSlot(
                    day=day,
                    period=i,
                    start_time=f"{8+i}:00",
                    end_time=f"{9+i}:00",
                    is_break=(i == 4)  # Lunch break at period 4
                ))
        db.add_all(slots)
        db.commit()
        print(f"    ✓ Added {len(slots)} time slots")
        
        # 2. Teachers
        print("  👨‍🏫 Adding teachers...")
        teachers = [
            models.Teacher(name="Dr. Rajesh Kumar", email="rajesh.kumar@college.edu", max_hours_per_week=18),
            models.Teacher(name="Prof. Priya Sharma", email="priya.sharma@college.edu", max_hours_per_week=16),
            models.Teacher(name="Dr. Amit Patel", email="amit.patel@college.edu", max_hours_per_week=15),
            models.Teacher(name="Dr. Sneha Desai", email="sneha.desai@college.edu", max_hours_per_week=14),
            models.Teacher(name="Prof. Vikram Singh", email="vikram.singh@college.edu", max_hours_per_week=16),
        ]
        db.add_all(teachers)
        db.commit()
        print(f"    ✓ Added {len(teachers)} teachers")
        
        # 3. Rooms
        print("  🏫 Adding rooms...")
        rooms = [
            models.Room(name="Room 101", capacity=60, type="LectureHall", resources=["Projector", "Whiteboard"]),
            models.Room(name="Room 102", capacity=60, type="LectureHall", resources=["Projector", "Whiteboard"]),
            models.Room(name="Lab 401", capacity=40, type="ComputerLab", resources=["Computers", "Projector"]),
            models.Room(name="Lab 402", capacity=40, type="ComputerLab", resources=["Computers", "Projector"]),
            models.Room(name="Conference Hall", capacity=100, type="Auditorium", resources=["Projector", "Sound System"]),
        ]
        db.add_all(rooms)
        db.commit()
        print(f"    ✓ Added {len(rooms)} rooms")
        
        # 4. Class Groups
        print("  👥 Adding class groups...")
        groups = [
            models.ClassGroup(name="SE-AI-DS-A", student_count=60),
            models.ClassGroup(name="SE-AI-DS-B", student_count=55),
            models.ClassGroup(name="TE-AI-DS-A", student_count=50),
        ]
        db.add_all(groups)
        db.commit()
        print(f"    ✓ Added {len(groups)} class groups")
        
        # 5. Subjects
        print("  📚 Adding subjects...")
        subjects = [
            models.Subject(name="Data Structures", code="CS301", is_lab=False, credits=4, 
                          required_room_type="LectureHall", duration_slots=1, teacher_id=1),
            models.Subject(name="Database Management", code="CS302", is_lab=False, credits=3,
                          required_room_type="LectureHall", duration_slots=1, teacher_id=2),
            models.Subject(name="Database Lab", code="CS302L", is_lab=True, credits=2,
                          required_room_type="ComputerLab", duration_slots=2, teacher_id=2),
            models.Subject(name="Machine Learning", code="CS401", is_lab=False, credits=4,
                          required_room_type="LectureHall", duration_slots=1, teacher_id=3),
            models.Subject(name="ML Lab", code="CS401L", is_lab=True, credits=2,
                          required_room_type="ComputerLab", duration_slots=2, teacher_id=3),
            models.Subject(name="Web Development", code="CS303", is_lab=False, credits=3,
                          required_room_type="LectureHall", duration_slots=1, teacher_id=4),
            models.Subject(name="Software Engineering", code="SE201", is_lab=False, credits=4,
                          required_room_type="LectureHall", duration_slots=1, teacher_id=5),
            models.Subject(name="SE Project Lab", code="SE201L", is_lab=True, credits=3,
                          required_room_type="ComputerLab", duration_slots=2, teacher_id=5),
        ]
        db.add_all(subjects)
        db.commit()
        print(f"    ✓ Added {len(subjects)} subjects")
        
        print("\n✅ Database seeding complete!")
        print("\n📈 Summary:")
        print(f"   - Time Slots: {len(slots)}")
        print(f"   - Teachers: {len(teachers)}")
        print(f"   - Rooms: {len(rooms)}")
        print(f"   - Class Groups: {len(groups)}")
        print(f"   - Subjects: {len(subjects)}")
        print("\n🚀 Ready to generate timetables!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_and_seed()
