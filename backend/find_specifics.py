from app.infrastructure.database import SessionLocal
from app.infrastructure import models

def find_specifics():
    db = SessionLocal()
    try:
        # Teachers
        t_kottawar = db.query(models.Teacher).filter(models.Teacher.name.like("%Kottawar%")).first()
        t_sharma = db.query(models.Teacher).filter(models.Teacher.name.like("%Manish Sharma%")).first()
        t_gothane = db.query(models.Teacher).filter(models.Teacher.name.like("%Gothane%")).first()
        
        print("TARGET TEACHERS:")
        for t in [t_kottawar, t_sharma, t_gothane]:
            if t:
                print(f"ID: {t.id}, Name: {t.name}")
            else:
                print("Missing a teacher!")

        # Subjects
        s_ptc = db.query(models.Subject).filter(models.Subject.name.like("%Professional%Technical%Communication%")).all()
        s_se = db.query(models.Subject).filter(models.Subject.name.like("%Sustainable%Energy%")).all()
        s_ep = db.query(models.Subject).filter(models.Subject.name.like("%Engineering%Physics%")).all()
        
        print("\nTARGET SUBJECTS:")
        for s_list, name in [(s_ptc, "PTC"), (s_se, "SE"), (s_ep, "EP")]:
            print(f"{name}:")
            for s in s_list:
                print(f"  ID: {s.id}, Name: {s.name}, TeacherID: {s.teacher_id}, is_lab: {s.is_lab}, duration: {s.duration_slots}")

        # Lab check
        labs = db.query(models.Subject).filter(models.Subject.is_lab == True).all()
        print("\nLABS (should be 2 hours/slots):")
        for l in labs:
            print(f"  ID: {l.id}, Name: {l.name}, duration: {l.duration_slots}")

    finally:
        db.close()

if __name__ == "__main__":
    find_specifics()
