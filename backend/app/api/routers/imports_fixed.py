from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from typing import Optional, List
import csv
import io
from sqlalchemy.orm import Session
from sqlalchemy import text

from ...infrastructure.database import get_db
from ...infrastructure import models

router = APIRouter()

@router.post("/")
async def import_dataset(
    dataset: str = Form(...), 
    file: UploadFile = File(...), 
    force_clear_existing: str = Form("false"),
    db: Session = Depends(get_db)
):
    """Import CSV data - FIXED VERSION"""
    
    # Simple validation
    if not file.filename.lower().endswith(('.csv', '.txt')):
        raise HTTPException(status_code=400, detail="Only CSV/TXT files supported")

    # Read file content
    try:
        content = await file.read()
        text_content = content.decode('utf-8-sig')  # Handle BOM
    except Exception:
        raise HTTPException(status_code=400, detail="Cannot read file")

    # Parse CSV
    try:
        reader = csv.DictReader(io.StringIO(text_content))
        rows = list(reader)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid CSV format")

    if not rows:
        raise HTTPException(status_code=400, detail="CSV file is empty")

    # Parse clear flag safely
    should_clear = force_clear_existing.lower() == 'true'
    
    try:
        # Clear existing if requested
        if should_clear and dataset == 'teachers':
            # Clear in safe order
            db.execute(text("DELETE FROM timetable_entries"))
            db.execute(text("DELETE FROM timetable_versions"))
            db.execute(text("DELETE FROM lesson_teachers"))
            db.execute(text("DELETE FROM lesson_class_groups"))
            db.execute(text("DELETE FROM lesson_subjects"))
            db.execute(text("DELETE FROM lessons"))
            db.execute(text("DELETE FROM substitutions"))
            db.execute(text("UPDATE subjects SET teacher_id = NULL"))
            db.execute(text("DELETE FROM teachers"))
            db.commit()

        # Import teachers
        if dataset == 'teachers':
            added = 0
            for row in rows:
                name = (row.get('name') or '').strip()
                email = (row.get('email') or '').strip()
                max_hours = 18
                
                try:
                    max_hours = int(row.get('max_hours_per_week') or 18)
                except:
                    max_hours = 18
                
                if not name:
                    continue
                    
                if not email:
                    # Generate email from name
                    clean_name = name.lower().replace('dr.', '').replace('prof.', '').strip()
                    email = clean_name.replace(' ', '.') + '@college.edu'
                
                # Check if exists
                existing = db.query(models.Teacher).filter(models.Teacher.email == email).first()
                if existing:
                    existing.name = name
                    existing.max_hours_per_week = max_hours
                else:
                    teacher = models.Teacher(name=name, email=email, max_hours_per_week=max_hours)
                    db.add(teacher)
                    added += 1
            
            db.commit()
            return {"message": f"Imported {added} teachers", "added": added}
        
        else:
            raise HTTPException(status_code=400, detail="Only 'teachers' dataset supported")
            
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Import failed: {type(e).__name__}")