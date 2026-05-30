from app.infrastructure.database import SessionLocal
from app.infrastructure import models

def find_details():
    db = SessionLocal()
    try:
        teachers = {t.id: t.name for t in db.query(models.Teacher).all()}
        subjects = {s.id: s for s in db.query(models.Subject).all()}
        
        with open("full_details_utf8.txt", "w", encoding="utf-8") as f:
            target_teacher_ids = [1, 2, 3] # Kottawar, Sharma, Gothane
            
            f.write("LESSONS FOR TARGET TEACHERS:\n")
            lessons = db.query(models.Lesson).all()
            for l in lessons:
                t_ids = [t.id for t in l.teachers]
                if any(tid in target_teacher_ids for tid in t_ids):
                    s_names = [subjects[s.id].name for s in l.subjects]
                    t_names = [teachers[tid] for tid in t_ids]
                    f.write(f"Lesson ID: {l.id}, Teachers: {t_names}, Subjects: {s_names}, per_week: {l.lessons_per_week}, length: {l.length_per_lesson}\n")

            f.write("\nCHECKING SUBJECTS TABLE ASSIGNMENTS:\n")
            for s_id, s in subjects.items():
                if s.teacher_id in target_teacher_ids:
                    f.write(f"Subject ID: {s.id}, Name: '{s.name}', Assigned Teacher: {teachers[s.teacher_id]} (ID: {s.teacher_id})\n")

            f.write("\nCHECKING FOR PROBLEM SUBJECTS:\n")
            problem_names = ["Professional", "Technical", "Communication", "Sustainable", "Energy", "Development", "Physics"]
            for s_id, s in subjects.items():
                if any(pn.lower() in s.name.lower() for pn in problem_names):
                    teacher_name = teachers.get(s.teacher_id, "None")
                    f.write(f"Subject ID: {s.id}, Name: '{s.name}', Teacher: {teacher_name} (ID: {s.teacher_id})\n")

    finally:
        db.close()

if __name__ == "__main__":
    find_details()
