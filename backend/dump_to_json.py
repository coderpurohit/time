import json
from app.infrastructure.database import SessionLocal
from app.infrastructure import models

def dump_to_json():
    db = SessionLocal()
    try:
        teachers = db.query(models.Teacher).all()
        subjects = db.query(models.Subject).all()
        lessons = db.query(models.Lesson).all()
        
        data = {
            "teachers": [{"id": t.id, "name": t.name} for t in teachers],
            "subjects": [{"id": s.id, "name": s.name, "teacher_id": s.teacher_id, "is_lab": s.is_lab, "duration": s.duration_slots} for s in subjects],
            "lessons": []
        }
        
        for l in lessons:
            l_data = {
                "id": l.id,
                "teacher_ids": [t.id for t in l.teachers],
                "subject_ids": [s.id for s in l.subjects],
                "class_group_ids": [c.id for c in l.class_groups],
                "lessons_per_week": l.lessons_per_week,
                "length_per_lesson": l.length_per_lesson
            }
            data["lessons"].append(l_data)
            
        with open("db_dump_full.json", "w") as f:
            json.dump(data, f, indent=2)
            
    finally:
        db.close()

if __name__ == "__main__":
    dump_to_json()
