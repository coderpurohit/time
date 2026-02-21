import sys
sys.path.insert(0, 'backend')

from app.infrastructure.database import SessionLocal
from app.infrastructure.models import Teacher, Lesson, Subject, ClassGroup

db = SessionLocal()

print("=== CREATING LESSONS FOR ALL SECTIONS ===")

# Get all data
teachers = db.query(Teacher).all()
subjects = db.query(Subject).all()
groups = db.query(ClassGroup).all()

print(f"\nAvailable:")
print(f"  Teachers: {len(teachers)}")
print(f"  Subjects: {len(subjects)}")
print(f"  Class Groups: {len(groups)}")

# Get existing lessons
existing_lessons = db.query(Lesson).all()
print(f"  Existing Lessons: {len(existing_lessons)}")

# Create lessons for all groups
print(f"\n=== CREATING LESSONS ===")
lessons_created = 0

for group in groups:
    # Check if this group already has lessons
    group_has_lessons = any(group in lesson.class_groups for lesson in existing_lessons)
    
    if group_has_lessons:
        print(f"⏭️  {group.name} - already has lessons")
        continue
    
    print(f"📚 Creating lessons for {group.name}...")
    
    # Assign each subject to this group with rotating teachers
    for i, subject in enumerate(subjects):
        teacher_idx = i % len(teachers)
        teacher = teachers[teacher_idx]
        
        # Determine periods based on subject type
        if 'Lab' in subject.name:
            periods = 4
        elif 'Project' in subject.name:
            periods = 2
        else:
            periods = 3
        
        lesson = Lesson(
            lessons_per_week=periods,
            length_per_lesson=1
        )
        lesson.teachers.append(teacher)
        lesson.subjects.append(subject)
        lesson.class_groups.append(group)
        
        db.add(lesson)
        lessons_created += 1

if lessons_created > 0:
    db.commit()
    print(f"\n✅ Created {lessons_created} new lessons")
else:
    print(f"\n✅ All groups already have lessons")

# Verify
all_lessons = db.query(Lesson).all()
print(f"\n=== VERIFICATION ===")
print(f"Total lessons: {len(all_lessons)}")

# Count lessons per group
print(f"\nLessons per class group:")
for group in sorted(groups, key=lambda x: x.name):
    group_lessons = [l for l in all_lessons if group in l.class_groups]
    total_periods = sum(l.lessons_per_week for l in group_lessons)
    print(f"  {group.name}: {len(group_lessons)} lessons ({total_periods} periods/week)")

# Count lessons per teacher
print(f"\nLessons per teacher:")
for teacher in sorted(teachers, key=lambda x: x.name):
    teacher_lessons = [l for l in all_lessons if teacher in l.teachers]
    total_periods = sum(l.lessons_per_week for l in teacher_lessons)
    print(f"  {teacher.name}: {len(teacher_lessons)} lessons ({total_periods} periods/week)")

db.close()

print("\n" + "="*60)
print("✅ LESSONS CREATED FOR ALL SECTIONS!")
print("="*60)
print("\nNEXT STEP:")
print("1. Open: http://localhost:8000/timetable_page.html")
print("2. Click 'Generate New Schedule'")
print("3. Wait for generation to complete")
print("4. Click 'Load Latest Timetable'")
print("5. Check dropdown - you'll see all sections!")
