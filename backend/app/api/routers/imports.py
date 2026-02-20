from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from typing import Optional, List
import csv
import io
from sqlalchemy.orm import Session

from ...infrastructure.database import get_db
from ...infrastructure import models

router = APIRouter()


def parse_bool(value: str) -> bool:
    """Parse boolean from string"""
    if not value:
        return False
    return value.lower() in ('true', '1', 'yes', 'y')


def parse_int(value: str, default: int = 0) -> int:
    """Parse integer from string with default"""
    if not value:
        return default
    try:
        return int(float(value)) # Handle '3.0' as 3
    except ValueError:
        return default

def clean_header(header: str) -> str:
    """Clean CSV header name"""
    if not header:
        return ""
    # Remove BOM if present at start of string (in case logic missed it)
    return header.lower().strip().replace('\ufeff', '')

@router.post("/")
async def import_dataset(
    dataset: str = Form(...), 
    file: UploadFile = File(...), 
    force_clear_existing: str = Form("false"),
    db: Session = Depends(get_db)
):
    """
    Import endpoint for CSV datasets.
    
    Supported dataset types:
    - "teachers": CSV with headers name, email, max_hours_per_week
    - "rooms": CSV with headers name, capacity, type, resources (semicolon-separated)
    - "subjects": CSV with headers name, code, is_lab, credits, required_room_type, duration_slots, teacher_email
    - "classgroups": CSV with headers name, student_count
    
    Set force_clear_existing="true" to delete all existing records before importing.
    """
    if not any(file.filename.lower().endswith(ext) for ext in ['.csv', '.tsv', '.txt']):
        raise HTTPException(status_code=400, detail="Only CSV, TSV, or TXT files are supported")

    content = await file.read()
    try:
        # Try UTF-8 first, then fallback to latin-1
        try:
            text = content.decode('utf-8')
        except UnicodeDecodeError:
            text = content.decode('latin-1')
    except Exception:
        raise HTTPException(status_code=400, detail="Unable to decode uploaded file")

    # Handle BOM if present
    if text.startswith('\ufeff'):
        text = text[1:]
    
    
    # Clean empty lines from start
    lines = [line for line in text.split('\n') if line.strip()]
    cleaned_text = '\n'.join(lines)
    
    if not lines:
         raise HTTPException(status_code=400, detail="CSV file appears to be empty")

    # Detect delimiter using Sniffer with fallback
    delimiter = ','
    try:
        dialect = csv.Sniffer().sniff(cleaned_text[:4096], delimiters=',;\t')
        delimiter = dialect.delimiter
    except:
        # Fallback to manual detection
        first_line = lines[0]
        if ';' in first_line and first_line.count(';') > first_line.count(','):
            delimiter = ';'
        elif '\t' in first_line and first_line.count('\t') > first_line.count(','):
            delimiter = '\t'
        
    print(f"DEBUG: Detected delimiter '{delimiter}' for {dataset}")

    reader = csv.DictReader(io.StringIO(cleaned_text), delimiter=delimiter)
    
    # Normalize header names (lowercase, strip whitespace)
    if reader.fieldnames:
        reader.fieldnames = [clean_header(f) for f in reader.fieldnames]
        
        # EDGE CASE: If we have 1 column but it contains commas/semicolons, we probably guessed wrong or it's quoted weirdly
        if len(reader.fieldnames) == 1 and (',' in reader.fieldnames[0] or ';' in reader.fieldnames[0]):
             print(f"DEBUG: Single column detected with delimiters inside: {reader.fieldnames[0]}. Forcing comma.")
             # Force comma retry if it looks like a comma-separated list
             if ',' in reader.fieldnames[0]:
                 reader = csv.DictReader(io.StringIO(cleaned_text), delimiter=',')
                 if reader.fieldnames:
                     reader.fieldnames = [clean_header(f) for f in reader.fieldnames]

        print(f"DEBUG: Normalized headers: {reader.fieldnames}")
    else:
         raise HTTPException(status_code=400, detail="CSV file appears to be empty or missing headers")

    try:
        # Parse boolean flag manually to avoid form data issues
        print(f"DEBUG: force_clear_existing raw value: '{force_clear_existing}', type: {type(force_clear_existing)}")
        should_clear = str(force_clear_existing).lower().strip() == 'true'
        print(f"DEBUG: should_clear evaluated to: {should_clear}")
        
        # Clear existing data if requested
        cleared = 0
        timetable_cleared = False
        if should_clear:
            # Clear timetable first to avoid broken foreign key references
            timetable_count = db.query(models.TimetableEntry).count()
            if timetable_count > 0:
                db.query(models.TimetableEntry).delete()
                db.query(models.TimetableVersion).delete()
                timetable_cleared = True
            
            if dataset == 'teachers':
                db.query(models.Subject).update({models.Subject.teacher_id: None})
                cleared = db.query(models.Teacher).delete()
            elif dataset == 'rooms':
                cleared = db.query(models.Room).delete()
            elif dataset == 'subjects':
                cleared = db.query(models.Subject).delete()
            elif dataset == 'classgroups' or dataset == 'class_groups':
                cleared = db.query(models.ClassGroup).delete()
            db.commit()
        
        if dataset == 'teachers':
            result = await _import_teachers(reader, db)
        elif dataset == 'rooms':
            result = await _import_rooms(reader, db)
        elif dataset == 'subjects':
            result = await _import_subjects(reader, db)
        elif dataset == 'classgroups' or dataset == 'class_groups':
            result = await _import_classgroups(reader, db)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported dataset type: {dataset}. Supported: teachers, rooms, subjects, classgroups")
        
        if should_clear:
            result["cleared"] = cleared
            if timetable_cleared:
                result["timetable_cleared"] = True
                result["message"] += " (timetable also cleared - please regenerate)"
        return result

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")


