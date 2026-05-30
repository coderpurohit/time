
from app.infrastructure.database import SessionLocal
from app.infrastructure import models

db = SessionLocal()

print("--- SUBJECTS ---")
subjects = db.query(models.Subject).all()
for s in subjects:
    print(f"ID: {s.id}, Name: {s.name}, Code: {s.code}, IsLab: {s.is_lab}, Duration: {s.duration_slots}")

print("\n--- LESSONS ---")
lessons = db.query(models.Lesson).all()
for l in lessons:
    s_names = [s.name for s in l.subjects]
    g_names = [g.name for g in l.class_groups]
    t_names = [t.name for t in l.teachers]
    print(f"ID: {l.id}, Subj: {s_names}, Group: {g_names}, Teacher: {t_names}, PerWeek: {l.lessons_per_week}, Length: {l.length_per_lesson}")

db.close()
