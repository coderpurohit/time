#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.infrastructure.database import SessionLocal
from backend.app.infrastructure import models

def add_all_data():
    """Add all teachers, classes, subjects, and rooms from the screenshot"""
    db = SessionLocal()
    try:
        print("=== ADDING FACULTY DATA FROM SCREENSHOT ===")
        
        # 1. Add Teachers
        teachers_data = [
            {"name": "Dr. V. G. Kottawar", "designation": "HOD", "email": "vg.kottawar@dypatil.edu", "max_hours": 8},
            {"name": "Dr. Manish Sharma", "designation": "Professor", "email": "manish.sharma@dypatil.edu", "max_hours": 10},
            {"name": "Dr. Suvarna S. Gothane", "designation": "Associate Professor", "email": "suvarna.gothane@dypatil.edu", "max_hours": 13},
            {"name": "Dr. Bhaghyshri A. Tingare", "designation": "Assistant Professor", "email": "bhaghyshri.tingare@dypatil.edu", "max_hours": 15},
            {"name": "Mrs. Manasi D. Karajgar", "designation": "Assistant Professor", "email": "manasi.karajgar@dypatil.edu", "max_hours": 16},
            {"name": "Mrs. Neeta J. Mahale", "designation": "Assistant Professor", "email": "neeta.mahale@dypatil.edu", "max_hours": 18},
            {"name": "Mrs. Rasika V. Wattamwar", "designation": "Assistant Professor", "email": "rasika.wattamwar@dypatil.edu", "max_hours": 18}
        ]
        
        print("Adding teachers...")
        for teacher_data in teachers_data:
            teacher = models.Teacher(
                name=teacher_data["name"],
                email=teacher_data["email"],
                max_hours_per_week=teacher_data["max_hours"]
            )
            db.add(teacher)
        
        db.commit()
        print(f"✅ Added {len(teachers_data)} teachers")
        
        # 2. Add Classes/Divisions
        classes_data = [
            {"name": "SE-B", "student_count": 60},
            {"name": "SE-A", "student_count": 60},
            {"name": "SE-C", "student_count": 60},
            {"name": "TE-A", "student_count": 60},
            {"name": "TE-B", "student_count": 60},
            {"name": "TE-C", "student_count": 60},
            {"name": "BE-A", "student_count": 60},
            {"name": "BE-B", "student_count": 60},
            {"name": "BE-C", "student_count": 60}
        ]
        
        print("Adding classes...")
        for class_data in classes_data:
            class_group = models.ClassGroup(
                name=class_data["name"],
                student_count=class_data["student_count"]
            )
            db.add(class_group)
        
        db.commit()
        print(f"✅ Added {len(classes_data)} classes")
        
        # 3. Get teacher IDs for subjects
        teachers = db.query(models.Teacher).all()
        teacher_map = {t.name: t.id for t in teachers}
        
        # 4. Add Subjects with proper lab classification
        subjects_data = [
            # Dr. V. G. Kottawar
            {"name": "Critical Thinking and Problem Solving", "code": "CTPS", "teacher": "Dr. V. G. Kottawar", "is_lab": False, "credits": 3, "duration": 1},
            {"name": "Mini Project", "code": "MP1", "teacher": "Dr. V. G. Kottawar", "is_lab": True, "credits": 4, "duration": 1},
            
            # Dr. Manish Sharma
            {"name": "Fundamentals of AI", "code": "FAI", "teacher": "Dr. Manish Sharma", "is_lab": False, "credits": 2, "duration": 1},
            {"name": "Mini Project", "code": "MP2", "teacher": "Dr. Manish Sharma", "is_lab": True, "credits": 4, "duration": 2},
            
            # Dr. Suvarna S. Gothane
            {"name": "Data Base Management System", "code": "DBMS", "teacher": "Dr. Suvarna S. Gothane", "is_lab": False, "credits": 3, "duration": 1},
            {"name": "SL1 Lab", "code": "SL1", "teacher": "Dr. Suvarna S. Gothane", "is_lab": True, "credits": 2, "duration": 4},
            {"name": "Fundamentals of AI", "code": "FAI2", "teacher": "Dr. Suvarna S. Gothane", "is_lab": False, "credits": 2, "duration": 1},
            
            # Dr. Bhaghyshri A. Tingare
            {"name": "Elective I- HCI", "code": "HCI", "teacher": "Dr. Bhaghyshri A. Tingare", "is_lab": False, "credits": 3, "duration": 1},
            {"name": "CL2 Lab", "code": "CL2", "teacher": "Dr. Bhaghyshri A. Tingare", "is_lab": True, "credits": 2, "duration": 5},
            {"name": "Project Management", "code": "PM", "teacher": "Dr. Bhaghyshri A. Tingare", "is_lab": False, "credits": 2, "duration": 1},
            
            # Mrs. Manasi D. Karajgar
            {"name": "Data Base Management System", "code": "DBMS2", "teacher": "Mrs. Manasi D. Karajgar", "is_lab": False, "credits": 3, "duration": 1},
            {"name": "SL1 Lab", "code": "SL1_2", "teacher": "Mrs. Manasi D. Karajgar", "is_lab": True, "credits": 2, "duration": 3},
            {"name": "Elective III- EAC", "code": "EAC", "teacher": "Mrs. Manasi D. Karajgar", "is_lab": False, "credits": 3, "duration": 1},
            {"name": "MOOC", "code": "MOOC", "teacher": "Mrs. Manasi D. Karajgar", "is_lab": True, "credits": 2, "duration": 2},
            
            # Mrs. Neeta J. Mahale
            {"name": "Artificial Intelligence", "code": "AI", "teacher": "Mrs. Neeta J. Mahale", "is_lab": False, "credits": 3, "duration": 1},
            {"name": "Elective IV- IR", "code": "IR", "teacher": "Mrs. Neeta J. Mahale", "is_lab": False, "credits": 3, "duration": 1},
            {"name": "CL2 Lab", "code": "CL2_2", "teacher": "Mrs. Neeta J. Mahale", "is_lab": True, "credits": 4, "duration": 3},
            
            # Mrs. Rasika V. Wattamwar
            {"name": "Web Technology", "code": "WT", "teacher": "Mrs. Rasika V. Wattamwar", "is_lab": False, "credits": 3, "duration": 1},
            {"name": "Machine Learning", "code": "ML", "teacher": "Mrs. Rasika V. Wattamwar", "is_lab": False, "credits": 3, "duration": 1},
            {"name": "CL1 Lab", "code": "CL1", "teacher": "Mrs. Rasika V. Wattamwar", "is_lab": True, "credits": 4, "duration": 3}
        ]
        
        print("Adding subjects...")
        for subject_data in subjects_data:
            teacher_id = teacher_map.get(subject_data["teacher"])
            if teacher_id:
                subject = models.Subject(
                    name=subject_data["name"],
                    code=subject_data["code"],
                    teacher_id=teacher_id,
                    is_lab=subject_data["is_lab"],
                    credits=subject_data["credits"],
                    duration_slots=subject_data["duration"],
                    required_room_type="Lab" if subject_data["is_lab"] else "LectureHall"
                )
                db.add(subject)
        
        db.commit()
        print(f"✅ Added {len(subjects_data)} subjects")
        
        # 5. Add Rooms
        rooms_data = [
            # Lecture Halls
            {"name": "LH-101", "type": "LectureHall", "capacity": 60},
            {"name": "LH-102", "type": "LectureHall", "capacity": 60},
            {"name": "LH-103", "type": "LectureHall", "capacity": 60},
            {"name": "LH-201", "type": "LectureHall", "capacity": 60},
            {"name": "LH-202", "type": "LectureHall", "capacity": 60},
            
            # Labs from the data
            {"name": "SL1 Lab", "type": "Lab", "capacity": 30},
            {"name": "SL2 Lab", "type": "Lab", "capacity": 30},
            {"name": "SL3 Lab", "type": "Lab", "capacity": 30},
            {"name": "SL4 Lab", "type": "Lab", "capacity": 30},
            {"name": "AI Lab", "type": "Lab", "capacity": 30},
            {"name": "DS Lab", "type": "Lab", "capacity": 30},
            {"name": "PLL Lab", "type": "Lab", "capacity": 30},
            {"name": "DIY Lab", "type": "Lab", "capacity": 30},
            {"name": "CL1 Lab", "type": "Lab", "capacity": 30},
            {"name": "CL2 Lab", "type": "Lab", "capacity": 30}
        ]
        
        print("Adding rooms...")
        for room_data in rooms_data:
            room = models.Room(
                name=room_data["name"],
                type=room_data["type"],
                capacity=room_data["capacity"],
                resources=[]
            )
            db.add(room)
        
        db.commit()
        print(f"✅ Added {len(rooms_data)} rooms")
        
        # 6. Add Time Slots (basic schedule)
        time_slots_data = [
            # Monday to Friday, 8 periods per day
            {"day": "Monday", "period": 1, "start_time": "08:15", "end_time": "09:15"},
            {"day": "Monday", "period": 2, "start_time": "09:15", "end_time": "10:15"},
            {"day": "Monday", "period": 3, "start_time": "10:30", "end_time": "11:30"},
            {"day": "Monday", "period": 4, "start_time": "11:30", "end_time": "12:30"},
            {"day": "Monday", "period": 5, "start_time": "12:30", "end_time": "13:30"},
            {"day": "Monday", "period": 6, "start_time": "13:30", "end_time": "14:30"},
            {"day": "Monday", "period": 7, "start_time": "14:45", "end_time": "15:45"},
            {"day": "Monday", "period": 8, "start_time": "15:45", "end_time": "16:45"},
        ]
        
        # Replicate for all weekdays
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        all_slots = []
        for day in days:
            for slot in time_slots_data:
                all_slots.append({
                    "day": day,
                    "period": slot["period"],
                    "start_time": slot["start_time"],
                    "end_time": slot["end_time"],
                    "is_break": False
                })
        
        print("Adding time slots...")
        for slot_data in all_slots:
            time_slot = models.TimeSlot(
                day=slot_data["day"],
                period=slot_data["period"],
                start_time=slot_data["start_time"],
                end_time=slot_data["end_time"],
                is_break=slot_data["is_break"]
            )
            db.add(time_slot)
        
        db.commit()
        print(f"✅ Added {len(all_slots)} time slots")
        
        # Final verification
        print("\n=== VERIFICATION ===")
        teachers_count = db.query(models.Teacher).count()
        classes_count = db.query(models.ClassGroup).count()
        subjects_count = db.query(models.Subject).count()
        rooms_count = db.query(models.Room).count()
        slots_count = db.query(models.TimeSlot).count()
        
        print(f"✅ Teachers: {teachers_count}")
        print(f"✅ Classes: {classes_count}")
        print(f"✅ Subjects: {subjects_count}")
        print(f"✅ Rooms: {rooms_count}")
        print(f"✅ Time Slots: {slots_count}")
        
        print("\n🎉 SUCCESS! All faculty data added successfully!")
        print("🌐 Now open: http://localhost:3000/timetable_page.html")
        print("📊 Enhanced Load Factor analysis is ready!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    add_all_data()