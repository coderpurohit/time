import sys
sys.path.insert(0, 'backend')

from app.infrastructure.database import SessionLocal
from app.infrastructure.models import Teacher, Lesson, Subject, ClassGroup

db = SessionLocal()

print("=== ADDING NEW TEACHERS WITH LESSONS ===")

# Check if they already exist
existing_bharat = db.query(Teacher).filter(Teacher.name.ilike('%bharat%')).first()
existing_hari = db.query(Teacher).filter(Teacher.name.ilike('%hari%')).first()

# Add bharat if not exists
if existing_bharat:
    print(f"✅ Bharat already exists (ID: {existing_bharat.id})")
    bharat = existing_bharat
else:
    bharat = Teacher(
        name='bharat',
        email='bharat@college.edu',
        max_hours_per_week=20,
        available_slots=[]
    )
    db.add(bharat)
    db.commit()
    db.refresh(bharat)
    print(f"✅ Added teacher: bharat (ID: {bharat.id})")

# Add hari if not exists
if existing_hari:
    print(f"✅ Hari already exists (ID: {existing_hari.id})")
    hari = existing_hari
else:
    hari = Teacher(
        name='hari',
        email='hari@college.edu',
        max_hours_per_week=20,
        available_slots=[]
    )
    db.add(hari)
    db.commit()
    db.refresh(hari)
    print(f"✅ Added teacher: hari (ID: {hari.id})")

# Get subjects and classes
subjects = db.query(Subject).all()
groups = db.query(ClassGroup).all()

print(f"\nAvailable: {len(subjects)} subjects, {len(groups)} class groups")

# Assign lessons to bharat
print(f"\n📚 Assigning lessons to bharat...")
bharat_lesson_count = 0
for subject in subjects[:3]:  # First 3 subjects
    for group in groups[:2]:  # First 2 classes
        lesson = Lesson(
            lessons_per_week=4,
            length_per_lesson=1
        )
        lesson.teachers.append(bharat)
        lesson.subjects.append(subject)
        lesson.class_groups.append(group)
        db.add(lesson)
        bharat_lesson_count += 1

db.commit()
print(f"✅ Created {bharat_lesson_count} lessons for bharat")

# Assign lessons to hari
print(f"\n📚 Assigning lessons to hari...")
hari_lesson_count = 0
for subject in subjects[3:6]:  # Next 3 subjects
    for group in groups[2:4]:  # Next 2 classes
        lesson = Lesson(
            lessons_per_week=4,
            length_per_lesson=1
        )
        lesson.teachers.append(hari)
        lesson.subjects.append(subject)
        lesson.class_groups.append(group)
        db.add(lesson)
        hari_lesson_count += 1

db.commit()
print(f"✅ Created {hari_lesson_count} lessons for hari")

# Verify
print("\n=== VERIFICATION ===")
all_teachers = db.query(Teacher).all()
print(f"Total teachers: {len(all_teachers)}")

all_lessons = db.query(Lesson).all()
print(f"Total lessons: {len(all_lessons)}")

bharat_lessons = [l for l in all_lessons if bharat in l.teachers]
hari_lessons = [l for l in all_lessons if hari in l.teachers]

print(f"\nbharat: {len(bharat_lessons)} lessons (approx {len(bharat_lessons) * 4} periods/week)")
print(f"hari: {len(hari_lessons)} lessons (approx {len(hari_lessons) * 4} periods/week)")

db.close()

print("\n" + "="*50)
print("✅ SETUP COMPLETE!")
print("="*50)
print("\nNEXT STEPS:")
print("1. Open: http://localhost:8000/timetable_page.html")
print("2. Click 'Generate New Schedule' button")
print("3. Wait 5-10 seconds for generation")
print("4. Click 'Load Latest Timetable'")
print("5. Go to 'Load Factor' tab to see bharat and hari with assignments")
print("6. Go to 'Classes/Grades' tab to see all divisions including TE-AI-DS-C")
