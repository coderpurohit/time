
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..schemas import Subject, SubjectCreate
from ...infrastructure.database import get_db
from ...infrastructure import models

router = APIRouter()

@router.post("/", response_model=Subject)
def create_subject(subject: SubjectCreate, db: Session = Depends(get_db)):
    # Check for duplicate subject code
    existing = db.query(models.Subject).filter(models.Subject.code == subject.code).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Subject with code {subject.code} already exists")
    
    db_subject = models.Subject(
        name=subject.name, 
        code=subject.code,
        is_lab=subject.is_lab,
        credits=subject.credits,
        required_room_type=subject.required_room_type,
        duration_slots=subject.duration_slots,
        teacher_id=subject.teacher_id
    )
    db.add(db_subject)
    db.commit()
    db.refresh(db_subject)
    return db_subject

@router.get("/", response_model=List[Subject])
def read_subjects(
    skip: int = 0, 
    limit: int = 100,
    search: Optional[str] = Query(None, description="Search by name or code"),
    is_lab: Optional[bool] = None,
    teacher_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Subject)
    
    # Apply filters
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (models.Subject.name.ilike(search_filter)) | 
            (models.Subject.code.ilike(search_filter))
        )
    
    if is_lab is not None:
        query = query.filter(models.Subject.is_lab == is_lab)
    
    if teacher_id is not None:
        query = query.filter(models.Subject.teacher_id == teacher_id)
    
    subjects = query.offset(skip).limit(limit).all()
    return subjects

@router.get("/{subject_id}", response_model=Subject)
def get_subject(subject_id: int, db: Session = Depends(get_db)):
    subject = db.query(models.Subject).filter(models.Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail=f"Subject with id {subject_id} not found")
    return subject

@router.put("/{subject_id}", response_model=Subject)
def update_subject(subject_id: int, subject: SubjectCreate, db: Session = Depends(get_db)):
    db_subject = db.query(models.Subject).filter(models.Subject.id == subject_id).first()
    if not db_subject:
        raise HTTPException(status_code=404, detail=f"Subject with id {subject_id} not found")
    
    # Check code uniqueness if changing
    if subject.code != db_subject.code:
        existing = db.query(models.Subject).filter(models.Subject.code == subject.code).first()
        if existing:
            raise HTTPException(status_code=400, detail=f"Subject with code {subject.code} already exists")
    
    db_subject.name = subject.name
    db_subject.code = subject.code
    db_subject.is_lab = subject.is_lab
    db_subject.credits = subject.credits
    db_subject.required_room_type = subject.required_room_type
    db_subject.duration_slots = subject.duration_slots
    db_subject.teacher_id = subject.teacher_id
    
    db.commit()
    db.refresh(db_subject)
    return db_subject

@router.delete("/{subject_id}")
def delete_subject(subject_id: int, db: Session = Depends(get_db)):
    db_subject = db.query(models.Subject).filter(models.Subject.id == subject_id).first()
    if not db_subject:
        raise HTTPException(status_code=404, detail=f"Subject with id {subject_id} not found")
    
    db.delete(db_subject)
    db.commit()
    return {"message": f"Subject {subject_id} deleted successfully"}
