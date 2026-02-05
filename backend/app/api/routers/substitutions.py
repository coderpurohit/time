from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.infrastructure.database import get_db
from app.infrastructure import models
from app.api import schemas
from app.services.auto_assignment import AutoAssignmentService

router = APIRouter(prefix="/api/substitutions", tags=["substitutions"])


@router.post("/mark-absent", response_model=schemas.AbsentResponse)
def mark_teacher_absent(request: schemas.MarkAbsentRequest, db: Session = Depends(get_db)):
    """
    Mark a teacher as absent for a specific date.
    Returns all affected classes and suggested substitute teachers.
    """
    # Verify teacher exists
    teacher = db.query(models.Teacher).filter(models.Teacher.id == request.teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail=f"Teacher with id {request.teacher_id} not found")
    
    # Find all classes taught by this teacher on the given date
    # Get the latest timetable version
    latest_version = db.query(models.TimetableVersion).order_by(models.TimetableVersion.created_at.desc()).first()
    
    if not latest_version:
        raise HTTPException(status_code=404, detail="No timetable found. Please generate a timetable first.")
    
    # Get all entries for this teacher in the latest timetable
    entries = db.query(models.TimetableEntry).filter(
        models.TimetableEntry.version_id == latest_version.id,
        models.TimetableEntry.teacher_id == request.teacher_id
    ).all()
    
    if not entries:
        return schemas.AbsentResponse(
            teacher_name=teacher.name,
            date=request.date,
            affected_classes=[],
            suggested_substitutes=[]
        )
    
    # Build affected classes list
    affected_classes = []
    time_slot_ids = set()
    
    for entry in entries:
        time_slot = db.query(models.TimeSlot).filter(models.TimeSlot.id == entry.time_slot_id).first()
        subject = db.query(models.Subject).filter(models.Subject.id == entry.subject_id).first()
        room = db.query(models.Room).filter(models.Room.id == entry.room_id).first()
        class_group = db.query(models.ClassGroup).filter(models.ClassGroup.id == entry.class_group_id).first()
        
        if time_slot and subject and room and class_group:
            affected_classes.append(schemas.AffectedClass(
                entry_id=entry.id,
                subject_name=subject.name,
                time_slot=f"{time_slot.day} {time_slot.start_time}-{time_slot.end_time}",
                class_group_name=class_group.name,
                room_name=room.name
            ))
            time_slot_ids.add(entry.time_slot_id)
    
    # Find suggested substitute teachers
    # Get all teachers except the absent one
    all_teachers = db.query(models.Teacher).filter(models.Teacher.id != request.teacher_id).all()
    
    suggested_substitutes = []
    for candidate in all_teachers:
        # Check if candidate is free during all the required time slots
        candidate_entries = db.query(models.TimetableEntry).filter(
            models.TimetableEntry.version_id == latest_version.id,
            models.TimetableEntry.teacher_id == candidate.id,
            models.TimetableEntry.time_slot_id.in_(time_slot_ids)
        ).all()
        
        # If candidate has no classes during these slots, they're available
        is_available_for_all = len(candidate_entries) == 0
        
        # Count how many classes they have that day (for workload consideration)
        # For simplicity, we'll just count total classes in this timetable
        total_classes = db.query(models.TimetableEntry).filter(
            models.TimetableEntry.version_id == latest_version.id,
            models.TimetableEntry.teacher_id == candidate.id
        ).count()
        
        # Check if they teach the same subjects
        candidate_subjects = db.query(models.Subject).filter(
            models.Subject.teacher_id == candidate.id
        ).all()
        candidate_subject_names = {s.name for s in candidate_subjects}
        
        absent_teacher_subjects = db.query(models.Subject).filter(
            models.Subject.teacher_id == request.teacher_id
        ).all()
        absent_subject_names = {s.name for s in absent_teacher_subjects}
        
        teaches_same_subject = bool(candidate_subject_names & absent_subject_names)
        
        if is_available_for_all or teaches_same_subject:
            suggested_substitutes.append(schemas.SuggestedTeacher(
                teacher_id=candidate.id,
                teacher_name=candidate.name,
                available_for_all=is_available_for_all,
                teaches_same_subject=teaches_same_subject,
                current_classes_that_day=total_classes
            ))
    
    # Sort by priority: available + same subject > available > same subject
    suggested_substitutes.sort(
        key=lambda x: (x.available_for_all, x.teaches_same_subject, -x.current_classes_that_day),
        reverse=True
    )
    
    return schemas.AbsentResponse(
        teacher_name=teacher.name,
        date=request.date,
        affected_classes=affected_classes,
        suggested_substitutes=suggested_substitutes[:5]  # Top 5 suggestions
    )


