
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from .. import schemas
from ...infrastructure.database import get_db
from ...infrastructure import models

router = APIRouter()

@router.post("/holidays/", response_model=schemas.Holiday)
def create_holiday(holiday: schemas.HolidayCreate, db: Session = Depends(get_db)):
    db_holiday = models.Holiday(date=holiday.date, name=holiday.name)
    db.add(db_holiday)
    db.commit()
    db.refresh(db_holiday)
    return db_holiday

@router.get("/holidays/", response_model=List[schemas.Holiday])
def read_holidays(db: Session = Depends(get_db)):
    return db.query(models.Holiday).all()

@router.post("/absent/", response_model=List[schemas.Substitution])
def mark_teacher_absent(teacher_id: int, date: str, db: Session = Depends(get_db)):
    """
    Mark a teacher absent for a specific date.
    Automatically finds all their classes from the master timetable and creates substitution requests.
    """
    # 1. Determine day of week
    try:
        dt = datetime.strptime(date, "%Y-%m-%d")
        day_of_week = dt.strftime("%A") # e.g. "Monday"
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    # 2. Find teacher's classes for that day
    classes = db.query(models.Timetable).join(models.TimeSlot).filter(
        models.Timetable.teacher_id == teacher_id,
        models.TimeSlot.day == day_of_week
    ).all()

    if not classes:
        return []

    # 3. Create substitutions
    subs = []
    for c in classes:
        # Check if sub already exists for this date/timetable combo
        existing = db.query(models.Substitution).filter(
            models.Substitution.date == date,
            models.Substitution.timetable_id == c.id
        ).first()
        
        if not existing:
            sub = models.Substitution(
                date=date,
                timetable_id=c.id,
                original_teacher_id=teacher_id,
                status="pending"
            )
            db.add(sub)
            subs.append(sub)
    
    db.commit()
    for s in subs: db.refresh(s)
    return subs

@router.get("/substitutes/available/{substitution_id}", response_model=List[schemas.Teacher])
def get_available_substitutes(substitution_id: int, db: Session = Depends(get_db)):
    """
    Find teachers who are free during the time slot of a given substitution.
    """
    sub = db.query(models.Substitution).filter(models.Substitution.id == substitution_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Substitution not found")

    # Get the time slot of the original class
    master_entry = db.query(models.Timetable).filter(models.Timetable.id == sub.timetable_id).first()
    slot_id = master_entry.time_slot_id

    # Find teachers who are NOT teaching in this slot in the master timetable
    # And are NOT already assigned as a substitute in this slot on this date
    
    # 1. Teachers busy in Master Timetable for this slot
    busy_in_master = db.query(models.Timetable.teacher_id).filter(
        models.Timetable.time_slot_id == slot_id
    ).all()
    busy_ids = [t[0] for t in busy_in_master]

    # 2. Teachers busy as substitutes on this specific date/slot
    busy_as_subs = db.query(models.Substitution.substitute_teacher_id).join(models.Timetable).filter(
        models.Substitution.date == sub.date,
        models.Timetable.time_slot_id == slot_id,
        models.Substitution.substitute_teacher_id != None
    ).all()
    busy_ids.extend([t[0] for t in busy_as_subs])

    # 3. Return all other teachers
    available = db.query(models.Teacher).filter(~models.Teacher.id.in_(busy_ids)).all()
    return available

@router.post("/substitutes/assign/{substitution_id}", response_model=schemas.Substitution)
def assign_substitute(substitution_id: int, substitute_teacher_id: int, db: Session = Depends(get_db)):
    sub = db.query(models.Substitution).filter(models.Substitution.id == substitution_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Substitution not found")
    
    sub.substitute_teacher_id = substitute_teacher_id
    sub.status = "assigned"
    db.commit()
    db.refresh(sub)
    return sub
