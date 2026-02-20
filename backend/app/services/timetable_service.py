
from sqlalchemy.orm import Session
from ..infrastructure.database import SessionLocal
from ..infrastructure import models
from ..solver.csp_solver import CspTimetableSolver
from ..solver.genetic_solver import GeneticTimetableSolver
from ..solver.constraints.base import HardConstraints
from ..domain.entities.all_entities import Teacher, Subject, Room, ClassGroup, TimeSlot
from fastapi import HTTPException

class TimetableService:
    @staticmethod
    def generate_and_save(db: Session, method: str = "csp", version_name: str = "New Timetable"):
        # 1. Fetch data
        db_teachers = db.query(models.Teacher).all()
        db_subjects = db.query(models.Subject).all()
        db_rooms = db.query(models.Room).all()
        db_groups = db.query(models.ClassGroup).all()
        db_slots = db.query(models.TimeSlot).all()
        db_lessons = db.query(models.Lesson).all()

        # 2. Domain conversion (Simplified)
        teachers = [Teacher(id=t.id, name=t.name, email=t.email, max_hours_per_week=t.max_hours_per_week) for t in db_teachers]
        subjects = [Subject(id=s.id, name=s.name, code=s.code, is_lab=s.is_lab, credits=s.credits, 
                    required_room_type=s.required_room_type, duration_slots=s.duration_slots, teacher_id=s.teacher_id) for s in db_subjects]
        rooms = [Room(id=r.id, name=r.name, capacity=r.capacity, type=r.type) for r in db_rooms]
        groups = [ClassGroup(id=g.id, name=g.name, student_count=g.student_count) for g in db_groups]
        slots = [TimeSlot(id=s.id, day=s.day, period=s.period, start_time=s.start_time, end_time=s.end_time, is_break=s.is_break) for s in db_slots]
        
        # Convert lessons to required assignments
        # Each lesson defines: which groups need which subjects, how many times per week
        required_assignments = []
        assignment_id = 0  # Unique ID for each assignment occurrence
        
        print(f"DEBUG: Found {len(db_lessons)} lessons in database")
        
        for lesson in db_lessons:
            # Handle many-to-many relationships - create assignments for ALL combinations
            teachers_list = lesson.teachers if lesson.teachers else []
            subjects_list = lesson.subjects if lesson.subjects else []
            groups_list = lesson.class_groups if lesson.class_groups else []
            
            print(f"DEBUG: Lesson {lesson.id}: {len(teachers_list)} teachers, {len(subjects_list)} subjects, {len(groups_list)} groups, {lesson.lessons_per_week} periods/week")
            
            # Create assignments for each combination
            for teacher in teachers_list:
                for subject in subjects_list:
                    for group in groups_list:
                        # Add this many assignments for this lesson
                        for occurrence in range(lesson.lessons_per_week):
                            required_assignments.append({
                                'assignment_id': assignment_id,
                                'group_id': group.id,
                                'subject_id': subject.id,
                                'teacher_id': teacher.id,
                                'duration': lesson.length_per_lesson,
                                'occurrence': occurrence + 1
                            })
                            assignment_id += 1

        print(f"DEBUG: Generated {len(required_assignments)} required assignments from {len(db_lessons)} lessons")

        # 3. Solver
        if method == "genetic":
            solver = GeneticTimetableSolver(teachers, subjects, rooms, groups, slots, required_assignments)
            schedule = solver.solve()
        else:
            solver = CspTimetableSolver(teachers, subjects, rooms, groups, slots, required_assignments)
            schedule = solver.solve()

        if not schedule:
            raise HTTPException(status_code=409, detail="No feasible solution found.")

        # 4. Save with versioning
        version = models.TimetableVersion(name=version_name, algorithm=method)
        db.add(version)
        db.commit()
        db.refresh(version)

        for item in schedule:
            entry = models.TimetableEntry(
                version_id=version.id,
                time_slot_id=item["time_slot_id"],
                subject_id=item["subject_id"],
                room_id=item["room_id"],
                class_group_id=item["class_group_id"],
                teacher_id=item["teacher_id"]
            )
            db.add(entry)
        
        # Mark version as active after successful generation
        version.status = "active"
        version.is_valid = True
        db.commit()
        db.refresh(version)
        return version

    @staticmethod
    def get_latest(db: Session):
        return db.query(models.TimetableVersion).order_by(models.TimetableVersion.id.desc()).first()

    @staticmethod
    def get_analytics(db: Session, version_id: int):
        version = db.query(models.TimetableVersion).filter(models.TimetableVersion.id == version_id).first()
        if not version: return None
        
        entries = version.entries
        total_slots = db.query(models.TimeSlot).filter(models.TimeSlot.is_break == False).count()
        
        # 1. Teacher Utilization
        teacher_stats = []
        teachers = db.query(models.Teacher).all()
        for t in teachers:
            assigned = sum(1 for e in entries if e.teacher_id == t.id)
            teacher_stats.append({
                "id": t.id,
                "name": t.name,
                "assigned_slots": assigned,
                "total_slots": t.max_hours_per_week, # Or use a different metric
                "utilization_percentage": (assigned / t.max_hours_per_week * 100) if t.max_hours_per_week else 0
            })
            
        # 2. Room Utilization
        room_stats = []
        rooms = db.query(models.Room).all()
        for r in rooms:
            assigned = sum(1 for e in entries if e.room_id == r.id)
            room_stats.append({
                "id": r.id,
                "name": r.name,
                "assigned_slots": assigned,
                "total_slots": total_slots,
                "utilization_percentage": (assigned / total_slots * 100) if total_slots else 0
            })
            
        # 3. Conflict Detection (Redundant for auto-generated, but good for manual edits)
        conflicts = HardConstraints.check_teacher_overlap([e.__dict__ for e in entries])
        conflicts += HardConstraints.check_room_overlap([e.__dict__ for e in entries])

        return {
            "teacher_utilization": teacher_stats,
            "room_utilization": room_stats,
            "conflicts": conflicts,
            "subject_load": {s.id: 1.0 for s in db.query(models.Subject).all()} # Placeholder
        }

    @staticmethod
    def generate_in_background(version_id: int, method: str):
        db = SessionLocal()
        try:
            version = db.query(models.TimetableVersion).filter(models.TimetableVersion.id == version_id).first()
            if not version: return
            
            # Fetch data (reusing logic from generate_and_save)
            db_teachers = db.query(models.Teacher).all()
            db_subjects = db.query(models.Subject).all()
            db_rooms = db.query(models.Room).all()
            db_groups = db.query(models.ClassGroup).all()
            db_slots = db.query(models.TimeSlot).all()
            db_lessons = db.query(models.Lesson).all()  # ADDED: Query lessons

            teachers = [Teacher(id=t.id, name=t.name, email=t.email) for t in db_teachers]
            subjects = [Subject(id=s.id, name=s.name, code=s.code, is_lab=s.is_lab, credits=s.credits, 
                        required_room_type=s.required_room_type, duration_slots=s.duration_slots, teacher_id=s.teacher_id) for s in db_subjects]
            rooms = [Room(id=r.id, name=r.name, capacity=r.capacity, type=r.type) for r in db_rooms]
            groups = [ClassGroup(id=g.id, name=g.name, student_count=g.student_count) for g in db_groups]
            slots = [TimeSlot(id=s.id, day=s.day, period=s.period, start_time=s.start_time, end_time=s.end_time, is_break=s.is_break) for s in db_slots]

            # ADDED: Convert lessons to required assignments (same logic as generate_and_save)
            required_assignments = []
            assignment_id = 0
            
            print(f"DEBUG (background): Found {len(db_lessons)} lessons in database")
            
            for lesson in db_lessons:
                teacher_id = lesson.teachers[0].id if lesson.teachers else None
                subject_id = lesson.subjects[0].id if lesson.subjects else None
                group_id = lesson.class_groups[0].id if lesson.class_groups else None
                
                print(f"DEBUG (background): Lesson {lesson.id}: teacher={teacher_id}, subject={subject_id}, group={group_id}, periods={lesson.lessons_per_week}")
                
                if teacher_id and subject_id and group_id:
                    for occurrence in range(lesson.lessons_per_week):
                        required_assignments.append({
                            'assignment_id': assignment_id,
                            'group_id': group_id,
                            'subject_id': subject_id,
                            'teacher_id': teacher_id,
                            'duration': lesson.length_per_lesson,
                            'occurrence': occurrence + 1
                        })
                        assignment_id += 1

            print(f"DEBUG (background): Generated {len(required_assignments)} required assignments from {len(db_lessons)} lessons")

            # Pass required_assignments to solver
            if method == "genetic":
                solver = GeneticTimetableSolver(teachers, subjects, rooms, groups, slots, required_assignments)
                schedule = solver.solve()
            else:
                solver = CspTimetableSolver(teachers, subjects, rooms, groups, slots, required_assignments)
                schedule = solver.solve()

            if schedule:
                for item in schedule:
                    entry = models.TimetableEntry(
                        version_id=version.id,
                        time_slot_id=item["time_slot_id"],
                        subject_id=item["subject_id"],
                        room_id=item["room_id"],
                        class_group_id=item["class_group_id"],
                        teacher_id=item["teacher_id"]
                    )
                    db.add(entry)
                version.status = "active"
                version.is_valid = True
            else:
                version.status = "failed"
                version.is_valid = False
            
            db.commit()
        except Exception as e:
            print(f"Bkg Error: {e}")
            import traceback
            traceback.print_exc()
            if version:
                version.status = "error"
                db.commit()
        finally:
            db.close()
