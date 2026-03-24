from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from typing import Optional, List, Dict, Any
import csv
import io
import re
from sqlalchemy.orm import Session
from sqlalchemy import text

from ...infrastructure.database import get_db
from ...infrastructure import models

router = APIRouter()

class EnhancedCSVParser:
    """Enhanced CSV parser for faculty workload data"""
    
    # Field mapping for flexible header recognition
    FIELD_MAPPINGS = {
        'name': ['faculty name', 'name', 'teacher name', 'faculty', 'teacher'],
        'email': ['email', 'email address', 'mail'],
        'designation': ['designation', 'position', 'rank', 'title'],
        'theory_hours': ['theory hours', 'theory', 'theory load', 'th'],
        'practical_hours': ['practical hours', 'practical', 'practical load', 'ph'],
        'project_hours': ['project hours', 'project', 'project load', 'proj'],
        'max_hours': ['max hours', 'max_hours_per_week', 'weekly hours', 'total hours']
    }
    
    def __init__(self, csv_content: str):
        self.csv_content = csv_content
        self.rows = []
        self.headers = []
        self.field_map = {}
        self.errors = []
        self.warnings = []
        
    def parse(self) -> Dict[str, Any]:
        """Parse CSV content and return structured data"""
        try:
            # Try different encodings and delimiters
            reader = csv.DictReader(io.StringIO(self.csv_content))
            self.headers = reader.fieldnames or []
            self.rows = [row for row in reader if any(row.values())]
            
            if not self.headers:
                raise ValueError("No headers found in CSV")
                
            if not self.rows:
                raise ValueError("No data rows found in CSV")
                
            # Map headers to our fields
            self._map_headers()
            
            # Parse and validate rows
            parsed_teachers = []
            for i, row in enumerate(self.rows, 1):
                try:
                    teacher_data = self._parse_teacher_row(row, i)
                    if teacher_data:
                        parsed_teachers.append(teacher_data)
                except Exception as e:
                    self.errors.append(f"Row {i}: {str(e)}")
                    
            return {
                'teachers': parsed_teachers,
                'total_rows': len(self.rows),
                'parsed_count': len(parsed_teachers),
                'errors': self.errors,
                'warnings': self.warnings,
                'field_mapping': self.field_map
            }
            
        except Exception as e:
            raise ValueError(f"CSV parsing failed: {str(e)}")
    
    def _map_headers(self):
        """Map CSV headers to our field names"""
        self.field_map = {}
        
        for header in self.headers:
            header_lower = header.lower().strip()
            
            # Find matching field
            for field, variations in self.FIELD_MAPPINGS.items():
                if any(var in header_lower for var in variations):
                    self.field_map[field] = header
                    break
        
        # Check for required fields
        if 'name' not in self.field_map:
            # Try to find name field by position or common patterns
            for header in self.headers:
                if any(word in header.lower() for word in ['name', 'faculty', 'teacher']):
                    self.field_map['name'] = header
                    break
            
            if 'name' not in self.field_map:
                raise ValueError("Could not find faculty name column")
    
    def _parse_teacher_row(self, row: Dict[str, str], row_num: int) -> Optional[Dict[str, Any]]:
        """Parse a single teacher row"""
        # Clean row data
        clean_row = {k: (v or '').strip() for k, v in row.items()}
        
        # Extract name (required)
        name = clean_row.get(self.field_map.get('name', ''), '').strip()
        if not name or name.lower() in ['', 'na', 'n/a', 'null']:
            self.warnings.append(f"Row {row_num}: Skipping row with empty name")
            return None
        
        # Clean name
        name = re.sub(r'\s+', ' ', name).strip()
        
        # Extract or generate email
        email = clean_row.get(self.field_map.get('email', ''), '').strip()
        if not email:
            email = self._generate_email(name)
            self.warnings.append(f"Row {row_num}: Generated email for {name}")
        
        # Extract designation
        designation = clean_row.get(self.field_map.get('designation', ''), '').strip()
        
        # Extract hours and calculate total
        theory_hours = self._parse_hours(clean_row.get(self.field_map.get('theory_hours', ''), '0'))
        practical_hours = self._parse_hours(clean_row.get(self.field_map.get('practical_hours', ''), '0'))
        project_hours = self._parse_hours(clean_row.get(self.field_map.get('project_hours', ''), '0'))
        
        # Calculate max hours
        calculated_hours = theory_hours + practical_hours + project_hours
        max_hours_field = clean_row.get(self.field_map.get('max_hours', ''), '')
        
        if max_hours_field:
            max_hours = self._parse_hours(max_hours_field)
        else:
            max_hours = max(calculated_hours, 18) if calculated_hours > 0 else 22
        
        return {
            'name': name,
            'email': email,
            'designation': designation,
            'max_hours_per_week': max_hours,
            'theory_hours': theory_hours,
            'practical_hours': practical_hours,
            'project_hours': project_hours,
            'calculated_hours': calculated_hours
        }
    
    def _parse_hours(self, hours_str: str) -> int:
        """Parse hours from string, handling various formats"""
        if not hours_str:
            return 0
            
        # Extract numbers from string
        numbers = re.findall(r'\d+', str(hours_str))
        if numbers:
            return int(numbers[0])
        return 0
    
    def _generate_email(self, name: str) -> str:
        """Generate email from faculty name"""
        # Remove titles and clean name
        clean_name = re.sub(r'\b(dr|prof|mr|mrs|ms)\.?\s*', '', name.lower())
        clean_name = re.sub(r'[^\w\s]', '', clean_name)
        
        # Take first and last name
        parts = clean_name.split()
        if len(parts) >= 2:
            email = f"{parts[0]}.{parts[-1]}@dypatil.edu"
        else:
            email = f"{clean_name.replace(' ', '.')}@dypatil.edu"
        
        return email

