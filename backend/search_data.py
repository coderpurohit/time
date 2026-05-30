from app.infrastructure.database import SessionLocal
from app.infrastructure import models

def search_subjects():
    db = SessionLocal()
    try:
        subjects = db.query(models.Subject).all()
        print("--- ALL SUBJECTS ---")
        for s in subjects:
            print(f"ID: {s.id}, Name: '{s.name}', TeacherID: {s.teacher_id}, Lab: {s.is_lab}, Duration: {s.duration_slots}")
            
        teachers = db.query(models.Teacher).all()
        print("\n--- ALL TEACHERS ---")
        for t in teachers:
            print(f"ID: {t.id}, Name: '{t.name}'")
            
    finally:
        db.close()

if __name__ == "__main__":
    search_subjects()
