from app.infrastructure.database import SessionLocal
from app.infrastructure import models
from sqlalchemy import or_

def cleanup():
    db = SessionLocal()
    try:
        # Teacher IDs
        T_KOTTAWAR = 1
        T_SHARMA = 2
        T_GOTHANE = 3
        
        # Subject IDs to remove for specific teachers
        # Professional and Technical Communication (3, 20), Seminar (29)
        PTC_IDS = [3, 20, 29]
        # Sustainable Development I (5)
        SE_IDS = [5]
        # Engineering Physics (7)
        EP_IDS = [7]
        
        removals = [
            (T_KOTTAWAR, PTC_IDS),
            (T_SHARMA, SE_IDS),
            (T_GOTHANE, EP_IDS)
        ]
        
        print("--- CLEANING UP INCORRECT ASSIGNMENTS ---")
        for t_id, s_ids in removals:
            t_name = db.query(models.Teacher).filter(models.Teacher.id == t_id).first().name
            print(f"Checking for {t_name} (ID: {t_id}) with Subjects {s_ids}")
            
            # 1. Remove from Lesson association
            lessons = db.query(models.Lesson).all()
            for l in lessons:
                has_teacher = any(t.id == t_id for t in l.teachers)
                has_subject = any(s.id in s_ids for s in l.subjects)
                if has_teacher and has_subject:
                    print(f"  Deleting Lesson {l.id} (linked to {t_name} and problem subject)")
                    # Delete association references first
                    db.execute(models.lesson_teachers.delete().where(models.lesson_teachers.c.lesson_id == l.id))
                    db.execute(models.lesson_class_groups.delete().where(models.lesson_class_groups.c.lesson_id == l.id))
                    db.execute(models.lesson_subjects.delete().where(models.lesson_subjects.c.lesson_id == l.id))
                    db.delete(l)
            
            # 2. Remove from TimetableEntry
            entries = db.query(models.TimetableEntry).filter(
                models.TimetableEntry.teacher_id == t_id,
                models.TimetableEntry.subject_id.in_(s_ids)
            ).all()
            for e in entries:
                print(f"  Deleting TimetableEntry {e.id}")
                db.delete(e)
                
            # 3. Unassign from Subject table if teacher_id matches
            subjects = db.query(models.Subject).filter(
                models.Subject.id.in_(s_ids),
                models.Subject.teacher_id == t_id
            ).all()
            for s in subjects:
                print(f"  Unassigning Subject {s.id} from {t_name}")
                s.teacher_id = None

        # 4. Set Teacher Max Hours
        print("\n--- UPDATING TEACHER MAX HOURS ---")
        t_kottawar = db.query(models.Teacher).filter(models.Teacher.id == T_KOTTAWAR).first()
        if t_kottawar: t_kottawar.max_hours_per_week = 8
        
        t_sharma = db.query(models.Teacher).filter(models.Teacher.id == T_SHARMA).first()
        if t_sharma: t_sharma.max_hours_per_week = 8
        
        t_gothane = db.query(models.Teacher).filter(models.Teacher.id == T_GOTHANE).first()
        if t_gothane: t_gothane.max_hours_per_week = 13
        
        # 5. Fix Lab Durations
        print("\n--- FIXING LAB DURATIONS ---")
        lab_subjects = db.query(models.Subject).filter(models.Subject.is_lab == True).all()
        lab_subject_ids = [s.id for s in lab_subjects]
        for s in lab_subjects:
            if s.duration_slots != 2:
                print(f"  Setting Subject {s.id} ({s.name}) duration to 2")
                s.duration_slots = 2
                
        # Update lessons for lab subjects
        all_lessons = db.query(models.Lesson).all()
        for l in all_lessons:
            if any(s.id in lab_subject_ids for s in l.subjects):
                if l.length_per_lesson != 2:
                    print(f"  Setting Lesson {l.id} length to 2 (Lab subject detected)")
                    l.length_per_lesson = 2

        db.commit()
        print("\nSUCCESS: Cleanup complete.")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    cleanup()