async def _import_teachers(reader: csv.DictReader, db: Session) -> dict:
    """Import teachers from CSV"""
    added = 0
    updated = 0
    skipped = 0
    errors = []
    
    # Verify headers
    required = {'name'} # minimal requirement
    headers = set(reader.fieldnames)
    # Check if 'name' or 'full_name' or 'teacher_name' exists
    if not any(h in headers for h in ['name', 'full_name', 'teacher_name']):
         return {
             "message": f"Missing required column: 'name'. Found headers: {list(headers)}", 
             "errors": [f"CSV must have a 'name' column. Found: {list(headers)}"], 
             "added": 0
         }

    rows_list = list(reader)
    if len(rows_list) == 0:
        return {"message": "No data rows found in CSV", "added": 0, "skipped": 0}
    
    for idx, row in enumerate(rows_list, start=2):  # Start at 2 (1 is header)
        name = (row.get('name') or row.get('full_name') or row.get('teacher_name') or '').strip()
        email = (row.get('email') or '').strip()
        teacher_id = (row.get('teacher_id') or row.get('id') or '').strip()
        max_hours = parse_int(row.get('max_hours_per_week') or row.get('max_hours'), 18)

        if not name:
            errors.append(f"Row {idx}: Missing teacher name")
            skipped += 1
            continue
        
        # Auto-generate email if missing
        if not email:
            # Create email from name or teacher_id
            if teacher_id:
                email = f"{teacher_id.lower()}@college.edu"
            else:
                # Generate from name: "Dr. Amit Sharma" -> "amit.sharma@college.edu"
                name_parts = name.lower().replace('dr.', '').replace('prof.', '').strip().split()
                email = '.'.join(name_parts) + '@college.edu'

        # UPSERT: Check duplicate by email and update
        existing = db.query(models.Teacher).filter(models.Teacher.email == email).first()
        if existing:
            # Update existing record
            existing.name = name
            existing.max_hours_per_week = max_hours
            updated += 1
            print(f"DEBUG: Updated teacher {email}")
        else:
            teacher = models.Teacher(name=name, email=email, max_hours_per_week=max_hours)
            db.add(teacher)
            added += 1

    db.commit()
    result = {"message": f"Imported {added} teachers (updated {updated})", "added": added, "updated": updated, "skipped": skipped}
    if errors:
        result["errors"] = errors[:10]  # Limit error messages
    return result


async def _import_rooms(reader: csv.DictReader, db: Session) -> dict:
    """Import rooms from CSV"""
    added = 0
    updated = 0
    skipped = 0
    errors = []
    
    # Check headers
    headers = set(reader.fieldnames)
    if not any(h in headers for h in ['name', 'room_name']):
         return {
             "message": f"Missing required column: 'name'. Found headers: {list(headers)}", 
             "errors": [f"CSV must have a 'name' column. Found: {list(headers)}"], 
             "added": 0
         }

    for idx, row in enumerate(reader, start=2):
        name = (row.get('name') or row.get('room_name') or '').strip()
        capacity = parse_int(row.get('capacity'), 30)
        room_type = (row.get('type') or row.get('room_type') or 'LectureHall').strip()
        resources_str = (row.get('resources') or '').strip()
        
        # Parse resources (semicolon or comma separated)
        if resources_str:
            if ';' in resources_str:
                resources = [r.strip() for r in resources_str.split(';') if r.strip()]
            else:
                resources = [r.strip() for r in resources_str.split(',') if r.strip()]
        else:
            resources = []

        if not name:
            errors.append(f"Row {idx}: Missing room name")
            skipped += 1
            continue

        # UPSERT: Check duplicate by name
        existing = db.query(models.Room).filter(models.Room.name == name).first()
        if existing:
            existing.capacity = capacity
            existing.type = room_type
            existing.resources = resources
            updated += 1
        else:
            room = models.Room(name=name, capacity=capacity, type=room_type, resources=resources)
            db.add(room)
            added += 1

    db.commit()
    result = {"message": f"Imported {added} rooms (updated {updated})", "added": added, "updated": updated, "skipped": skipped}
    if errors:
        result["errors"] = errors[:10]
    return result


