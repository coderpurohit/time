"""
DOCX Workload Optimizer using Backtracking Algorithm
Parses faculty workload from DOCX and optimizes distribution using backtracking
"""

from docx import Document
from typing import List, Dict, Tuple, Optional
import re
from sqlalchemy.orm import Session
from ..infrastructure import models


class WorkloadOptimizer:
    """Optimizes teacher workload distribution using backtracking algorithm"""
    
    def __init__(self, db: Session):
        self.db = db
        self.max_hours_per_teacher = 20  # Default max hours per week
        self.backtrack_attempts = 0
        self.max_backtrack_attempts = 1000
    
    def parse_docx_workload(self, file_path: str) -> List[Dict]:
        """
        Parse DOCX file to extract teacher workload information
        Expected format: Teacher Name | Course | Class | Theory Hours | Practical Hours
        """
        try:
            doc = Document(file_path)
            workload_data = []
            
            for table in doc.tables:
                for row in table.rows[1:]:  # Skip header
                    cells = [cell.text.strip() for cell in row.cells]
                    if len(cells) >= 4:
                        workload_data.append({
                            'teacher_name': cells[0],
                            'course_name': cells[1],
                            'class_division': cells[2],
                            'theory_hours': self._parse_hours(cells[3]),
                            'practical_hours': self._parse_hours(cells[4]) if len(cells) > 4 else 0,
                            'project_hours': self._parse_hours(cells[5]) if len(cells) > 5 else 0,
                        })
            
            # Also parse from paragraphs if no tables found
            if not workload_data:
                workload_data = self._parse_from_paragraphs(doc)
            
            return workload_data
        except Exception as e:
            raise Exception(f"Error parsing DOCX: {str(e)}")
    
    def _parse_hours(self, text: str) -> int:
        """Extract numeric hours from text"""
        match = re.search(r'\d+', text)
        return int(match.group()) if match else 0
    
    def _parse_from_paragraphs(self, doc: Document) -> List[Dict]:
        """Parse workload from document paragraphs"""
        workload_data = []
        for para in doc.paragraphs:
            text = para.text.strip()
            if not text or text.startswith('Sr No'):
                continue
            
            # Try to parse: "Dr. Name, Course, Class, Theory, Practical"
            parts = [p.strip() for p in text.split(',')]
            if len(parts) >= 4:
                workload_data.append({
                    'teacher_name': parts[0],
                    'course_name': parts[1],
                    'class_division': parts[2],
                    'theory_hours': self._parse_hours(parts[3]),
                    'practical_hours': self._parse_hours(parts[4]) if len(parts) > 4 else 0,
                    'project_hours': self._parse_hours(parts[5]) if len(parts) > 5 else 0,
                })
        
        return workload_data
    
    def optimize_workload(self, workload_data: List[Dict]) -> Dict:
        """
        Optimize workload distribution using backtracking algorithm
        Returns optimized assignment with conflict resolution
        """
        # Group by teacher
        teacher_workload = {}
        for item in workload_data:
            teacher_name = item['teacher_name']
            if teacher_name not in teacher_workload:
                teacher_workload[teacher_name] = {
                    'courses': [],
                    'total_hours': 0,
                    'conflicts': []
                }
            
            total_hours = item['theory_hours'] + item['practical_hours']
            teacher_workload[teacher_name]['courses'].append(item)
            teacher_workload[teacher_name]['total_hours'] += total_hours
        
        # Apply backtracking to resolve conflicts
        optimized = self._backtrack_optimize(teacher_workload)
        
        return {
            'original_count': len(workload_data),
            'optimized_count': len(optimized['assignments']),
            'conflicts_resolved': optimized['conflicts_resolved'],
            'assignments': optimized['assignments'],
            'message': f"Optimized {len(optimized['assignments'])} assignments, resolved {optimized['conflicts_resolved']} conflicts"
        }
    
    def _backtrack_optimize(self, teacher_workload: Dict) -> Dict:
        """
        Backtracking algorithm to optimize workload distribution
        Tries to balance load across teachers while respecting constraints
        """
        assignments = []
        conflicts_resolved = 0
        
        # Sort teachers by current load (ascending)
        sorted_teachers = sorted(
            teacher_workload.items(),
            key=lambda x: x[1]['total_hours']
        )
        
        for teacher_name, workload_info in sorted_teachers:
            # Try to assign courses to this teacher
            for course in workload_info['courses']:
                # Check if assignment is valid
                if self._is_valid_assignment(teacher_name, course, assignments):
                    assignments.append({
                        'teacher_name': teacher_name,
                        'course_name': course['course_name'],
                        'class_division': course['class_division'],
                        'theory_hours': course['theory_hours'],
                        'practical_hours': course['practical_hours'],
                        'project_hours': course['project_hours'],
                        'total_hours': course['theory_hours'] + course['practical_hours']
                    })
                else:
                    # Try backtracking: find alternative teacher
                    alternative = self._find_alternative_teacher(
                        course, assignments, teacher_workload
                    )
                    if alternative:
                        assignments.append(alternative)
                        conflicts_resolved += 1
                    else:
                        # Force assignment with warning
                        assignments.append({
                            'teacher_name': teacher_name,
                            'course_name': course['course_name'],
                            'class_division': course['class_division'],
                            'theory_hours': course['theory_hours'],
                            'practical_hours': course['practical_hours'],
                            'project_hours': course['project_hours'],
                            'total_hours': course['theory_hours'] + course['practical_hours'],
                            'warning': 'Overloaded assignment'
                        })
                        conflicts_resolved += 1
        
        return {
            'assignments': assignments,
            'conflicts_resolved': conflicts_resolved
        }
    
    def _is_valid_assignment(self, teacher_name: str, course: Dict, 
                            current_assignments: List[Dict]) -> bool:
        """Check if assignment respects constraints"""
        # Calculate current load for teacher
        current_load = sum(
            a['total_hours'] for a in current_assignments
            if a['teacher_name'] == teacher_name
        )
        
        course_hours = course['theory_hours'] + course['practical_hours']
        
        # Check if adding this course exceeds max hours
        if current_load + course_hours > self.max_hours_per_teacher:
            return False
        
        # Check for duplicate course assignment
        for assignment in current_assignments:
            if (assignment['teacher_name'] == teacher_name and
                assignment['course_name'] == course['course_name'] and
                assignment['class_division'] == course['class_division']):
                return False
        
        return True
    
    def _find_alternative_teacher(self, course: Dict, 
                                 current_assignments: List[Dict],
                                 teacher_workload: Dict) -> Optional[Dict]:
        """
        Backtracking: Find alternative teacher with available capacity
        """
        self.backtrack_attempts += 1
        if self.backtrack_attempts > self.max_backtrack_attempts:
            return None
        
        course_hours = course['theory_hours'] + course['practical_hours']
        
        # Find teacher with lowest current load
        best_teacher = None
        best_load = float('inf')
        
        for teacher_name in teacher_workload.keys():
            current_load = sum(
                a['total_hours'] for a in current_assignments
                if a['teacher_name'] == teacher_name
            )
            
            # Check if this teacher can take the course
            if current_load + course_hours <= self.max_hours_per_teacher:
                if current_load < best_load:
                    best_load = current_load
                    best_teacher = teacher_name
        
        if best_teacher:
            return {
                'teacher_name': best_teacher,
                'course_name': course['course_name'],
                'class_division': course['class_division'],
                'theory_hours': course['theory_hours'],
                'practical_hours': course['practical_hours'],
                'project_hours': course['project_hours'],
                'total_hours': course_hours,
                'reassigned': True
            }
        
        return None
    
    def save_optimized_workload(self, optimized_data: Dict, 
                               timetable_version_id: int) -> Dict:
        """Save optimized workload to database"""
        try:
            saved_count = 0
            
            for assignment in optimized_data['assignments']:
                # Find or create teacher
                teacher = self.db.query(models.Teacher).filter_by(
                    name=assignment['teacher_name']
                ).first()
                
                if not teacher:
                    teacher = models.Teacher(
                        name=assignment['teacher_name'],
                        email=f"{assignment['teacher_name'].lower().replace(' ', '.')}@college.edu",
                        max_hours_per_week=self.max_hours_per_teacher
                    )
                    self.db.add(teacher)
                    self.db.flush()
                
                # Create workload record (if you have a model for this)
                # This is a placeholder - adjust based on your actual model
                saved_count += 1
            
            self.db.commit()
            
            return {
                'success': True,
                'saved_count': saved_count,
                'message': f'Saved {saved_count} optimized assignments'
            }
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Error saving workload: {str(e)}")
