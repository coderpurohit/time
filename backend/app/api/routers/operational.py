
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from .. import schemas
from ...infrastructure.database import get_db
from ...infrastructure import models
from typing import Optional, Dict, Any
from ...services.timetable_service import TimetableService
from fastapi import BackgroundTasks

router = APIRouter()

@router.get('/time-slots', response_model=List[schemas.TimeSlot])
def get_time_slots(db: Session = Depends(get_db)):
    """Get all configured time slots"""
    return db.query(models.TimeSlot).all()

@router.get('/time-slots/configure')
@router.post('/time-slots/configure')
def configure_time_slots(number_of_periods: int = 7, period_length_minutes: int = 60, start_hour: int = 9, db: Session = Depends(get_db)):
    """Recreate time slots for Monday-Friday with the given number of periods and period length.
    - `number_of_periods`: how many periods per day (int)
    - `period_length_minutes`: duration of each period in minutes (int)
    - `start_hour`: starting hour for period 1 (24h integer, default 9)
    This will clear existing `TimeSlot` entries and create the new ones. Lunch/breaks can be represented by setting `is_break=True` for specific periods later in UI.
    """
    if number_of_periods < 1 or period_length_minutes < 1:
        raise HTTPException(status_code=400, detail="Invalid period configuration")

    # Validate inputs
    if start_hour < 0 or start_hour > 23:
        raise HTTPException(status_code=400, detail="start_hour must be between 0 and 23")

    # Prevent configurations that would go past midnight
    minutes_per_day = 24 * 60
    last_end = start_hour * 60 + number_of_periods * period_length_minutes
    if last_end > minutes_per_day:
        raise HTTPException(status_code=400, detail=f"Configured periods end past midnight ({last_end} minutes). Reduce period count or duration.")

    # Clear existing time slots
    db.query(models.TimeSlot).delete()

    created = 0
    for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
        minutes = start_hour * 60
        for p in range(1, number_of_periods + 1):
            start_h = (minutes // 60) % 24
            start_m = minutes % 60
            end_minutes = minutes + period_length_minutes
            end_h = (end_minutes // 60) % 24
            end_m = end_minutes % 60

            start_time = f"{start_h:02d}:{start_m:02d}"
            end_time = f"{end_h:02d}:{end_m:02d}"

            ts = models.TimeSlot(day=day, period=p, start_time=start_time, end_time=end_time, is_break=False)
            db.add(ts)
            created += 1
            minutes = end_minutes

    db.commit()
    # Persist these values into ScheduleConfig so UI callers that use this endpoint
    # have the changes reflected in the saved configuration.
    try:
        cfg = db.query(models.ScheduleConfig).first()
        if not cfg:
            cfg = models.ScheduleConfig()

        # store start time as HH:00 using the integer start_hour input
        cfg.day_start_time = f"{start_hour:02d}:00"
        cfg.number_of_periods = number_of_periods
        cfg.period_duration_minutes = period_length_minutes
        cfg.working_minutes_per_day = number_of_periods * period_length_minutes
        cfg.schedule_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

        db.add(cfg)
        db.commit()
        db.refresh(cfg)
    except Exception:
        # Non-fatal: timeslots were created; if config persistence fails, return success for timeslots
        pass

    return {"message": f"Created {created} time slots ({number_of_periods} periods/day)", "config_saved": True}


def _hhmm_to_minutes(t: str) -> int:
    h, m = map(int, t.split(':'))
    return h * 60 + m


def _minutes_to_hhmm(m: int) -> str:
    h = (m // 60) % 24
    mm = m % 60
    return f"{h:02d}:{mm:02d}"


def generate_time_slots_from_config(cfg: models.ScheduleConfig, db: Session):
    """Generate TimeSlot rows from a ScheduleConfig instance.
    Supports: explicit number_of_periods + period_duration_minutes OR period_duration + working_minutes/day (auto-calc periods).
    Handles breaks (by position) and a lunch break (start/end).
    """
    # clear existing slots
    db.query(models.TimeSlot).delete()

    # parse basic values
    start_min = _hhmm_to_minutes(cfg.day_start_time or "09:00")
    working_minutes = None
    if cfg.working_minutes_per_day:
        working_minutes = int(cfg.working_minutes_per_day)
    elif cfg.day_end_time:
        end_min = _hhmm_to_minutes(cfg.day_end_time)
        # allow end on same day; if end < start, assume next day
        working_minutes = (end_min - start_min) if end_min >= start_min else (24*60 - start_min + end_min)

    period_dur = cfg.period_duration_minutes
    num_periods = cfg.number_of_periods

    # compute break total duration
    breaks = cfg.breaks or []
    total_break_minutes = 0
    for b in breaks:
        try:
            total_break_minutes += int(b.get("duration", 0))
        except Exception:
            pass

    # lunch duration
    lunch_minutes = 0
    try:
        if cfg.lunch_break_start and cfg.lunch_break_end:
            lunch_minutes = _hhmm_to_minutes(cfg.lunch_break_end) - _hhmm_to_minutes(cfg.lunch_break_start)
            if lunch_minutes < 0:
                lunch_minutes = 0
    except Exception:
        lunch_minutes = 0

    # Determine number_of_periods if missing
    if not num_periods:
        if period_dur and working_minutes:
            # subtract breaks and lunch from available working minutes
            available = working_minutes - total_break_minutes - lunch_minutes
            if available <= 0:
                raise HTTPException(status_code=400, detail="Working minutes too small for breaks/lunch")
            num_periods = max(1, available // period_dur)
        else:
            raise HTTPException(status_code=400, detail="Either number_of_periods or both period_duration and working_minutes/day (or day_end_time) must be provided")

    # Determine period_duration if missing
    if not period_dur:
        if working_minutes and num_periods:
            available = working_minutes - total_break_minutes - lunch_minutes
            if available <= 0:
                raise HTTPException(status_code=400, detail="Working minutes too small for breaks/lunch")
            period_dur = max(1, available // num_periods)
        else:
            raise HTTPException(status_code=400, detail="Either period_duration or both number_of_periods and working_minutes/day must be provided")

    # validate ending before midnight
    last_end = start_min + num_periods * period_dur + total_break_minutes + lunch_minutes
    if last_end > 24*60:
        raise HTTPException(status_code=400, detail="Configured schedule extends past midnight")

    created = 0
    days = cfg.schedule_days or ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    for day in days:
        minutes = start_min
        period_idx = 1
        lunch_inserted = False
        for p in range(1, num_periods + 1):
            # before creating next period, check if lunch should start now (absolute time)
            if cfg.lunch_break_start and not lunch_inserted:
                try:
                    lunch_start_min = _hhmm_to_minutes(cfg.lunch_break_start)
                    lunch_end_min = _hhmm_to_minutes(cfg.lunch_break_end)
                    if minutes >= lunch_start_min:
                        # insert lunch break slot
                        ts = models.TimeSlot(day=day, period=0, start_time=_minutes_to_hhmm(lunch_start_min), end_time=_minutes_to_hhmm(lunch_end_min), is_break=True)
                        db.add(ts)
                        created += 1
                        minutes = lunch_end_min
                        lunch_inserted = True
                except Exception:
                    pass

            # create period slot
            start_t = _minutes_to_hhmm(minutes)
            end_minutes = minutes + period_dur
            end_t = _minutes_to_hhmm(end_minutes)
            ts = models.TimeSlot(day=day, period=period_idx, start_time=start_t, end_time=end_t, is_break=False)
            db.add(ts)
            created += 1
            minutes = end_minutes
            period_idx += 1

            # after this period, check breaks by position
            for b in breaks:
                if b.get("position") == p:
                    dur = int(b.get("duration", 0))
                    if dur > 0:
                        b_start = minutes
                        b_end = minutes + dur
                        tsb = models.TimeSlot(day=day, period=0, start_time=_minutes_to_hhmm(b_start), end_time=_minutes_to_hhmm(b_end), is_break=True)
                        db.add(tsb)
                        created += 1
                        minutes = b_end

    db.commit()
    return created

@router.get('/schedule-config')
def get_schedule_config(db: Session = Depends(get_db)):
    """Get current schedule configuration (teaching hours, lunch break, schedule days)"""
    cfg = db.query(models.ScheduleConfig).first()
    if not cfg:
        # Create default
        cfg = models.ScheduleConfig()
        db.add(cfg)
        db.commit()
        db.refresh(cfg)
    return {
        "id": cfg.id,
        "day_start_time": cfg.day_start_time,
        "day_end_time": cfg.day_end_time,
        "working_minutes_per_day": cfg.working_minutes_per_day,
        "number_of_periods": cfg.number_of_periods,
        "period_duration_minutes": cfg.period_duration_minutes,
        "breaks": cfg.breaks,
        "lunch_break_start": cfg.lunch_break_start,
        "lunch_break_end": cfg.lunch_break_end,
        "schedule_days": cfg.schedule_days,
        "institution": cfg.institution,
        "updated_at": cfg.updated_at.isoformat() if cfg.updated_at else None
    }

@router.post('/schedule-config')
def update_schedule_config(config: schemas.ScheduleConfigBase, db: Session = Depends(get_db)):
    """Update schedule configuration, regenerate time slots AND auto-regenerate timetable if one exists.
    
    This is the main endpoint for admins to update the schedule. Any changes here will:
    1. Update the configuration
    2. Regenerate time slots
    3. If a timetable exists, delete it and generate a new one automatically
    """
    cfg = db.query(models.ScheduleConfig).first()
    if not cfg:
        cfg = models.ScheduleConfig()

    cfg.day_start_time = config.day_start_time
    cfg.day_end_time = config.day_end_time
    cfg.working_minutes_per_day = config.working_minutes_per_day
    cfg.number_of_periods = config.number_of_periods
    cfg.period_duration_minutes = config.period_duration_minutes
    # convert breaks to plain list of dicts
    cfg.breaks = [b.model_dump() if hasattr(b, 'model_dump') else b for b in config.breaks]
    cfg.lunch_break_start = config.lunch_break_start
    cfg.lunch_break_end = config.lunch_break_end
    cfg.schedule_days = config.schedule_days
    cfg.institution = config.institution

    db.add(cfg)
    db.commit()
    db.refresh(cfg)

    print(f"[schedule-config] Config updated")

    # regenerate time slots based on new config
    try:
        created = generate_time_slots_from_config(cfg, db)
        print(f"[schedule-config] Time slots regenerated: {created}")
    except HTTPException:
        # propagate validation error
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate time slots: {e}")

    # AUTO-REGENERATE TIMETABLE if one exists
    try:
        existing_timetable = db.query(models.TimetableVersion).first()
        if existing_timetable:
            print(f"[schedule-config] Existing timetable found. Auto-regenerating...")
            # Delete old timetable
            deleted_entries = db.query(models.TimetableEntry).delete()
            deleted_versions = db.query(models.TimetableVersion).delete()
            db.commit()
            print(f"[schedule-config] Deleted old timetable: entries={deleted_entries}, versions={deleted_versions}")
            
            # Regenerate new timetable
            version = TimetableService.generate_and_save(db, method="csp", version_name="Auto-generated after schedule config")
            print(f"[schedule-config] New timetable generated: version_id={version.id}")
            
            return {
                "id": cfg.id,
                "day_start_time": cfg.day_start_time,
                "day_end_time": cfg.day_end_time,
                "working_minutes_per_day": cfg.working_minutes_per_day,
                "number_of_periods": cfg.number_of_periods,
                "period_duration_minutes": cfg.period_duration_minutes,
                "breaks": cfg.breaks,
                "lunch_break_start": cfg.lunch_break_start,
                "lunch_break_end": cfg.lunch_break_end,
                "schedule_days": cfg.schedule_days,
                "institution": cfg.institution,
                "updated_at": cfg.updated_at.isoformat() if cfg.updated_at else None,
                "timetable_regenerated": True,
                "timetable_version_id": version.id,
                "timetable_status": version.status
            }
    except HTTPException as he:
        raise
    except Exception as e:
        print(f"[schedule-config] Timetable generation failed: {e}")
        # Still return config success even if timetable generation fails
        return {
            "id": cfg.id,
            "day_start_time": cfg.day_start_time,
            "day_end_time": cfg.day_end_time,
            "working_minutes_per_day": cfg.working_minutes_per_day,
            "number_of_periods": cfg.number_of_periods,
            "period_duration_minutes": cfg.period_duration_minutes,
            "breaks": cfg.breaks,
            "lunch_break_start": cfg.lunch_break_start,
            "lunch_break_end": cfg.lunch_break_end,
            "schedule_days": cfg.schedule_days,
            "institution": cfg.institution,
            "updated_at": cfg.updated_at.isoformat() if cfg.updated_at else None,
            "timetable_regenerated": False,
            "warning": f"Schedule config updated successfully, but timetable regeneration failed: {str(e)}"
        }

    # No existing timetable - just return config
    return {
        "id": cfg.id,
        "day_start_time": cfg.day_start_time,
        "day_end_time": cfg.day_end_time,
        "working_minutes_per_day": cfg.working_minutes_per_day,
        "number_of_periods": cfg.number_of_periods,
        "period_duration_minutes": cfg.period_duration_minutes,
        "breaks": cfg.breaks,
        "lunch_break_start": cfg.lunch_break_start,
        "lunch_break_end": cfg.lunch_break_end,
        "schedule_days": cfg.schedule_days,
        "institution": cfg.institution,
        "updated_at": cfg.updated_at.isoformat() if cfg.updated_at else None,
        "created_time_slots": created
    }


@router.post('/apply-config')
def apply_config(config: schemas.ScheduleConfigBase, db: Session = Depends(get_db)):
    """[DEPRECATED - Use POST /schedule-config instead]
    
    Apply schedule configuration, validate, recreate time slots, clear old timetable, and regenerate timetable.
    This is kept for backward compatibility. New code should use POST /schedule-config instead.

    This endpoint performs the full flow described by the admin's "Apply All" action.
    It validates the basic time math, saves the configuration, deletes old timetable data,
    regenerates time slots, runs the timetable generator synchronously, and returns the new version.
    """
    # 1. Basic validation: schedule days present
    days = config.schedule_days or []
    if not days:
        raise HTTPException(status_code=400, detail="Invalid configuration: No working days provided.")

    # 2. Compute available_time (minutes)
    available = None
    if config.working_minutes_per_day:
        try:
            available = int(config.working_minutes_per_day)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid working_minutes_per_day")
    elif config.day_end_time and config.day_start_time:
        try:
            start_min = _hhmm_to_minutes(config.day_start_time)
            end_min = _hhmm_to_minutes(config.day_end_time)
            available = (end_min - start_min) if end_min >= start_min else (24*60 - start_min + end_min)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid day_start_time/day_end_time format")
    else:
        raise HTTPException(status_code=400, detail="Invalid configuration: provide working_minutes_per_day or day_end_time/day_start_time")

    # 3. Ensure number_of_periods and period_duration available for validation
    if not config.number_of_periods or not config.period_duration_minutes:
        # If missing one, try to derive so we can validate; if impossible, reject
        if config.number_of_periods and not config.period_duration_minutes:
            # derive duration as floor(available / number_of_periods)
            try:
                derived = max(1, int(available) // int(config.number_of_periods))
                period_dur = derived
            except Exception:
                raise HTTPException(status_code=400, detail="Invalid configuration: cannot derive period duration")
        elif config.period_duration_minutes and not config.number_of_periods:
            try:
                derived_n = max(1, int(available) // int(config.period_duration_minutes))
                period_dur = int(config.period_duration_minutes)
                # set number for validation
                config.number_of_periods = derived_n
            except Exception:
                raise HTTPException(status_code=400, detail="Invalid configuration: cannot derive number_of_periods")
        else:
            raise HTTPException(status_code=400, detail="Invalid configuration: number_of_periods and period_duration_minutes required")

    total_required = int(config.number_of_periods) * int(config.period_duration_minutes)

    # 4. Auto-adjust working_minutes_per_day if needed (flexibility for admin)
    # If admin wants more periods/duration, accept it and auto-adjust the working_minutes_per_day
    adjusted_working_minutes = int(available)
    if total_required > int(available):
        adjusted_working_minutes = total_required
        print(f"[apply-config] Auto-adjusting working_minutes_per_day from {available} to {adjusted_working_minutes} to accommodate {config.number_of_periods} periods × {config.period_duration_minutes} minutes")

    # 5. Save the config with adjusted working_minutes if necessary
    cfg = db.query(models.ScheduleConfig).first()
    if not cfg:
        cfg = models.ScheduleConfig()

    cfg.day_start_time = config.day_start_time
    cfg.day_end_time = config.day_end_time
    cfg.working_minutes_per_day = adjusted_working_minutes  # Use adjusted value
    cfg.number_of_periods = config.number_of_periods
    cfg.period_duration_minutes = config.period_duration_minutes
    cfg.breaks = [b.model_dump() if hasattr(b, 'model_dump') else b for b in config.breaks]
    cfg.lunch_break_start = config.lunch_break_start
    cfg.lunch_break_end = config.lunch_break_end
    cfg.schedule_days = config.schedule_days
    cfg.institution = config.institution

    db.add(cfg)
    db.commit()
    db.refresh(cfg)

    print(f"[apply-config] Received config: {config.dict()}")
    print(f"[apply-config] Final working_minutes_per_day: {cfg.working_minutes_per_day}")

    # 6. Delete old timetable data (versions and entries)
    try:
        deleted_entries = db.query(models.TimetableEntry).delete()
        deleted_versions = db.query(models.TimetableVersion).delete()
        db.commit()
        print(f"[apply-config] Deleted old timetable: entries={deleted_entries}, versions={deleted_versions}")
    except Exception as e:
        db.rollback()
        print(f"[apply-config] Failed to delete old timetable: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clear old timetable: {e}")

    # 7. Generate time slots from config (this clears existing TimeSlot rows)
    try:
        created = generate_time_slots_from_config(cfg, db)
        print(f"[apply-config] Generated time slots: {created}")
    except HTTPException:
        raise
    except Exception as e:
        print(f"[apply-config] Time slot generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate time slots: {e}")

    # 8. Run timetable generator synchronously and return the new timetable version
    try:
        print("[apply-config] Starting timetable generation (synchronous)")
        version = TimetableService.generate_and_save(db, method="csp", version_name="Auto-generated after config")
        print(f"[apply-config] Generation completed: version_id={version.id}")
    except HTTPException as he:
        # propagate solver infeasible errors
        raise
    except Exception as e:
        print(f"[apply-config] Generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate timetable: {e}")

    # 9. Return the newly created version summary
    return {
        "message": "Configuration applied successfully",
        "config": {
            "id": cfg.id,
            "day_start_time": cfg.day_start_time,
            "number_of_periods": cfg.number_of_periods,
            "period_duration_minutes": cfg.period_duration_minutes
        },
        "timetable": {
            "id": version.id,
            "name": version.name,
            "status": version.status,
            "is_valid": version.is_valid,
            "created_at": version.created_at.isoformat() if version.created_at else None
        }
    }

# Class Groups endpoints
@router.get("/class-groups", response_model=List[schemas.ClassGroup])
def get_class_groups(db: Session = Depends(get_db)):
    """Get all class groups"""
    return db.query(models.ClassGroup).all()

@router.post("/class-groups", response_model=schemas.ClassGroup)
def create_class_group(class_group: schemas.ClassGroupCreate, db: Session = Depends(get_db)):
    """Create a new class group"""
    db_group = models.ClassGroup(
        name=class_group.name,
        student_count=class_group.student_count
    )
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    return db_group

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