async def _import_subjects(reader: csv.DictReader, db: Session) -> dict:
    """Import subjects from CSV"""
    added = 0
    updated = 0
    skipped = 0
    errors = []
    
    # Check headers
    headers = set(reader.fieldnames)
    if not any(h in headers for h in ['name', 'subject_name']):
         return {
             "message": f"Missing required column: 'name'. Found headers: {list(headers)}", 
             "errors": [f"CSV must have a 'name' column. Found: {list(headers)}"], 
             "added": 0
         }

    # Build teacher lookup by email
    teachers = {t.email.lower(): t.id for t in db.query(models.Teacher).all()}
    
    for idx, row in enumerate(reader, start=2):
        name = (row.get('name') or row.get('subject_name') or '').strip()
        code = (row.get('code') or row.get('subject_code') or row.get('subject_id') or row.get('id') or '').strip()
        is_lab = parse_bool(row.get('is_lab') or row.get('lab') or row.get('has_lab'))
        credits = parse_int(row.get('credits'), 3)
        required_room_type = (row.get('required_room_type') or row.get('room_type') or 'LectureHall').strip()
        duration_slots = parse_int(row.get('duration_slots') or row.get('duration'), 1)
        
        # Teacher can be specified by email or ID
        teacher_email = (row.get('teacher_email') or row.get('teacher') or '').strip().lower()
        teacher_id_str = row.get('teacher_id') or ''
        
        teacher_id = None
        if teacher_id_str:
            teacher_id = parse_int(teacher_id_str, None)
        elif teacher_email and teacher_email in teachers:
            teacher_id = teachers[teacher_email]

        if not name:
            errors.append(f"Row {idx}: Missing subject name")
            skipped += 1
            continue
            
        if not code:
           # Try to find code in other common headers or generate
           code = (row.get('subject_id') or row.get('id') or '').strip()
           if not code:
               # Generate code from name if still missing
               code = name.upper().replace(' ', '')[:10]

        # UPSERT: Check duplicate by code
        existing = db.query(models.Subject).filter(models.Subject.code == code).first()
        if existing:
            existing.name = name
            existing.is_lab = is_lab
            existing.credits = credits
            existing.required_room_type = required_room_type
            existing.duration_slots = duration_slots
            existing.teacher_id = teacher_id
            updated += 1
        else:
            subject = models.Subject(
                name=name,
                code=code,
                is_lab=is_lab,
                credits=credits,
                required_room_type=required_room_type,
                duration_slots=duration_slots,
                teacher_id=teacher_id
            )
            db.add(subject)
            added += 1

    db.commit()
    result = {"message": f"Imported {added} subjects (updated {updated})", "added": added, "updated": updated, "skipped": skipped}
    if errors:
        result["errors"] = errors[:10]
    return result


async def _import_classgroups(reader: csv.DictReader, db: Session) -> dict:
    """Import class groups from CSV"""
    added = 0
    updated = 0
    skipped = 0
    errors = []

    # Check headers
    headers = set(reader.fieldnames)
    if not any(h in headers for h in ['name', 'class_name', 'group_name']):
         return {
             "message": f"Missing required column: 'name'. Found headers: {list(headers)}", 
             "errors": [f"CSV must have a 'name' column. Found: {list(headers)}"], 
             "added": 0
         }
    
    for idx, row in enumerate(reader, start=2):
        name = (row.get('name') or row.get('class_name') or row.get('group_name') or '').strip()
        student_count = parse_int(row.get('student_count') or row.get('students') or row.get('count'), 30)

        if not name:
            errors.append(f"Row {idx}: Missing class group name")
            skipped += 1
            continue

        # UPSERT: Check duplicate by name
        existing = db.query(models.ClassGroup).filter(models.ClassGroup.name == name).first()
        if existing:
            existing.student_count = student_count
            updated += 1
        else:
            group = models.ClassGroup(name=name, student_count=student_count)
            db.add(group)
            added += 1

    db.commit()
    result = {"message": f"Imported {added} class groups (updated {updated})", "added": added, "updated": updated, "skipped": skipped}
    if errors:
        result["errors"] = errors[:10]
    return result


@router.delete("/clear/{dataset}")
async def clear_dataset(dataset: str, db: Session = Depends(get_db)):
    """
    Clear all records of a specific dataset type.
    WARNING: This will delete all records! Use with caution.
    """
    try:
        if dataset == 'teachers':
            # First clear subjects that reference teachers
            db.query(models.Subject).update({models.Subject.teacher_id: None})
            count = db.query(models.Teacher).delete()
            db.commit()
            return {"message": f"Deleted {count} teachers"}
        
        elif dataset == 'rooms':
            count = db.query(models.Room).delete()
            db.commit()
            return {"message": f"Deleted {count} rooms"}
        
        elif dataset == 'subjects':
            count = db.query(models.Subject).delete()
            db.commit()
            return {"message": f"Deleted {count} subjects"}
        
        elif dataset == 'classgroups' or dataset == 'class_groups':
            count = db.query(models.ClassGroup).delete()
            db.commit()
            return {"message": f"Deleted {count} class groups"}
        
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported dataset type: {dataset}")
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