@router.post("/assign", response_model=dict)
def assign_substitute(request: schemas.AssignSubstituteRequest, db: Session = Depends(get_db)):
    """
    Assign a substitute teacher to a specific class.
    """
    # Verify the timetable entry exists
    entry = db.query(models.TimetableEntry).filter(
        models.TimetableEntry.id == request.timetable_entry_id
    ).first()
    
    if not entry:
        raise HTTPException(status_code=404, detail=f"Timetable entry {request.timetable_entry_id} not found")
    
    # Verify substitute teacher exists
    substitute = db.query(models.Teacher).filter(
        models.Teacher.id == request.substitute_teacher_id
    ).first()
    
    if not substitute:
        raise HTTPException(status_code=404, detail=f"Substitute teacher {request.substitute_teacher_id} not found")
    
    # Check if substitution already exists
    existing = db.query(models.Substitution).filter(
        models.Substitution.date == request.date,
        models.Substitution.timetable_entry_id == request.timetable_entry_id
    ).first()
    
    if existing:
        # Update existing substitution
        existing.substitute_teacher_id = request.substitute_teacher_id
        existing.status = "confirmed"
        db.commit()
        substitution_id = existing.id
    else:
        # Create new substitution
        substitution = models.Substitution(
            date=request.date,
            timetable_entry_id=request.timetable_entry_id,
            original_teacher_id=request.original_teacher_id,
            substitute_teacher_id=request.substitute_teacher_id,
            status="confirmed"
        )
        db.add(substitution)
        db.commit()
        db.refresh(substitution)
        substitution_id = substitution.id
    
    # Get class details for response
    subject = db.query(models.Subject).filter(models.Subject.id == entry.subject_id).first()
    time_slot = db.query(models.TimeSlot).filter(models.TimeSlot.id == entry.time_slot_id).first()
    
    return {
        "substitution_id": substitution_id,
        "status": "confirmed",
        "message": f"{substitute.name} assigned to {subject.name if subject else 'class'} on {time_slot.day if time_slot else 'unknown'} {time_slot.start_time if time_slot else ''}"
    }


@router.post("/cancel-class", response_model=dict)
def cancel_class(request: schemas.CancelClassRequest, db: Session = Depends(get_db)):
    """
    Cancel a class due to teacher absence and no substitute available.
    """
    # Verify the timetable entry exists
    entry = db.query(models.TimetableEntry).filter(
        models.TimetableEntry.id == request.timetable_entry_id
    ).first()
    
    if not entry:
        raise HTTPException(status_code=404, detail=f"Timetable entry {request.timetable_entry_id} not found")
    
    # Create substitution record with status 'cancelled'
    substitution = models.Substitution(
        date=request.date,
        timetable_entry_id=request.timetable_entry_id,
        original_teacher_id=request.original_teacher_id,
        substitute_teacher_id=None,
        status="cancelled"
    )
    db.add(substitution)
    db.commit()
    db.refresh(substitution)
    
    return {
        "substitution_id": substitution.id,
        "status": "cancelled",
        "message": f"Class cancelled: {request.reason}"
    }


@router.get("/by-date/{date}", response_model=List[schemas.SubstitutionResponse])
def get_substitutions_by_date(date: str, db: Session = Depends(get_db)):
    """
    Get all substitutions for a specific date.
    """
    substitutions = db.query(models.Substitution).filter(
        models.Substitution.date == date
    ).all()
    
    result = []
    for sub in substitutions:
        # Get related data
        entry = db.query(models.TimetableEntry).filter(
            models.TimetableEntry.id == sub.timetable_entry_id
        ).first()
        
        if not entry:
            continue
        
        original_teacher = db.query(models.Teacher).filter(
            models.Teacher.id == sub.original_teacher_id
        ).first()
        
        substitute_teacher = None
        if sub.substitute_teacher_id:
            substitute_teacher = db.query(models.Teacher).filter(
                models.Teacher.id == sub.substitute_teacher_id
            ).first()
        
        subject = db.query(models.Subject).filter(models.Subject.id == entry.subject_id).first()
        time_slot = db.query(models.TimeSlot).filter(models.TimeSlot.id == entry.time_slot_id).first()
        class_group = db.query(models.ClassGroup).filter(models.ClassGroup.id == entry.class_group_id).first()
        
        result.append(schemas.SubstitutionResponse(
            id=sub.id,
            date=sub.date,
            original_teacher=original_teacher.name if original_teacher else "Unknown",
            substitute_teacher=substitute_teacher.name if substitute_teacher else None,
            subject=subject.name if subject else "Unknown",
            time_slot=f"{time_slot.day} {time_slot.start_time}-{time_slot.end_time}" if time_slot else "Unknown",
            class_group=class_group.name if class_group else "Unknown",
            status=sub.status
        ))
    
    return result


