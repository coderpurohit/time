from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..schemas import Lesson, LessonCreate, BulkImportRequest, BulkImportResponse
from ...infrastructure.database import get_db
from ...infrastructure import models

router = APIRouter()

@router.get("/", response_model=List[Lesson])
def get_lessons(db: Session = Depends(get_db)):
    return db.query(models.Lesson).all()

@router.post("/", response_model=Lesson)
def create_lesson(lesson: LessonCreate, db: Session = Depends(get_db)):
    db_lesson = models.Lesson(
        lessons_per_week=lesson.lessons_per_week,
        length_per_lesson=lesson.length_per_lesson
    )
    
    # Associate teachers
    teachers = db.query(models.Teacher).filter(models.Teacher.id.in_(lesson.teacher_ids)).all()
    if len(teachers) != len(lesson.teacher_ids):
        raise HTTPException(status_code=400, detail="Some teacher IDs are invalid")
    db_lesson.teachers = teachers
    
    # Associate class groups
    groups = db.query(models.ClassGroup).filter(models.ClassGroup.id.in_(lesson.class_group_ids)).all()
    if len(groups) != len(lesson.class_group_ids):
        raise HTTPException(status_code=400, detail="Some class group IDs are invalid")
    db_lesson.class_groups = groups
    
    # Associate subjects
    subjects = db.query(models.Subject).filter(models.Subject.id.in_(lesson.subject_ids)).all()
    if len(subjects) != len(lesson.subject_ids):
        raise HTTPException(status_code=400, detail="Some subject IDs are invalid")
    db_lesson.subjects = subjects
    
    db.add(db_lesson)
    db.commit()
    db.refresh(db_lesson)
    return db_lesson

@router.delete("/{lesson_id}")
def delete_lesson(lesson_id: int, db: Session = Depends(get_db)):
    db_lesson = db.query(models.Lesson).filter(models.Lesson.id == lesson_id).first()
    if not db_lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    db.delete(db_lesson)
    db.commit()
    return {"message": "Lesson deleted"}

@router.post("/bulk-import", response_model=BulkImportResponse)
def bulk_import_lessons(req: BulkImportRequest, db: Session = Depends(get_db)):
    if req.clear_existing:
        # Clear all lessons (cascade will handle associations)
        db.query(models.Lesson).delete()
        db.commit()
    
    lines = [l.strip() for l in req.text.strip().split("\n") if l.strip()]
    success = 0
    fail = 0
    errors = []
    
    for i, line in enumerate(lines, 1):
        try:
            # Format: Teacher Name(s), Class Name(s), Subject Name(s), # of periods
            parts = [p.strip() for p in line.split(",")]
            if len(parts) < 4:
                raise ValueError(f"Missing fields. Expected 4 fields (Teacher, Class, Subject, Periods), got {len(parts)}")
            
            teacher_names = [n.strip() for n in parts[0].split("|") if n.strip()]
            class_names = [n.strip() for n in parts[1].split("|") if n.strip()]
            subject_names = [n.strip() for n in parts[2].split("|") if n.strip()]
            
            try:
                count = int(parts[3])
            except ValueError:
                raise ValueError(f"Invalid period count '{parts[3]}' - must be a number")
            
            if not teacher_names:
                raise ValueError("No teacher names provided")
            if not class_names:
                raise ValueError("No class names provided")
            if not subject_names:
                raise ValueError("No subject names provided")
            
            # Resolve entities (with auto-creation)
            teachers = []
            for name in teacher_names:
                t = db.query(models.Teacher).filter(models.Teacher.name.ilike(name)).first()
                if not t:
                    # Auto-create teacher
                    safe_email = name.lower().replace(" ", ".") + "@auto-generated.com"
                    # Handle duplicate emails by adding a suffix if needed
                    suffix = 1
                    while db.query(models.Teacher).filter(models.Teacher.email == safe_email).first():
                        safe_email = f"{name.lower().replace(' ', '.')}{suffix}@auto-generated.com"
                        suffix += 1
                    
                    t = models.Teacher(name=name, email=safe_email, max_hours_per_week=18)
                    db.add(t)
                    db.flush() # Get ID
                teachers.append(t)
            
            groups = []
            for name in class_names:
                g = db.query(models.ClassGroup).filter(models.ClassGroup.name.ilike(name)).first()
                if not g:
                    # Auto-create class group
                    g = models.ClassGroup(name=name, student_count=60)
                    db.add(g)
                    db.flush()
                groups.append(g)
                
            subjects = []
            for name in subject_names:
                # Try to find by name or code
                s = db.query(models.Subject).filter(
                    (models.Subject.name.ilike(name)) | (models.Subject.code.ilike(name))
                ).first()
                if not s:
                    # Auto-create subject
                    safe_code = name[:10].upper().replace(" ", "")
                    # Ensure code uniqueness
                    suffix = 1
                    while db.query(models.Subject).filter(models.Subject.code == safe_code).first():
                        safe_code = f"{name[:7].upper().replace(' ', '')}{suffix}"
                        suffix += 1
                    
                    s = models.Subject(name=name, code=safe_code, credits=3, is_lab=False)
                    db.add(s)
                    db.flush()
                subjects.append(s)
            
            # Create the lesson with associations
            db_lesson = models.Lesson(
                lessons_per_week=count,
                length_per_lesson=1,
                teachers=teachers,
                class_groups=groups,
                subjects=subjects
            )
            db.add(db_lesson)
            db.flush()  # Flush to catch integrity errors per lesson
            success += 1
            
        except Exception as e:
            fail += 1
            errors.append(f"Line {i}: {str(e)}")
            db.rollback()  # Rollback this lesson but continue with others
            
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        errors.append(f"Final commit failed: {str(e)}")
        
    return BulkImportResponse(success_count=success, fail_count=fail, errors=errors)
