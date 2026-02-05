
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..schemas import Teacher, TeacherCreate
from ...infrastructure.database import get_db
from ...infrastructure import models

router = APIRouter()

@router.post("/", response_model=Teacher)
def create_teacher(teacher: TeacherCreate, db: Session = Depends(get_db)):
    # Check for duplicate email
    existing = db.query(models.Teacher).filter(models.Teacher.email == teacher.email).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Teacher with email {teacher.email} already exists")
    
    db_teacher = models.Teacher(
        name=teacher.name, 
        email=teacher.email,
        max_hours_per_week=teacher.max_hours_per_week,
        available_slots=teacher.available_slots
    )
    db.add(db_teacher)
    db.commit()
    db.refresh(db_teacher)
    return db_teacher

@router.get("/", response_model=List[Teacher])
def read_teachers(
    skip: int = 0, 
    limit: int = 100, 
    search: Optional[str] = Query(None, description="Search by name or email"),
    db: Session = Depends(get_db)
):
    query = db.query(models.Teacher)
    
    # Apply search filter if provided
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (models.Teacher.name.ilike(search_filter)) | 
            (models.Teacher.email.ilike(search_filter))
        )
    
    teachers = query.offset(skip).limit(limit).all()
    return teachers

@router.get("/{teacher_id}", response_model=Teacher)
def get_teacher(teacher_id: int, db: Session = Depends(get_db)):
    teacher = db.query(models.Teacher).filter(models.Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail=f"Teacher with id {teacher_id} not found")
    return teacher

@router.put("/{teacher_id}", response_model=Teacher)
def update_teacher(teacher_id: int, teacher: TeacherCreate, db: Session = Depends(get_db)):
    db_teacher = db.query(models.Teacher).filter(models.Teacher.id == teacher_id).first()
    if not db_teacher:
        raise HTTPException(status_code=404, detail=f"Teacher with id {teacher_id} not found")
    
    # Check email uniqueness if changing
    if teacher.email != db_teacher.email:
        existing = db.query(models.Teacher).filter(models.Teacher.email == teacher.email).first()
        if existing:
            raise HTTPException(status_code=400, detail=f"Teacher with email {teacher.email} already exists")
    
    db_teacher.name = teacher.name
    db_teacher.email = teacher.email
    db_teacher.max_hours_per_week = teacher.max_hours_per_week
    db_teacher.available_slots = teacher.available_slots
    
    db.commit()
    db.refresh(db_teacher)
    return db_teacher

@router.delete("/{teacher_id}")
def delete_teacher(teacher_id: int, db: Session = Depends(get_db)):
    db_teacher = db.query(models.Teacher).filter(models.Teacher.id == teacher_id).first()
    if not db_teacher:
        raise HTTPException(status_code=404, detail=f"Teacher with id {teacher_id} not found")
    
    db.delete(db_teacher)
    db.commit()
    return {"message": f"Teacher {teacher_id} deleted successfully"}
