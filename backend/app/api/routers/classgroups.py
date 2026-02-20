
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import schemas
from ...infrastructure.database import get_db
from ...infrastructure import models

router = APIRouter()

@router.post("/", response_model=schemas.ClassGroup)
def create_class_group(group: schemas.ClassGroupCreate, db: Session = Depends(get_db)):
    # Check for duplicate name
    existing = db.query(models.ClassGroup).filter(models.ClassGroup.name == group.name).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Class Group with name {group.name} already exists")
    
    db_group = models.ClassGroup(
        name=group.name, 
        student_count=group.student_count
    )
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    return db_group

@router.get("/", response_model=List[schemas.ClassGroup])
def read_class_groups(
    skip: int = 0, 
    limit: int = 100,
    min_size: Optional[int] = Query(None, description="Minimum student count"),
    db: Session = Depends(get_db)
):
    query = db.query(models.ClassGroup)
    
    if min_size is not None:
        query = query.filter(models.ClassGroup.student_count >= min_size)
    
    groups = query.offset(skip).limit(limit).all()
    return groups

@router.get("/{group_id}", response_model=schemas.ClassGroup)
def get_class_group(group_id: int, db: Session = Depends(get_db)):
    group = db.query(models.ClassGroup).filter(models.ClassGroup.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail=f"Class Group with id {group_id} not found")
    return group

@router.put("/{group_id}", response_model=schemas.ClassGroup)
def update_class_group(group_id: int, group: schemas.ClassGroupCreate, db: Session = Depends(get_db)):
    db_group = db.query(models.ClassGroup).filter(models.ClassGroup.id == group_id).first()
    if not db_group:
        raise HTTPException(status_code=404, detail=f"Class Group with id {group_id} not found")
    
    # Check name uniqueness if changing
    if group.name != db_group.name:
        existing = db.query(models.ClassGroup).filter(models.ClassGroup.name == group.name).first()
        if existing:
            raise HTTPException(status_code=400, detail=f"Class Group with name {group.name} already exists")
    
    db_group.name = group.name
    db_group.student_count = group.student_count
    
    db.commit()
    db.refresh(db_group)
    return db_group

@router.delete("/{group_id}")
def delete_class_group(group_id: int, db: Session = Depends(get_db)):
    db_group = db.query(models.ClassGroup).filter(models.ClassGroup.id == group_id).first()
    if not db_group:
        raise HTTPException(status_code=404, detail=f"Class Group with id {group_id} not found")
    
    db.delete(db_group)
    db.commit()
    return {"message": f"Class Group {group_id} deleted successfully"}
