from app.infrastructure.database import SessionLocal
from app.infrastructure import models

def find_details():
    db = SessionLocal()
    try:
        teachers = {t.id: t.name for t in db.query(models.Teacher).all()}
        subjects = {s.id: s for s in db.query(models.Subject).all()}
        
        target_teacher_ids = [1, 2, 3] # Kottawar, Sharma, Gothane
        
        print("LESSONS FOR TARGET TEACHERS:")
        lessons = db.query(models.Lesson).all()
        for l in lessons:
            t_ids = [t.id for t in l.teachers]
            if any(tid in target_teacher_ids for tid in t_ids):
                s_names = [subjects[s.id].name for s in l.subjects]
                t_names = [teachers[tid] for tid in t_ids]
                print(f"Lesson ID: {l.id}, Teachers: {t_names}, Subjects: {s_names}, per_week: {l.lessons_per_week}, length: {l.length_per_lesson}")

        print("\nCHECKING SUBJECTS TABLE ASSIGNMENTS:")
        for s_id, s in subjects.items():
            if s.teacher_id in target_teacher_ids:
                print(f"Subject ID: {s.id}, Name: '{s.name}', Assigned Teacher: {teachers[s.teacher_id]} (ID: {s.teacher_id})")

        print("\nCHECKING FOR UNASSIGNED PROBLEM SUBJECTS:")
        problem_names = ["Professional and Technical Communication", "Sustainable Development I", "Sustainable Energy", "Engineering Physics"]
        for s_id, s in subjects.items():
            if any(pn.lower() in s.name.lower() for pn in problem_names):
                print(f"Subject ID: {s.id}, Name: '{s.name}', TeacherID: {s.teacher_id}")

    finally:
        db.close()

if __name__ == "__main__":
    find_details()
