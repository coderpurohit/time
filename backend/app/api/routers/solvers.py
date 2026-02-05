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
    Generate and save a new timetable version. 
    Heavy generations can be moved to background if needed, but for now we return the version metadata.
    """
    version = models.TimetableVersion(name=name, algorithm=method, status="processing")
    db.add(version)
    db.commit()
    db.refresh(version)

    def run_generation(v_id: int):
        # We need a fresh session for background tasks usually, but here we reuse for simplicity
        try:
            TimetableService.generate_in_background(v_id, method)
        except Exception as e:
            print(f"Background Gen Error: {e}")

    background_tasks.add_task(run_generation, version.id)
    return version

