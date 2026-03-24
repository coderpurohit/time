#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.infrastructure.database import SessionLocal
from backend.app.infrastructure import models

def emergency_fix_faculty_data():
    """Emergency fix for faculty data loading issue"""
    
    db = SessionLocal()
    try:
        print("🔧 EMERGENCY FIX: Faculty Data Loading")
        
        # Check current data
        teachers = db.query(models.Teacher).all()
        subjects = db.query(models.Subject).all()
        
        print(f"📊 Current data: {len(teachers)} teachers, {len(subjects)} subjects")
        
        if len(teachers) == 0:
            print("❌ No teachers found! Adding emergency teachers...")
            
            # Add the 7 teachers from your table
            emergency_teachers = [
                {"name": "Dr. V. G. Kottawar", "email": "vg.kottawar@dypatil.edu", "max_hours": 22},
                {"name": "Dr. Manish Sharma", "email": "manish.sharma@dypatil.edu", "max_hours": 22},
                {"name": "Dr. Suvarna S. Gothane", "email": "suvarna.gothane@dypatil.edu", "max_hours": 22},
                {"name": "Dr. Bhaghyshri A. Tingare", "email": "bhaghyshri.tingare@dypatil.edu", "max_hours": 22},
                {"name": "Mrs. Manasi D. Karajgar", "email": "manasi.karajgar@dypatil.edu", "max_hours": 22},
                {"name": "Mrs. Neeta J. Mahale", "email": "neeta.mahale@dypatil.edu", "max_hours": 22},
                {"name": "Mrs. Rasika V. Wattamwar", "email": "rasika.wattamwar@dypatil.edu", "max_hours": 22}
            ]
            
            for teacher_data in emergency_teachers:
                teacher = models.Teacher(
                    name=teacher_data["name"],
                    email=teacher_data["email"],
                    max_hours_per_week=teacher_data["max_hours"]
                )
                db.add(teacher)
            
            db.commit()
            print(f"✅ Added {len(emergency_teachers)} emergency teachers")
        
        # Refresh teacher list
        teachers = db.query(models.Teacher).all()
        
        if len(subjects) == 0:
            print("❌ No subjects found! Adding emergency subjects...")
            
            # Add subjects with teacher assignments
            emergency_subjects = [
                {"name": "Critical Thinking and Problem Solving", "code": "CTPS", "teacher": "Dr. V. G. Kottawar"},
                {"name": "Mini Project", "code": "MP1", "teacher": "Dr. V. G. Kottawar"},
                {"name": "Fundamentals of AI", "code": "FAI", "teacher": "Dr. Manish Sharma"},
                {"name": "Mini Project 2", "code": "MP2", "teacher": "Dr. Manish Sharma"},
                {"name": "Data Base Management System", "code": "DBMS", "teacher": "Dr. Suvarna S. Gothane"},
                {"name": "Fundamentals of AI 2", "code": "FAI2", "teacher": "Dr. Suvarna S. Gothane"},
                {"name": "Elective I- HCI", "code": "HCI", "teacher": "Dr. Bhaghyshri A. Tingare"},
                {"name": "Project Management", "code": "PM", "teacher": "Dr. Bhaghyshri A. Tingare"},
                {"name": "Data Base Management System 2", "code": "DBMS2", "teacher": "Mrs. Manasi D. Karajgar"},
                {"name": "Elective III- EAC", "code": "EAC", "teacher": "Mrs. Manasi D. Karajgar"},
                {"name": "Artificial Intelligence", "code": "AI", "teacher": "Mrs. Neeta J. Mahale"},
                {"name": "Elective IV- IR", "code": "IR", "teacher": "Mrs. Neeta J. Mahale"},
                {"name": "Web Technology", "code": "WT", "teacher": "Mrs. Rasika V. Wattamwar"},
                {"name": "Machine Learning", "code": "ML", "teacher": "Mrs. Rasika V. Wattamwar"}
            ]
            
            for subject_data in emergency_subjects:
                # Find teacher
                teacher = next((t for t in teachers if t.name == subject_data["teacher"]), None)
                if teacher:
                    subject = models.Subject(
                        name=subject_data["name"],
                        code=subject_data["code"],
                        teacher_id=teacher.id,
                        is_lab=False,
                        credits=3,
                        required_room_type="LectureHall",
                        duration_slots=1
                    )
                    db.add(subject)
            
            db.commit()
            print(f"✅ Added {len(emergency_subjects)} emergency subjects")
        
        # Generate timetable if missing
        latest_version = db.query(models.TimetableVersion).order_by(
            models.TimetableVersion.id.desc()
        ).first()
        
        if not latest_version or not latest_version.entries:
            print("🔧 Generating emergency timetable...")
            
            from backend.app.services.timetable_service import TimetableService
            service = TimetableService()
            result = service.generate_simple_timetable(db)
            
            if result and result.get('success'):
                print(f"✅ Generated timetable with {result.get('total_entries', 0)} entries")
            else:
                print("⚠️ Timetable generation had issues")
        
        # Final verification
        teachers = db.query(models.Teacher).all()
        subjects = db.query(models.Subject).all()
        latest_version = db.query(models.TimetableVersion).order_by(
            models.TimetableVersion.id.desc()
        ).first()
        
        print(f"✅ FINAL STATUS:")
        print(f"   - Teachers: {len(teachers)}")
        print(f"   - Subjects: {len(subjects)}")
        print(f"   - Timetable entries: {len(latest_version.entries) if latest_version else 0}")
        
        return True
        
    except Exception as e:
        print(f"❌ Emergency fix error: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("🚨 EMERGENCY FIX: Faculty Data Loading Issue")
    
    if emergency_fix_faculty_data():
        print("\n🎉 EMERGENCY FIX COMPLETE!")
        print("✅ Faculty data should now load properly")
        print("🔄 Refresh the Dynamic Academic Management page")
        print("🌐 http://localhost:8000/dynamic_academic_management.html")
    else:
        print("\n❌ Emergency fix failed")