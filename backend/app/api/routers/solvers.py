from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List

from ...infrastructure.database import get_db
from ...infrastructure import models
from ...services.timetable_service import TimetableService
from .. import schemas

router = APIRouter()

@router.post("/generate", response_model=schemas.TimetableVersion)
def generate_timetable(background_tasks: BackgroundTasks, method: str = "csp", name: str = "New Generation", db: Session = Depends(get_db)):
    """
    Generate and save a new timetable version using LOAD-AWARE generator.
    This uses an enhanced algorithm that considers teacher load factors.
    """
    
    # Validate sufficient data exists
    teachers_count = db.query(models.Teacher).count()
    subjects_count = db.query(models.Subject).count()
    rooms_count = db.query(models.Room).count()
    groups_count = db.query(models.ClassGroup).count()
    lessons_count = db.query(models.Lesson).count()

    if teachers_count == 0 or subjects_count == 0 or rooms_count == 0 or groups_count == 0:
        raise HTTPException(
            status_code=400, 
            detail=f"Insufficient data. Teachers: {teachers_count}, Subjects: {subjects_count}, Rooms: {rooms_count}, Groups: {groups_count}"
        )
    
    override_exists = db.query(models.WorkloadReportOverride).filter(
        models.WorkloadReportOverride.version_id == None
    ).first() is not None

    if lessons_count == 0 and not override_exists:
        raise HTTPException(
            status_code=400,
            detail="No lessons found and no DOCX workload override exists. Please create lessons or upload the load distribution first."
        )

    print(f"LOAD-AWARE GENERATOR API: Starting generation with {lessons_count} lessons")

    # Use the enhanced timetable service
    version = TimetableService.generate_and_save(db, method, name)
    
    print(f"LOAD-AWARE GENERATOR API: Created version {version.id} with load balancing")
    return version

