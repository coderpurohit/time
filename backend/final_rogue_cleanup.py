
from app.infrastructure.database import SessionLocal
from app.infrastructure import models

def delete_rogue_data_dynamic():
    db = SessionLocal()
    try:
        target_teachers = ['kottawar', 'sharma', 'gothane']
        target_subjects = ['professional', 'technical', 'sustainable', 'physics', 'energy']
        
        lessons = db.query(models.Lesson).all()
        to_delete = []
        
        print(f"Scanning {len(lessons)} lessons for removals...")
        for l in lessons:
            t_names = [t.name.lower() for t in l.teachers]
            s_names = [s.name.lower() for s in l.subjects]
            
            match_t = any(any(tt in tn for tt in target_teachers) for tn in t_names)
            match_s = any(any(ts in sn for ts in target_subjects) for sn in s_names)
            
            if match_t and match_s:
                to_delete.append(l)
        
        print(f"Found {len(to_delete)} lessons to remove.")
        for l in to_delete:
            lid = l.id
            print(f"  Deleting Lesson {lid}: {[s.name for s in l.subjects]} for {[t.name for t in l.teachers]}")
            
            # 1. Delete associated Timetable entries
            t_ids = [t.id for t in l.teachers]
            s_ids = [s.id for s in l.subjects]
            g_ids = [g.id for g in l.class_groups]
            
            db.query(models.TimetableEntry).filter(
                models.TimetableEntry.teacher_id.in_(t_ids),
                models.TimetableEntry.subject_id.in_(s_ids),
                models.TimetableEntry.class_group_id.in_(g_ids)
            ).delete(synchronize_session=False)
            
            # 2. Delete associations
            db.execute(models.lesson_teachers.delete().where(models.lesson_teachers.c.lesson_id == lid))
            db.execute(models.lesson_class_groups.delete().where(models.lesson_class_groups.c.lesson_id == lid))
            db.execute(models.lesson_subjects.delete().where(models.lesson_subjects.c.lesson_id == lid))
            
            # 3. Delete lesson itself
            db.delete(l)
        
        # Correct Teacher Load for Suvarna Gothane, Manish Sharma, Kottawar
        print("Correcting teacher loads (8, 8, 13)...")
        db.query(models.Teacher).filter(models.Teacher.name.ilike("%kottawar%")).update({"max_hours_per_week": 8}, synchronize_session=False)
        db.query(models.Teacher).filter(models.Teacher.name.ilike("%sharma%")).update({"max_hours_per_week": 8}, synchronize_session=False)
        db.query(models.Teacher).filter(models.Teacher.name.ilike("%gothane%")).update({"max_hours_per_week": 13}, synchronize_session=False)
        
        # Also clear Subject.teacher_id for specifically these subjects
        print("Clearing direct subject associations...")
        for ss in target_subjects:
            db.query(models.Subject).filter(models.Subject.name.ilike(f"%{ss}%")).update({"teacher_id": None}, synchronize_session=False)
        
        db.commit()
        print(f"Success! {len(to_delete)} lessons and their entries removed.")
        
    except Exception as e:
        print(f"Error during cleanup: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    delete_rogue_data_dynamic()
