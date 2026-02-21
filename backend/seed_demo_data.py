"""
Demo Data Seeding Script
Seeds the database with:
- 10 Teachers
- 15 Classrooms (10 Lecture Halls + 5 Labs)
- 5 Core Subjects
- 3 Class Groups
- Time Slots: Monday-Friday, 7 periods (6 teaching + 1 lunch break)
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.infrastructure import models
from app.infrastructure.database import SQLALCHEMY_DATABASE_URL

def clear_database(db):
    """Clear existing data"""
    print("🗑️  Clearing existing data...")
    db.query(models.TimetableEntry).delete()
    db.query(models.TimetableVersion).delete()
    db.query(models.Subject).delete()
    db.query(models.Teacher).delete()
    db.query(models.Room).delete()
    db.query(models.ClassGroup).delete()
    db.query(models.TimeSlot).delete()
    db.commit()
    print("✅ Database cleared")

def seed_demo_data():
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        # Clear existing data
        clear_database(db)
        
        print("\n📊 Seeding Demo Data...")

        # 1. TIME SLOTS (Monday-Friday, 7 periods: 6 teaching + 1 lunch)
        print("  ⏰ Creating time slots...")
        time_slots = []
        periods_info = [
            (1, "9:00", "10:00", False),
            (2, "10:00", "11:00", False),
            (3, "11:00", "12:00", False),
            (4, "12:00", "13:00", True),   # LUNCH BREAK
            (5, "13:00", "14:00", False),
            (6, "14:00", "15:00", False),
            (7, "15:00", "16:00", False),
        ]
        
        for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
            for period, start_time, end_time, is_break in periods_info:
                time_slots.append(models.TimeSlot(
                    day=day,
                    period=period,
                    start_time=start_time,
                    end_time=end_time,
                    is_break=is_break
                ))
        
        db.add_all(time_slots)
        db.commit()
        print(f"    ✓ Added {len(time_slots)} time slots (5 days × 7 periods)")

        # 2. TEACHERS (10 teachers with different specializations)
        print("  👨‍🏫 Creating teachers...")
        teachers = [
            models.Teacher(name="Dr. Rajesh Kumar", email="rajesh.kumar@college.edu", max_hours_per_week=30),
            models.Teacher(name="Prof. Priya Sharma", email="priya.sharma@college.edu", max_hours_per_week=30),
            models.Teacher(name="Dr. Amit Patel", email="amit.patel@college.edu", max_hours_per_week=30),
            models.Teacher(name="Dr. Sneha Desai", email="sneha.desai@college.edu", max_hours_per_week=30),
            models.Teacher(name="Prof. Vikram Singh", email="vikram.singh@college.edu", max_hours_per_week=30),
            models.Teacher(name="Dr. Ananya Iyer", email="ananya.iyer@college.edu", max_hours_per_week=30),
            models.Teacher(name="Prof. Rohan Mehta", email="rohan.mehta@college.edu", max_hours_per_week=30),
            models.Teacher(name="Dr. Kavita Nair", email="kavita.nair@college.edu", max_hours_per_week=30),
            models.Teacher(name="Prof. Arjun Reddy", email="arjun.reddy@college.edu", max_hours_per_week=30),
            models.Teacher(name="Dr. Meera Joshi", email="meera.joshi@college.edu", max_hours_per_week=30),
        ]
        
        db.add_all(teachers)
        db.commit()
        print(f"    ✓ Added {len(teachers)} teachers")

        # 3. CLASSROOMS (15 rooms: 10 Lecture Halls + 5 Labs)
        print("  🏫 Creating classrooms...")
        rooms = []
        
        # 10 Lecture Halls
        for i in range(1, 11):
            rooms.append(models.Room(
                name=f"Room {100 + i}",
                capacity=60,
                type="LectureHall",
                resources=["Projector", "Whiteboard", "Audio System"]
            ))
        
        # 5 Computer/Science Labs
        lab_types = [
            ("Computer Lab A", "ComputerLab", ["Computers", "Projector", "Network"]),
            ("Computer Lab B", "ComputerLab", ["Computers", "Projector", "Network"]),
            ("Computer Lab C", "ComputerLab", ["Computers", "Projector", "Network"]),  # Extra Lab
            ("Physics Lab", "ScienceLab", ["Equipment", "Safety Gear", "Projector"]),
            ("Chemistry Lab", "ScienceLab", ["Equipment", "Safety Gear", "Fume Hood"]),
            ("Biology Lab", "ScienceLab", ["Microscopes", "Equipment", "Projector"]),
        ]
        
        for lab_name, lab_type, resources in lab_types:
            rooms.append(models.Room(
                name=lab_name,
                capacity=60,
                type=lab_type,
                resources=resources
            ))
        
        db.add_all(rooms)
        db.commit()
        print(f"    ✓ Added {len(rooms)} classrooms (10 Lecture Halls + 6 Labs)")

        # 4. CLASS GROUPS (3-4 groups to utilize classrooms)
        print("  👥 Creating class groups...")
        class_groups = [
            models.ClassGroup(name="SE-AI-DS-A", student_count=60),
            models.ClassGroup(name="SE-AI-DS-B", student_count=58),
            models.ClassGroup(name="TE-AI-DS-A", student_count=55),
            models.ClassGroup(name="TE-AI-DS-B", student_count=52),
        ]
        
        db.add_all(class_groups)
        db.commit()
        print(f"    ✓ Added {len(class_groups)} class groups")

        # 5. SUBJECTS - Only ML and CN labs (2 hours each)
        print("  📚 Creating subjects...")
        subjects = [
            models.Subject(
                name="Data Structures & Algorithms",
                code="CS301",
                is_lab=False,
                credits=3,
                required_room_type="LectureHall",
                duration_slots=1,
                teacher_id=1
            ),
            models.Subject(
                name="Database Management Systems",
                code="CS302",
                is_lab=False,
                credits=4,  # Increased since no DB lab
                required_room_type="LectureHall",
                duration_slots=1,
                teacher_id=2
            ),
            models.Subject(
                name="Machine Learning",
                code="CS401",
                is_lab=False,
                credits=3,
                required_room_type="LectureHall",
                duration_slots=1,
                teacher_id=3
            ),
            models.Subject(
                name="Machine Learning Lab",
                code="CS401L",
                is_lab=True,
                credits=1,  # 1 two-hour session per week (13:00-15:00)
                required_room_type="ComputerLab",
                duration_slots=2,  # 2-hour lab session
                teacher_id=3
            ),
            models.Subject(
                name="Web Development",
                code="CS303",
                is_lab=False,
                credits=3,
                required_room_type="LectureHall",
                duration_slots=1,
                teacher_id=4
            ),
            models.Subject(
                name="Computer Networks",
                code="CS304",
                is_lab=False,
                credits=3,
                required_room_type="LectureHall",
                duration_slots=1,
                teacher_id=5
            ),
            models.Subject(
                name="Computer Networks Lab",
                code="CS304L",
                is_lab=True,
                credits=1,  # 1 two-hour session per week (13:00-15:00)
                required_room_type="ComputerLab",
                duration_slots=2,  # 2-hour lab session
                teacher_id=5
            ),
        ]
        
        db.add_all(subjects)
        db.commit()
        print(f"    ✓ Added {len(subjects)} subjects")

        # 6. LESSONS (Workload Configuration)
        print("  📖 Creating initial lessons...")
        lessons = []
        # Create a lesson for each subject-teacher-class combo
        # This mirrors the initial subjects but in the new Lesson format
        for group in class_groups:
            for subject in subjects:
                # Assign subject to its designated teacher
                teacher = db.query(models.Teacher).filter(models.Teacher.id == subject.teacher_id).first()
                if teacher:
                    lessons.append(models.Lesson(
                        lessons_per_week=subject.credits,
                        length_per_lesson=subject.duration_slots,
                        teachers=[teacher],
                        class_groups=[group],
                        subjects=[subject]
                    ))
        
        db.add_all(lessons)
        db.commit()
        print(f"    ✓ Added {len(lessons)} initial lessons")

        print("\n✅ Demo data seeded successfully!")

        print("\n📊 Summary:")
        print(f"   - Teachers: {len(teachers)}")
        print(f"   - Classrooms: {len(rooms)} (10 Lecture Halls + 6 Labs)")
        print(f"   - Subjects: {len(subjects)}")
        print(f"   - Class Groups: {len(class_groups)}")
        print(f"   - Time Slots: {len(time_slots)} (Monday-Friday, 7 periods)")
        print(f"   - Teaching Hours/Day: 6 hours")
        print(f"   - Lunch Break: Period 4 (12:00 PM - 1:00 PM)")
        print("\n🚀 Ready to generate timetable!")

    except Exception as e:
        print(f"\n❌ Error seeding data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_demo_data()
