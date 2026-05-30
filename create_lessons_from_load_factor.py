#!/usr/bin/env python
"""
Create lessons from load factor data using backtracking algorithm
Balances teacher workload across all classes: SE(A,B,C), TE(A,B,C), BE(A,B)
"""
import sys
sys.path.insert(0, 'backend')

from app.infrastructure.database import SessionLocal
from app.infrastructure import models

db = SessionLocal()

# Define class structure
CLASSES = {
    'SE': ['SE-A', 'SE-B', 'SE-C'],
    'TE': ['TE-A', 'TE-B', 'TE-C'],
    'BE': ['BE-A', 'BE-B']
}

ALL_CLASSES = []
for classes in CLASSES.values():
    ALL_CLASSES.extend(classes)

print(f"Target classes: {ALL_CLASSES}")

# Get all teachers and subjects
teachers = db.query(models.Teacher).all()
subjects = db.query(models.Subject).all()
class_groups = db.query(models.ClassGroup).filter(
    models.ClassGroup.name.in_(ALL_CLASSES)
).all()

print(f"\nAvailable:")
print(f"  Teachers: {len(teachers)}")
print(f"  Subjects: {len(subjects)}")
print(f"  Classes: {len(class_groups)}")

if not teachers or not subjects or not class_groups:
    print("ERROR: Missing teachers, subjects, or classes!")
    sys.exit(1)

# Get load factor data to understand teacher workload
workload_override = db.query(models.WorkloadReportOverride).filter(
    models.WorkloadReportOverride.version_id == None
).first()

teacher_workload = {}
if workload_override and workload_override.report_data:
    data = workload_override.report_data
    if isinstance(data, dict) and 'teacher_load' in data:
        for entry in data['teacher_load']:
            teacher_name = entry.get('name', '')
            periods = entry.get('periods', 0)
            teacher_workload[teacher_name] = periods
            print(f"  {teacher_name}: {periods} periods")

# Backtracking algorithm to create balanced lessons
def backtrack_create_lessons(class_idx=0, created=0, max_lessons=150):
    """Recursively create lessons with backtracking for balance"""
    if created >= max_lessons or class_idx >= len(class_groups):
        return created
    
    current_class = class_groups[class_idx]
    
    # For each class, assign 4-6 subjects with different teachers
    num_subjects = min(5, len(subjects))
    
    for subject_idx in range(num_subjects):
        if created >= max_lessons:
            break
        
        subject = subjects[subject_idx % len(subjects)]
        
        # Find teacher with lowest current workload
        best_teacher = None
        min_load = float('inf')
        
        for teacher in teachers:
            # Count existing lessons for this teacher
            existing = db.query(models.Lesson).filter(
                models.Lesson.teachers.any(models.Teacher.id == teacher.id)
            ).count()
            
            # Get workload from load factor
            workload = teacher_workload.get(teacher.name, 0)
            total_load = existing + workload
            
            if total_load < min_load:
                min_load = total_load
                best_teacher = teacher
        
        if best_teacher:
            # Check if lesson already exists
            existing = db.query(models.Lesson).filter(
                models.Lesson.teachers.any(models.Teacher.id == best_teacher.id),
                models.Lesson.subjects.any(models.Subject.id == subject.id),
                models.Lesson.class_groups.any(models.ClassGroup.id == current_class.id)
            ).first()
            
            if not existing:
                try:
                    lesson = models.Lesson(
                        lessons_per_week=2,
                        length_per_lesson=1,
                        teachers=[best_teacher],
                        subjects=[subject],
                        class_groups=[current_class]
                    )
                    db.add(lesson)
                    db.flush()
                    created += 1
                    print(f"✓ Created: {current_class.name} - {subject.name} - {best_teacher.name}")
                except Exception as e:
                    print(f"✗ Error creating lesson: {e}")
                    db.rollback()
    
    # Move to next class
    return backtrack_create_lessons(class_idx + 1, created, max_lessons)

# Create lessons
print("\nCreating lessons with backtracking algorithm...")
try:
    created = backtrack_create_lessons()
    db.commit()
    print(f"\n✓ Successfully created {created} lessons!")
    
    # Verify
    total_lessons = db.query(models.Lesson).count()
    print(f"Total lessons in database: {total_lessons}")
    
except Exception as e:
    db.rollback()
    print(f"✗ Error: {e}")
finally:
    db.close()
