from app.infrastructure.database import SessionLocal
from app.infrastructure import models

def dump_all_subjects():
    db = SessionLocal()
    try:
        subjects = db.query(models.Subject).all()
        with open("all_subjects_dump.txt", "w") as f:
            for s in subjects:
                f.write(f"ID: {s.id}, Name: '{s.name}', TeacherID: {s.teacher_id}, is_lab: {s.is_lab}, duration: {s.duration_slots}\n")
    finally:
        db.close()

if __name__ == "__main__":
    dump_all_subjects()
