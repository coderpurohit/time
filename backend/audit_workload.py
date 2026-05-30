
from app.infrastructure.database import SessionLocal
from app.infrastructure import models
from collections import defaultdict

def audit():
    db = SessionLocal()
    try:
        lessons = db.query(models.Lesson).all()
        teacher_load = defaultdict(int)
        for l in lessons:
            for t in l.teachers:
                teacher_load[t.name] += l.lessons_per_week * l.length_per_lesson
        
        print("--- TEACHER TOTAL REQUIRED LOAD ---")
        sorted_load = sorted(teacher_load.items(), key=lambda x: x[1], reverse=True)
        for name, load in sorted_load:
            t = db.query(models.Teacher).filter(models.Teacher.name == name).first()
            limit = t.max_hours_per_week if t else "N/A"
            print(f"{name}: {load} (Limit: {limit})")

        print("\n--- GROUP TOTAL REQUIRED LOAD ---")
        group_load = defaultdict(int)
        for l in lessons:
            for g in l.class_groups:
                group_load[g.name] += l.lessons_per_week * l.length_per_lesson
        for name, load in group_load.items():
            print(f"{name}: {load}")

        print("\n--- ROOM AVAILABILITY ---")
        rooms = db.query(models.Room).all()
        print(f"Total Rooms: {len(rooms)} ({sum(1 for r in rooms if r.type=='Lab')} Labs, {sum(1 for r in rooms if r.type!='Lab')} Lecture Halls)")

        print("\n--- PERIOD TYPE BREAKDOWN ---")
        total_theory = 0
        total_lab = 0
        for l in lessons:
            if l.length_per_lesson >= 2:
                total_lab += l.lessons_per_week * l.length_per_lesson
            else:
                total_theory += l.lessons_per_week * l.length_per_lesson
        print(f"Total Theory Periods Required: {total_theory}")
        print(f"Total Lab Periods Required: {total_lab}")
        print(f"Total Combined Required: {total_theory + total_lab}")

    finally:
        db.close()

if __name__ == "__main__":
    audit()
