from app.infrastructure.database import SessionLocal
from app.infrastructure import models

def dump_info():
    db = SessionLocal()
    try:
        teachers = db.query(models.Teacher).all()
        subjects = db.query(models.Subject).all()
        
        print("TEACHERS:")
        for t in teachers:
            print(f"ID: {t.id}, Name: {t.name}")
            
        print("\nSUBJECTS:")
        for s in subjects:
            print(f"ID: {s.id}, Name: {s.name}, is_lab: {s.is_lab}, duration: {s.duration_slots}")
            
    finally:
        db.close()

if __name__ == "__main__":
    dump_info()