@router.post("/enhanced")
async def import_enhanced_csv(
    dataset: str = Form(...), 
    file: UploadFile = File(...), 
    force_clear_existing: str = Form("false"),
    db: Session = Depends(get_db)
):
    """Enhanced CSV import with robust parsing and error handling"""
    
    # Validate file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
        
    if not file.filename.lower().endswith(('.csv', '.txt')):
        raise HTTPException(status_code=400, detail="Only CSV/TXT files are supported")

    # Read file with multiple encoding attempts
    content = None
    encodings = ['utf-8-sig', 'utf-8', 'latin1', 'cp1252']
    
    for encoding in encodings:
        try:
            file_content = await file.read()
            content = file_content.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Cannot read file: {str(e)}")
    
    if content is None:
        raise HTTPException(status_code=400, detail="Cannot decode file - unsupported encoding")

    # Parse CSV
    try:
        parser = EnhancedCSVParser(content)
        result = parser.parse()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Parsing error: {str(e)}")

    # Validate dataset type
    if dataset != 'teachers':
        raise HTTPException(status_code=400, detail="Only 'teachers' dataset is supported")

    # Parse clear flag
    should_clear = force_clear_existing.lower() == 'true'
    
    try:
        # Clear existing data if requested
        if should_clear:
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
        added_count = 0
        updated_count = 0
        skipped_count = 0
        
        for teacher_data in result['teachers']:
            try:
                # Check if teacher exists
                existing = db.query(models.Teacher).filter(
                    models.Teacher.email == teacher_data['email']
                ).first()
                
                if existing:
                    # Update existing teacher
                    existing.name = teacher_data['name']
                    existing.max_hours_per_week = teacher_data['max_hours_per_week']
                    updated_count += 1
                else:
                    # Create new teacher
                    teacher = models.Teacher(
                        name=teacher_data['name'],
                        email=teacher_data['email'],
                        max_hours_per_week=teacher_data['max_hours_per_week']
                    )
                    db.add(teacher)
                    added_count += 1
                    
            except Exception as e:
                skipped_count += 1
                result['errors'].append(f"Failed to save teacher {teacher_data['name']}: {str(e)}")
        
        db.commit()
        
        # Prepare response
        response = {
            "success": True,
            "message": f"Import completed: {added_count} added, {updated_count} updated, {skipped_count} skipped",
            "statistics": {
                "total_rows_processed": result['total_rows'],
                "teachers_parsed": result['parsed_count'],
                "teachers_added": added_count,
                "teachers_updated": updated_count,
                "teachers_skipped": skipped_count,
                "errors_count": len(result['errors']),
                "warnings_count": len(result['warnings'])
            },
            "field_mapping": result['field_mapping'],
            "errors": result['errors'][:10],  # Limit errors in response
            "warnings": result['warnings'][:10]  # Limit warnings in response
        }
        
        if result['errors']:
            response["message"] += f" ({len(result['errors'])} errors occurred)"
        
        return response
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")