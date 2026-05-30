from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from ...infrastructure.database import get_db
from ...infrastructure import models

router = APIRouter(prefix="/api/schedule-config", tags=["schedule-config"])


class BreakConfig(BaseModel):
    name: str
    start_time: str
    end_time: str


class DivisionSchedulePayload(BaseModel):
    """Per-division schedule configuration payload."""
    division: str           # e.g. "BE-A"
    start_time: str         # HH:MM
    end_time: str           # HH:MM
    lunch_start: str = "12:00"   # HH:MM
    lunch_end: str = "13:00"     # HH:MM
    breaks: List[BreakConfig] = []


# Legacy payload kept for backwards compatibility
class ScheduleConfigPayload(BaseModel):
    division: str
    classes: List[str]
    start_time: str
    end_time: str
    breaks: List[BreakConfig] = []


# ---------------------------------------------------------------------------
# New: per-division endpoints
# ---------------------------------------------------------------------------

@router.get("/divisions")
def list_divisions(db: Session = Depends(get_db)):
    """Return all class groups (divisions) with their saved config (if any)."""
    try:
        groups = db.query(models.ClassGroup).order_by(models.ClassGroup.name).all()
        configs_raw = db.query(models.ScheduleConfig).all()
        config_map: Dict[str, Any] = {}
        for c in configs_raw:
            if c.institution:
                config_map[c.institution.upper()] = {
                    "start_time": c.day_start_time or "08:15",
                    "end_time": c.day_end_time or "17:00",
                    "lunch_start": c.lunch_break_start or "12:00",
                    "lunch_end": c.lunch_break_end or "13:00",
                    "breaks": c.breaks or [],
                }

        result = []
        for g in groups:
            key = g.name.upper()
            saved = config_map.get(key)
            result.append({
                "division": g.name,
                "student_count": g.student_count,
                "start_time": saved["start_time"] if saved else "08:15",
                "end_time": saved["end_time"] if saved else "17:00",
                "lunch_start": saved["lunch_start"] if saved else "12:00",
                "lunch_end": saved["lunch_end"] if saved else "13:00",
                "breaks": saved["breaks"] if saved else [],
                "is_configured": saved is not None,
            })
        return {"divisions": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/division/save")
def save_division_config(
    payload: DivisionSchedulePayload,
    db: Session = Depends(get_db)
):
    """Save timetable configuration for a single division independently."""
    try:
        division = payload.division.upper()

        config = db.query(models.ScheduleConfig).filter(
            models.ScheduleConfig.institution == division
        ).first()

        if not config:
            config = models.ScheduleConfig(institution=division)
            db.add(config)

        config.day_start_time = payload.start_time
        config.day_end_time = payload.end_time
        config.lunch_break_start = payload.lunch_start
        config.lunch_break_end = payload.lunch_end
        config.breaks = [b.dict() for b in payload.breaks]

        db.commit()
        db.refresh(config)

        return {
            "status": "success",
            "message": f"Configuration saved for {division}",
            "division": division,
            "start_time": config.day_start_time,
            "end_time": config.day_end_time,
            "lunch_start": config.lunch_break_start,
            "lunch_end": config.lunch_break_end,
            "breaks": config.breaks,
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/division/{division}")
def get_division_config(division: str, db: Session = Depends(get_db)):
    """Get schedule configuration for a specific division."""
    try:
        division_key = division.upper()
        config = db.query(models.ScheduleConfig).filter(
            models.ScheduleConfig.institution == division_key
        ).first()

        if not config:
            return {
                "division": division,
                "start_time": "08:15",
                "end_time": "17:00",
                "lunch_start": "12:00",
                "lunch_end": "13:00",
                "breaks": [],
                "is_configured": False,
            }

        return {
            "division": division,
            "start_time": config.day_start_time,
            "end_time": config.day_end_time,
            "lunch_start": config.lunch_break_start or "12:00",
            "lunch_end": config.lunch_break_end or "13:00",
            "breaks": config.breaks or [],
            "is_configured": True,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# Legacy endpoints (kept for backwards-compat with old frontend)
# ---------------------------------------------------------------------------

@router.post("/save")
def save_schedule_config(
    payload: ScheduleConfigPayload,
    db: Session = Depends(get_db)
):
    """Save schedule configuration for a division (legacy endpoint)."""
    try:
        division = payload.division.upper()
        breaks = [b.dict() for b in payload.breaks]

        if not division:
            raise HTTPException(status_code=400, detail="Division is required")

        config = db.query(models.ScheduleConfig).filter(
            models.ScheduleConfig.institution == division
        ).first()

        if not config:
            config = models.ScheduleConfig(institution=division)
            db.add(config)

        config.day_start_time = payload.start_time
        config.day_end_time = payload.end_time
        config.breaks = breaks
        db.commit()

        return {
            "status": "success",
            "message": f"Configuration saved for {division} division",
            "division": division,
            "start_time": payload.start_time,
            "end_time": payload.end_time,
            "breaks": breaks,
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get/{division}")
def get_schedule_config(division: str, db: Session = Depends(get_db)):
    """Get schedule configuration for a specific division (legacy)."""
    try:
        division_key = division.upper()
        config = db.query(models.ScheduleConfig).filter(
            models.ScheduleConfig.institution == division_key
        ).first()

        if not config:
            return {
                "division": division,
                "start_time": "08:15",
                "end_time": "17:00",
                "breaks": [],
            }

        return {
            "division": division,
            "start_time": config.day_start_time,
            "end_time": config.day_end_time,
            "breaks": config.breaks or [],
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/all")
def get_all_schedule_configs(db: Session = Depends(get_db)):
    """Get all schedule configurations for all divisions."""
    try:
        configs = db.query(models.ScheduleConfig).all()
        result = {}
        for config in configs:
            div = config.institution or "DEFAULT"
            result[div] = {
                "start_time": config.day_start_time,
                "end_time": config.day_end_time,
                "lunch_start": config.lunch_break_start or "12:00",
                "lunch_end": config.lunch_break_end or "13:00",
                "breaks": config.breaks or [],
            }
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
