"""
Comprehensive DOCX importer that extracts and creates:
- Teachers
- Subjects
- Classes
- Rooms
- Lessons
- Load Factor
"""
from docx import Document
import io
from typing import List, Dict, Tuple
from sqlalchemy.orm import Session
from ...infrastructure import models


class FullDocxImporter:
    def __init__(self, db: Session):
        self.db = db

    def import_from_docx(self, file_content: bytes) -> Dict:
        """Parse DOCX and extract all entities"""
        doc = Document(io.BytesIO(file_content))
        
        # Extract data from tables
        teachers_set = set()
        subjects_set = set()
        classes_set = set()
        rooms_set = set()
        lessons_list = []
        
        # Parse all tables in document
        for table in doc.tables:
            rows = table.rows
            if len(rows) < 2:
                continue
            
            # Try to identify table type by headers
            header_text = ' '.join([cell.text.lower() for cell in rows[0].cells[:3]])
            
            # Parse data rows
            for row_idx in range(1, len(rows)):
                row = rows[row_idx]
                cells = [cell.text.strip() for cell in row.cells]
                
                if len(cells) < 3:
                    continue
                
                # Extract teacher name (usually first column)
                teacher_name = cells[0]
                if teacher_name and teacher_name not in ['', '-', 'N/A']:
                    # Clean up teacher name (remove designation, extra spaces)
                    teacher_name = self._clean_name(teacher_name)
                    if teacher_name:
                        teachers_set.add(teacher_name)
                
                # Extract subject (usually second column)
                subject_name = cells[1] if len(cells) > 1 else ''
                if subject_name and subject_name not in ['', '-', 'N/A']:
                    subject_name = self._clean_name(subject_name)
                    if subject_name:
                        subjects_set.add(subject_name)
                
                # Extract class (usually third column or contains class info)
                class_name = cells[2] if len(cells) > 2 else ''
                if class_name and class_name not in ['', '-', 'N/A']:
                    class_name = self._clean_class_name(class_name)
                    if class_name:
                        classes_set.add(class_name)
                
                # Extract room if available
                room_name = cells[3] if len(cells) > 3 else 'Room-1'
                if room_name and room_name not in ['', '-', 'N/A']:
                    room_name = self._clean_name(room_name)
                    if room_name:
                        rooms_set.add(room_name)
                
                # Create lesson entry
                if teacher_name and subject_name and class_name:
                    lessons_list.append({
                        'teacher': teacher_name,
                        'subject': subject_name,
                        'class': class_name,
                        'room': room_name or 'Room-1',
                        'periods': 1
                    })
        
        # Create entities in database
        result = {
            'teachers_created': 0,
            'subjects_created': 0,
            'classes_created': 0,
            'rooms_created': 0,
            'lessons_created': 0,
            'errors': []
        }
        
        try:
            # Create teachers
            teacher_map = {}
            for teacher_name in teachers_set:
                try:
                    existing = self.db.query(models.Teacher).filter(
                        models.Teacher.name.ilike(teacher_name)
                    ).first()
                    
                    if not existing:
                        teacher = models.Teacher(
                            name=teacher_name,
                            email=f"{teacher_name.lower().replace(' ', '.')}@college.edu",
                            max_hours_per_week=18
                        )
                        self.db.add(teacher)
                        self.db.flush()
                        teacher_map[teacher_name] = teacher
                        result['teachers_created'] += 1
                    else:
                        teacher_map[teacher_name] = existing
                except Exception as e:
                    result['errors'].append(f"Teacher {teacher_name}: {str(e)}")
            
            # Create subjects
            subject_map = {}
            for subject_name in subjects_set:
                try:
                    existing = self.db.query(models.Subject).filter(
                        models.Subject.name.ilike(subject_name)
                    ).first()
                    
                    if not existing:
                        subject = models.Subject(
                            name=subject_name,
                            code=self._generate_code(subject_name),
                            credits=3,
                            is_lab=False
                        )
                        self.db.add(subject)
                        self.db.flush()
                        subject_map[subject_name] = subject
                        result['subjects_created'] += 1
                    else:
                        subject_map[subject_name] = existing
                except Exception as e:
                    result['errors'].append(f"Subject {subject_name}: {str(e)}")
            
            # Create classes
            class_map = {}
            for class_name in classes_set:
                try:
                    existing = self.db.query(models.ClassGroup).filter(
                        models.ClassGroup.name.ilike(class_name)
                    ).first()
                    
                    if not existing:
                        class_group = models.ClassGroup(
                            name=class_name,
                            student_count=60
                        )
                        self.db.add(class_group)
                        self.db.flush()
                        class_map[class_name] = class_group
                        result['classes_created'] += 1
                    else:
                        class_map[class_name] = existing
                except Exception as e:
                    result['errors'].append(f"Class {class_name}: {str(e)}")
            
            # Create rooms
            room_map = {}
            for room_name in rooms_set:
                try:
                    existing = self.db.query(models.Room).filter(
                        models.Room.name.ilike(room_name)
                    ).first()
                    
                    if not existing:
                        room = models.Room(
                            name=room_name,
                            capacity=60,
                            room_type='LectureHall'
                        )
                        self.db.add(room)
                        self.db.flush()
                        room_map[room_name] = room
                        result['rooms_created'] += 1
                    else:
                        room_map[room_name] = existing
                except Exception as e:
                    result['errors'].append(f"Room {room_name}: {str(e)}")
            
            # Create lessons
            for lesson_data in lessons_list:
                try:
                    teacher = teacher_map.get(lesson_data['teacher'])
                    subject = subject_map.get(lesson_data['subject'])
                    class_group = class_map.get(lesson_data['class'])
                    
                    if teacher and subject and class_group:
                        # Check if lesson already exists
                        existing = self.db.query(models.Lesson).filter(
                            models.Lesson.teachers.any(models.Teacher.id == teacher.id),
                            models.Lesson.subjects.any(models.Subject.id == subject.id),
                            models.Lesson.class_groups.any(models.ClassGroup.id == class_group.id)
                        ).first()
                        
                        if not existing:
                            lesson = models.Lesson(
                                lessons_per_week=lesson_data.get('periods', 1),
                                length_per_lesson=1,
                                teachers=[teacher],
                                subjects=[subject],
                                class_groups=[class_group]
                            )
                            self.db.add(lesson)
                            self.db.flush()
                            result['lessons_created'] += 1
                except Exception as e:
                    result['errors'].append(f"Lesson {lesson_data}: {str(e)}")
            
            # Commit all changes
            self.db.commit()
            result['status'] = 'success'
            
        except Exception as e:
            self.db.rollback()
            result['status'] = 'error'
            result['errors'].append(f"Database error: {str(e)}")
        
        return result

    def _clean_name(self, name: str) -> str:
        """Clean up name by removing extra spaces, designations, etc."""
        if not name:
            return ''
        
        # Remove common designations
        designations = ['Dr.', 'Prof.', 'Mr.', 'Mrs.', 'Ms.', 'Associate Professor', 
                       'Assistant Professor', 'Professor', 'Lecturer', '-', 'N/A']
        
        name = name.strip()
        for desig in designations:
            name = name.replace(desig, '').strip()
        
        # Remove extra spaces and newlines
        name = ' '.join(name.split())
        
        return name if name and len(name) > 2 else ''

    def _clean_class_name(self, name: str) -> str:
        """Clean up class name"""
        if not name:
            return ''
        
        name = name.strip().upper()
        # Keep only alphanumeric and hyphens
        name = ''.join(c for c in name if c.isalnum() or c in ['-', '_'])
        
        return name if name else ''

    def _generate_code(self, name: str) -> str:
        """Generate unique subject code"""
        code = ''.join(c for c in name.upper() if c.isalnum())[:10]
        
        # Ensure uniqueness
        existing = self.db.query(models.Subject).filter(
            models.Subject.code == code
        ).first()
        
        if existing:
            suffix = 1
            while self.db.query(models.Subject).filter(
                models.Subject.code == f"{code}{suffix}"
            ).first():
                suffix += 1
            code = f"{code}{suffix}"
        
        return code
