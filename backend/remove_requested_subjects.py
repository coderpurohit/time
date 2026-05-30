
from app.infrastructure.database import SessionLocal
from app.infrastructure import models
from sqlalchemy import and_

def run():
    db = SessionLocal()
    try:
        # Teachers
        # kottawar -> Dr. V. G. Kottawar (1)
        # sharma -> Dr. Manish Sharma (2)
        # gothane -> Suvarna Gothane (17)
        
        # Subjects
        # Professional and Technical Communication (18)
        # Sustainable Development I (5)
        # Engineering Physics (41)
        
        removals = [
            (1, 3), # Kottawar - Professional (Confirmed ID 3)
            (2, 5),  # Sharma - Sustainable
            (17, 41) # Gothane - Physics
        ]
        
        for t_id, s_id in removals:
            print(f"Checking removal for Teacher ID {t_id}, Subject ID {s_id}")
            
            # Find timetable entries
            entries = db.query(models.TimetableEntry).filter(
                models.TimetableEntry.teacher_id == t_id,
                models.TimetableEntry.subject_id == s_id
            ).all()
            for e in entries:
                print(f"  Deleting TimetableEntry {e.id}")
                db.delete(e)
            
            # Find lessons
            # Lesson is connected via association tables
            lessons = db.query(models.Lesson).all()
            for l in lessons:
                has_teacher = any(t.id == t_id for t in l.teachers)
                has_subject = any(s.id == s_id for s in l.subjects)
                if has_teacher and has_subject:
                    print(f"  Deleting Lesson {l.id} (found matching teacher/subject)")
                    # Delete association references first
                    db.execute(models.lesson_teachers.delete().where(models.lesson_teachers.c.lesson_id == l.id))
                    db.execute(models.lesson_class_groups.delete().where(models.lesson_class_groups.c.lesson_id == l.id))
                    db.execute(models.lesson_subjects.delete().where(models.lesson_subjects.c.lesson_id == l.id))
                    db.delete(l)
        
        db.commit()
        print("Success: Requested subjects and entries removed.")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    run()
