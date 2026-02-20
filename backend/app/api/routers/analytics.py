from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from ...infrastructure.database import get_db
from ...infrastructure import models

router = APIRouter()

@router.get("/load-factor")
def get_load_factor_analysis(db: Session = Depends(get_db)):
    """
    Get comprehensive load factor analysis for teachers and classes
    """
    # Get latest timetable
    latest_version = db.query(models.TimetableVersion).order_by(
        models.TimetableVersion.id.desc()
    ).first()
    
    if not latest_version:
        raise HTTPException(status_code=404, detail="No timetable found. Please generate a timetable first.")
    
    entries = latest_version.entries
    
    if not entries:
        raise HTTPException(status_code=404, detail="Timetable has no entries")
    
    # Get all data
    teachers = db.query(models.Teacher).all()
    classes = db.query(models.ClassGroup).all()
    subjects = db.query(models.Subject).all()
    slots = db.query(models.TimeSlot).all()
    
    # Calculate teacher load
    teacher_load = []
    max_periods_per_week = 25
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    
    for teacher in teachers:
        teacher_entries = [e for e in entries if e.teacher_id == teacher.id]
        total_periods = len(teacher_entries)
        load_percentage = round((total_periods / max_periods_per_week) * 100)
        
        # Daily distribution
        daily_load = {}
        for day in days:
            day_entries = [e for e in teacher_entries if e.time_slot and e.time_slot.day == day]
            daily_load[day] = len(day_entries)
        
        # Subject distribution
        subject_distribution = {}
        for entry in teacher_entries:
            subject_id = entry.subject_id
            if subject_id not in subject_distribution:
                subject_distribution[subject_id] = 0
            subject_distribution[subject_id] += 1
        
        teacher_load.append({
            "id": teacher.id,
            "name": teacher.name,
            "email": teacher.email,
            "total_periods": total_periods,
            "max_hours": teacher.max_hours_per_week or 20,
            "load_percentage": load_percentage,
            "daily_load": daily_load,
            "subject_distribution": subject_distribution,
            "avg_per_day": round(total_periods / 5, 1)
        })
    
    # Calculate class load
    class_load = []
    for class_group in classes:
        class_entries = [e for e in entries if e.class_group_id == class_group.id]
        total_periods = len(class_entries)
        load_percentage = round((total_periods / max_periods_per_week) * 100)
        
        # Daily distribution
        daily_load = {}
        for day in days:
            day_entries = [e for e in class_entries if e.time_slot and e.time_slot.day == day]
            daily_load[day] = len(day_entries)
        
        # Subject distribution
        subject_distribution = {}
        for entry in class_entries:
            subject_id = entry.subject_id
            if subject_id not in subject_distribution:
                subject_distribution[subject_id] = 0
            subject_distribution[subject_id] += 1
        
        class_load.append({
            "id": class_group.id,
            "name": class_group.name,
            "student_count": class_group.student_count,
            "total_periods": total_periods,
            "load_percentage": load_percentage,
            "daily_load": daily_load,
            "subject_distribution": subject_distribution
        })
    
    # Calculate summary stats
    avg_teacher_load = round(sum(t["total_periods"] for t in teacher_load) / len(teacher_load)) if teacher_load else 0
    
    return {
        "summary": {
            "total_teachers": len(teachers),
            "total_classes": len(classes),
            "total_periods": len(entries),
            "avg_teacher_load": avg_teacher_load,
            "timetable_id": latest_version.id,
            "timetable_name": latest_version.name
        },
        "teacher_load": teacher_load,
        "class_load": class_load,
        "subjects": [{"id": s.id, "name": s.name, "code": s.code} for s in subjects]
    }
