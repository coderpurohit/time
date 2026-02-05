
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ...infrastructure.database import get_db
from ...infrastructure import models
from ...services.timetable_service import TimetableService
from .. import schemas

router = APIRouter()

@router.get("/latest", response_model=schemas.TimetableVersion)
def get_latest_timetable(db: Session = Depends(get_db)):
    latest = TimetableService.get_latest(db)
    if not latest:
        raise HTTPException(status_code=404, detail="No timetables found")
    return latest

@router.get("/{id}", response_model=schemas.TimetableVersion)
def get_timetable_by_id(id: int, db: Session = Depends(get_db)):
    version = db.query(models.TimetableVersion).filter(models.TimetableVersion.id == id).first()
    if not version:
        raise HTTPException(status_code=404, detail="Timetable version not found")
    return version

@router.get("/analytics/{version_id}", response_model=schemas.AnalyticsReport)
def get_timetable_analytics(version_id: int, db: Session = Depends(get_db)):
    report = TimetableService.get_analytics(db, version_id)
    if not report:
        raise HTTPException(status_code=404, detail="Analytics not available")
    return report

@router.delete("/{id}")
def delete_timetable(id: int, db: Session = Depends(get_db)):
    db.query(models.TimetableVersion).filter(models.TimetableVersion.id == id).delete()
    db.commit()
    return {"message": "Timetable deleted successfully"}

@router.get("/{id}/export")
def export_timetable(id: int, db: Session = Depends(get_db)):
    version = db.query(models.TimetableVersion).filter(models.TimetableVersion.id == id).first()
    if not version:
        raise HTTPException(status_code=404, detail="Timetable not found")
    # Return raw JSON dump
    return version