@router.get("/available-teachers")
def get_available_teachers(date: str, time_slot_id: int, db: Session = Depends(get_db)):
    """
    Find teachers available for a specific time slot on a given date.
    """
    # Get latest timetable
    latest_version = db.query(models.TimetableVersion).order_by(
        models.TimetableVersion.created_at.desc()
    ).first()
    
    if not latest_version:
        raise HTTPException(status_code=404, detail="No timetable found")
    
    # Get all teachers
    all_teachers = db.query(models.Teacher).all()
    
    # Find teachers who are NOT teaching during this time slot
    busy_teacher_ids = db.query(models.TimetableEntry.teacher_id).filter(
        models.TimetableEntry.version_id == latest_version.id,
        models.TimetableEntry.time_slot_id == time_slot_id
    ).all()
    
    busy_ids = {t[0] for t in busy_teacher_ids}
    
    available = []
    for teacher in all_teachers:
        if teacher.id not in busy_ids:
            # Get their subject expertise
            subjects = db.query(models.Subject).filter(
                models.Subject.teacher_id == teacher.id
            ).all()
            
            # Count current workload
            workload = db.query(models.TimetableEntry).filter(
                models.TimetableEntry.version_id == latest_version.id,
                models.TimetableEntry.teacher_id == teacher.id
            ).count()
            
            available.append({
                "teacher_id": teacher.id,
                "name": teacher.name,
                "subject_expertise": [s.name for s in subjects],
                "current_workload": f"{workload}/{teacher.max_hours_per_week} hours"
            })
    
    return available


# ========== NEW AUTO-ASSIGNMENT ENDPOINTS ==========

@router.post("/auto-assign")
def auto_assign_substitute(
    teacher_id: int,
    date: str,
    auto_notify: bool = False,
    db: Session = Depends(get_db)
):
    """
    🤖 AUTOMATED: One-click auto-assignment of substitute teacher.
    
    Automatically finds and assigns the best substitute teacher for all classes
    of an absent teacher using intelligent scoring algorithm.
    
    **How it works:**
    1. Finds all classes taught by the absent teacher
    2. Scores all available teachers based on:
       - Availability (100 points)
       - Subject expertise (80 points)
       - Workload balance (50 points)
    3. Assigns the highest-scoring substitute to all classes
    4. Creates substitution records
    5. (Optional) Sends notifications
    
    **Parameters:**
    - teacher_id: ID of the absent teacher
    - date: Date of absence (YYYY-MM-DD format)
    - auto_notify: Whether to send notifications (default: False)
    
    **Returns:**
    - Complete assignment report with confidence scores
    - Alternative substitute suggestions
    - Details of all affected classes
    """
    service = AutoAssignmentService(db)
    result = service.auto_assign_substitutes(teacher_id, date, auto_notify)
    
    if not result.get("success", False) and "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result


@router.get("/suggestions/{entry_id}/ranked")
def get_ranked_substitute_suggestions(
    entry_id: int,
    top_n: int = 5,
    db: Session = Depends(get_db)
):
    """
    🎯 Get AI-ranked substitute suggestions for a specific class.
    
    Returns a ranked list of potential substitute teachers with:
    - Intelligent scoring based on multiple factors
    - Availability status
    - Subject expertise match
    - Current workload information
    - Detailed score breakdown
    
    **Parameters:**
    - entry_id: Timetable entry ID
    - top_n: Number of top suggestions to return (default: 5)
    
    **Returns:**
    - Ranked list of substitute teachers with scores and details
    """
    service = AutoAssignmentService(db)
    suggestions = service.get_ranked_suggestions(entry_id, top_n)
    
    return {
        "entry_id": entry_id,
        "total_suggestions": len(suggestions),
        "ranked_substitutes": suggestions
    }


@router.post("/auto-assign-bulk")
def auto_assign_bulk(
    absences: List[dict],
    auto_notify: bool = False,
    db: Session = Depends(get_db)
):
    """
    🚀 BULK AUTO-ASSIGNMENT: Handle multiple absent teachers at once.
    
    Efficiently processes multiple teacher absences in a single request.
    Perfect for handling planned absences, conferences, or emergency situations.
    
    **Input Format:**
    ```json
    {
        "absences": [
            {"teacher_id": 1, "date": "2026-02-05"},
            {"teacher_id": 3, "date": "2026-02-05"},
            {"teacher_id": 5, "date": "2026-02-06"}
        ],
        "auto_notify": true
    }
    ```
    
    **Returns:**
    - Aggregated results for all absences
    - Success/failure status for each teacher
    - Total statistics
    """
    service = AutoAssignmentService(db)
    results = []
    
    for absence in absences:
        teacher_id = absence.get("teacher_id")
        date = absence.get("date")
        
        if not teacher_id or not date:
            results.append({
                "teacher_id": teacher_id,
                "date": date,
                "success": False,
                "error": "Missing teacher_id or date"
            })
            continue
        
        result = service.auto_assign_substitutes(teacher_id, date, auto_notify)
        results.append(result)
    
    # Calculate statistics
    successful = sum(1 for r in results if r.get("success", False))
    total_classes = sum(r.get("affected_classes", 0) for r in results)
    
    return {
        "total_absences_processed": len(absences),
        "successful_assignments": successful,
        "failed_assignments": len(absences) - successful,
        "total_classes_affected": total_classes,
        "results": results
    }

