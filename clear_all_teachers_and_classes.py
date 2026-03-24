#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.infrastructure.database import SessionLocal
from backend.app.infrastructure import models

def clear_all_data():
    """Remove all teachers, classes, subjects, lessons, rooms, and timetables"""
    db = SessionLocal()
    try:
        print("=== CLEARING ALL DATA ===")
        
        # Get counts before deletion
        teachers_count = db.query(models.Teacher).count()
        classes_count = db.query(models.ClassGroup).count()
        subjects_count = db.query(models.Subject).count()
        lessons_count = db.query(models.Lesson).count()
        rooms_count = db.query(models.Room).count()
        timetables_count = db.query(models.TimetableVersion).count()
        
        print(f"Before deletion:")
        print(f"  Teachers: {teachers_count}")
        print(f"  Classes: {classes_count}")
        print(f"  Subjects: {subjects_count}")
        print(f"  Lessons: {lessons_count}")
        print(f"  Rooms: {rooms_count}")
        print(f"  Timetables: {timetables_count}")
        
        # Delete in correct order (foreign key dependencies)
        print("\n=== DELETING DATA ===")
        
        # 1. Delete timetable entries first
        entries_deleted = db.query(models.TimetableEntry).delete()
        print(f"✅ Deleted {entries_deleted} timetable entries")
        
        # 2. Delete timetable versions
        versions_deleted = db.query(models.TimetableVersion).delete()
        print(f"✅ Deleted {versions_deleted} timetable versions")
        
        # 3. Delete lessons (many-to-many relationships)
        lessons_deleted = db.query(models.Lesson).delete()
        print(f"✅ Deleted {lessons_deleted} lessons")
        
        # 4. Delete subjects (has foreign key to teachers)
        subjects_deleted = db.query(models.Subject).delete()
        print(f"✅ Deleted {subjects_deleted} subjects")
        
        # 5. Delete teachers
        teachers_deleted = db.query(models.Teacher).delete()
        print(f"✅ Deleted {teachers_deleted} teachers")
        
        # 6. Delete class groups
        classes_deleted = db.query(models.ClassGroup).delete()
        print(f"✅ Deleted {classes_deleted} class groups")
        
        # 7. Delete rooms
        rooms_deleted = db.query(models.Room).delete()
        print(f"✅ Deleted {rooms_deleted} rooms")
        
        # 8. Delete substitutions
        subs_deleted = db.query(models.Substitution).delete()
        print(f"✅ Deleted {subs_deleted} substitutions")
        
        # Commit all changes
        db.commit()
        
        print("\n=== VERIFICATION ===")
        # Verify deletion
        teachers_remaining = db.query(models.Teacher).count()
        classes_remaining = db.query(models.ClassGroup).count()
        subjects_remaining = db.query(models.Subject).count()
        lessons_remaining = db.query(models.Lesson).count()
        rooms_remaining = db.query(models.Room).count()
        timetables_remaining = db.query(models.TimetableVersion).count()
        
        print(f"After deletion:")
        print(f"  Teachers: {teachers_remaining}")
        print(f"  Classes: {classes_remaining}")
        print(f"  Subjects: {subjects_remaining}")
        print(f"  Lessons: {lessons_remaining}")
        print(f"  Rooms: {rooms_remaining}")
        print(f"  Timetables: {timetables_remaining}")
        
        if (teachers_remaining == 0 and classes_remaining == 0 and 
            subjects_remaining == 0 and lessons_remaining == 0 and 
            rooms_remaining == 0 and timetables_remaining == 0):
            print("\n🎉 SUCCESS! All data cleared successfully!")
            print("\nYou can now add new teachers, classes, subjects, and rooms through the web interface.")
            print("The enhanced Load Factor analysis will work with your new data.")
        else:
            print("\n⚠️ Some data may still remain. Check the counts above.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()

def main():
    print("🚨 WARNING: This will delete ALL teachers, classes, subjects, lessons, rooms, and timetables!")
    print("This action cannot be undone.")
    
    confirm = input("\nType 'YES' to confirm deletion: ")
    
    if confirm == 'YES':
        clear_all_data()
    else:
        print("❌ Operation cancelled.")

if __name__ == "__main__":
    main()