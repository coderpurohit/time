"""
Comprehensive DOCX importer that extracts teachers, classes, rooms, subjects, and lessons
"""
from docx import Document
from typing import Dict, List, Tuple
import re
from sqlalchemy.orm import Session
from backend.app.infrastructure.models import (
    Teacher, Subject, Room, ClassGroup, Lesson, TimeSlot
)


class ComprehensiveDocxImporter:
    def __init__(self, db: Session):
        self.db = db
        self.extracted_data = {
            'teachers': [],
            'classes': [],
            'rooms': [],
            'subjects': [],
            'lessons': []
        }

    def import_from_docx(self, file_path: str) -> Dict:
        """Main import function - extracts all data from DOCX"""
        try:
            doc = Document(file_path)
            
            # Extract all data from document
            self._extract_from_tables(doc)
            self._extract_from_paragraphs(doc)
            
            # Save to database
            results = self._save_to_database()
            
            return {
                'success': True,
                'message': 'DOCX imported successfully',
                'extracted': self.extracted_data,
                'saved': results
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error importing DOCX: {str(e)}',
                'error': str(e)
            }

    def _extract_from_tables(self, doc: Document):
        """Extract data from all tables in the document"""
        for table in doc.tables:
            self._process_table(table)

    def _process_table(self, table):
        """Process a single table to extract relevant data"""
        if len(table.rows) < 2:
            return

        # Get header row
        headers = [cell.text.strip().lower() for cell in table.rows[0].cells]
        
        # Detect table type and process accordingly
        if self._is_teacher_table(headers):
            self._extract_teachers_from_table(table, headers)
        elif self._is_class_table(headers):
            self._extract_classes_from_table(table, headers)
        elif self._is_room_table(headers):
            self._extract_rooms_from_table(table, headers)
        elif self._is_subject_table(headers):
            self._extract_subjects_from_table(table, headers)
        elif self._is_lesson_table(headers):
            self._extract_lessons_from_table(table, headers)

    def _is_teacher_table(self, headers: List[str]) -> bool:
        """Check if table contains teacher data"""
        keywords = ['teacher', 'faculty', 'instructor', 'name', 'email', 'designation']
        return any(kw in ' '.join(headers) for kw in keywords)

    def _is_class_table(self, headers: List[str]) -> bool:
        """Check if table contains class data"""
        keywords = ['class', 'division', 'section', 'grade', 'student']
        return any(kw in ' '.join(headers) for kw in keywords)

    def _is_room_table(self, headers: List[str]) -> bool:
        """Check if table contains room data"""
        keywords = ['room', 'lab', 'hall', 'capacity', 'building']
        return any(kw in ' '.join(headers) for kw in keywords)

    def _is_subject_table(self, headers: List[str]) -> bool:
        """Check if table contains subject data"""
        keywords = ['subject', 'course', 'code', 'credits', 'theory', 'practical']
        return any(kw in ' '.join(headers) for kw in keywords)

    def _is_lesson_table(self, headers: List[str]) -> bool:
        """Check if table contains lesson/timetable data"""
        keywords = ['lesson', 'timetable', 'schedule', 'period', 'slot', 'monday', 'tuesday']
        return any(kw in ' '.join(headers) for kw in keywords)

    def _extract_teachers_from_table(self, table, headers: List[str]):
        """Extract teacher information from table"""
        for row in table.rows[1:]:
            cells = [cell.text.strip() for cell in row.cells]
            if not cells[0]:  # Skip empty rows
                continue

            teacher_data = {
                'name': cells[0] if len(cells) > 0 else 'Unknown',
                'email': cells[1] if len(cells) > 1 else '',
                'designation': cells[2] if len(cells) > 2 else '',
                'max_hours_per_week': 20
            }
            
            if teacher_data['name'] and teacher_data['name'] != 'Unknown':
                self.extracted_data['teachers'].append(teacher_data)

    def _extract_classes_from_table(self, table, headers: List[str]):
        """Extract class information from table"""
        for row in table.rows[1:]:
            cells = [cell.text.strip() for cell in row.cells]
            if not cells[0]:
                continue

            class_data = {
                'name': cells[0],
                'student_count': self._parse_number(cells[1]) if len(cells) > 1 else 30
            }
            
            if class_data['name']:
                self.extracted_data['classes'].append(class_data)

    def _extract_rooms_from_table(self, table, headers: List[str]):
        """Extract room information from table"""
        for row in table.rows[1:]:
            cells = [cell.text.strip() for cell in row.cells]
            if not cells[0]:
                continue

            room_data = {
                'name': cells[0],
                'room_type': cells[1] if len(cells) > 1 else 'LectureHall',
                'capacity': self._parse_number(cells[2]) if len(cells) > 2 else 50,
                'resources': cells[3] if len(cells) > 3 else ''
            }
            
            if room_data['name']:
                self.extracted_data['rooms'].append(room_data)

    def _extract_subjects_from_table(self, table, headers: List[str]):
        """Extract subject information from table"""
        for row in table.rows[1:]:
            cells = [cell.text.strip() for cell in row.cells]
            if not cells[0]:
                continue

            is_lab = 'lab' in cells[1].lower() if len(cells) > 1 else False
            subject_data = {
                'code': cells[0],
                'name': cells[1] if len(cells) > 1 else cells[0],
                'credits': self._parse_number(cells[2]) if len(cells) > 2 else 3,
                'is_lab': is_lab,
                'duration_slots': self._parse_number(cells[3]) if len(cells) > 3 else 1,
                'room_type': 'Lab' if is_lab else 'LectureHall'
            }
            
            if subject_data['code']:
                self.extracted_data['subjects'].append(subject_data)

    def _extract_lessons_from_table(self, table, headers: List[str]):
        """Extract lesson/timetable information from table"""
        # This would extract timetable entries if present
        pass

    def _extract_from_paragraphs(self, doc: Document):
        """Extract data from paragraphs if not in tables"""
        text = '\n'.join([p.text for p in doc.paragraphs])
        
        # Try to extract teacher names from text
        self._extract_teachers_from_text(text)
        self._extract_classes_from_text(text)

    def _extract_teachers_from_text(self, text: str):
        """Extract teacher names from paragraph text"""
        # Look for patterns like "Teacher: Name" or "Faculty: Name"
        patterns = [
            r'(?:Teacher|Faculty|Instructor):\s*([A-Za-z\s]+)',
            r'(?:Dr\.|Prof\.|Mr\.|Ms\.|Mrs\.)\s+([A-Za-z\s]+)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                name = match.strip()
                if name and len(name) > 2:
                    # Check if not already extracted
                    if not any(t['name'].lower() == name.lower() for t in self.extracted_data['teachers']):
                        self.extracted_data['teachers'].append({
                            'name': name,
                            'email': '',
                            'designation': '',
                            'max_hours_per_week': 20
                        })

    def _extract_classes_from_text(self, text: str):
        """Extract class names from text"""
        # Look for patterns like "SE-AIDS-A", "TE-AIDS-B", etc.
        pattern = r'([A-Z]{2})-([A-Z]+)-([A-Z])'
        matches = re.findall(pattern, text)
        
        for match in matches:
            class_name = f"{match[0]}-{match[1]}-{match[2]}"
            if not any(c['name'] == class_name for c in self.extracted_data['classes']):
                self.extracted_data['classes'].append({
                    'name': class_name,
                    'student_count': 30
                })

    def _parse_number(self, text: str) -> int:
        """Extract number from text"""
        match = re.search(r'\d+', text)
        return int(match.group()) if match else 0

    def _save_to_database(self) -> Dict:
        """Save extracted data to database"""
        results = {
            'teachers_added': 0,
            'classes_added': 0,
            'rooms_added': 0,
            'subjects_added': 0,
            'lessons_added': 0
        }

        try:
            # Save teachers
            for teacher_data in self.extracted_data['teachers']:
                existing = self.db.query(Teacher).filter_by(name=teacher_data['name']).first()
                if not existing:
                    teacher = Teacher(
                        name=teacher_data['name'],
                        email=teacher_data.get('email', ''),
                        max_hours_per_week=teacher_data.get('max_hours_per_week', 20)
                    )
                    self.db.add(teacher)
                    results['teachers_added'] += 1

            # Save classes
            for class_data in self.extracted_data['classes']:
                existing = self.db.query(ClassGroup).filter_by(name=class_data['name']).first()
                if not existing:
                    class_group = ClassGroup(
                        name=class_data['name'],
                        student_count=class_data.get('student_count', 30)
                    )
                    self.db.add(class_group)
                    results['classes_added'] += 1

            # Save rooms
            for room_data in self.extracted_data['rooms']:
                existing = self.db.query(Room).filter_by(name=room_data['name']).first()
                if not existing:
                    room = Room(
                        name=room_data['name'],
                        room_type=room_data.get('room_type', 'LectureHall'),
                        capacity=room_data.get('capacity', 50),
                        resources=room_data.get('resources', '')
                    )
                    self.db.add(room)
                    results['rooms_added'] += 1

            # Save subjects
            for subject_data in self.extracted_data['subjects']:
                existing = self.db.query(Subject).filter_by(code=subject_data['code']).first()
                if not existing:
                    subject = Subject(
                        code=subject_data['code'],
                        name=subject_data.get('name', subject_data['code']),
                        credits=subject_data.get('credits', 3),
                        is_lab=subject_data.get('is_lab', False),
                        duration_slots=subject_data.get('duration_slots', 1),
                        room_type=subject_data.get('room_type', 'LectureHall')
                    )
                    self.db.add(subject)
                    results['subjects_added'] += 1

            self.db.commit()
            return results

        except Exception as e:
            self.db.rollback()
            raise e
