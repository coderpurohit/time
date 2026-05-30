from app.infrastructure.database import SessionLocal
from app.infrastructure import models

def dump_workload_and_config():
    db = SessionLocal()
    try:
        teachers = {t.id: t.name for t in db.query(models.Teacher).all()}
        aspects = db.query(models.TeacherWorkloadAspect).all()
        config = db.query(models.ScheduleConfig).first()
        
        with open("workload_and_config_dump.txt", "w", encoding="utf-8") as f:
            f.write("--- SCHEDULE CONFIG ---\n")
            if config:
                f.write(f"ID: {config.id}, Number of Periods: {config.number_of_periods}, Duration: {config.period_duration_minutes}\n")
                f.write(f"Days: {config.schedule_days}\n")
                f.write(f"Breaks: {config.breaks}\n")
            else:
                f.write("No config found!\n")
                
            f.write("\n--- TEACHER WORKLOAD ASPECTS ---\n")
            for a in aspects:
                t_name = teachers.get(a.teacher_id, "Unknown")
                f.write(f"ID: {a.id}, Teacher: {t_name} (ID: {a.teacher_id}), Course: '{a.course_name}', Theory: {a.theory_hours}, Practical: {a.practical_hours}, Total: {a.total_load}\n")
                
            f.write("\n--- SUBJECTS WITH TEACHER_ID ---\n")
            subjects = db.query(models.Subject).all()
            for s in subjects:
                t_name = teachers.get(s.teacher_id, "None")
                f.write(f"ID: {s.id}, Name: '{s.name}', Teacher: {t_name} (ID: {s.teacher_id}), IsLab: {s.is_lab}, Duration: {s.duration_slots}\n")

    finally:
        db.close()

if __name__ == "__main__":
    dump_workload_and_config()
