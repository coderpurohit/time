
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ...infrastructure.database import get_db
from ...services.timetable_service import TimetableService
from .. import schemas

router = APIRouter()

@router.get("/utilization/{version_id}", response_model=schemas.AnalyticsReport)
def get_utilization_report(version_id: int, db: Session = Depends(get_db)):
    report = TimetableService.get_analytics(db, version_id)
    if not report:
        raise HTTPException(status_code=404, detail="Timetable not found")
    return report

@router.get("/validate/{version_id}")
def validate_timetable(version_id: int, db: Session = Depends(get_db)):
    report = TimetableService.get_analytics(db, version_id)
    if not report:
        raise HTTPException(status_code=404, detail="Timetable not found")
    
    is_valid = len(report["conflicts"]) == 0
    return {"is_valid": is_valid, "conflicts": report["conflicts"]}
