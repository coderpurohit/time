import sys
sys.path.insert(0, 'backend')

from app.infrastructure.database import SessionLocal
from app.infrastructure.models import Teacher, Lesson, Subject, ClassGroup

db = SessionLocal()

print("=== ASSIGNING LESSONS TO NEW TEACHERS ===")

# Find bharat and hari
bharat = db.query(Teacher).filter(Teacher.name.ilike('%bharat%')).first()
hari = db.query(Teacher).filter(Teacher.name.ilike('%hari%')).first()

if not bharat:
    print("❌ Teacher 'bharat' not found")
else:
    print(f"✅ Found: {bharat.name} (ID: {bharat.id})")

if not hari:
    print("❌ Teacher 'hari' not found")
else:
    print(f"✅ Found: {hari.name} (ID: {hari.id})")

if not bharat and not hari:
    print("\n⚠️  Neither teacher found. Please add them first.")
    db.close()
    exit(1)

# Get available subjects and classes
subjects = db.query(Subject).all()
groups = db.query(ClassGroup).all()

print(f"\nAvailable: {len(subjects)} subjects, {len(groups)} class groups")

# Assign lessons to bharat
if bharat:
    print(f"\n📚 Assigning lessons to {bharat.name}...")
    # Assign 3-4 subjects to bharat
    for i, subject in enumerate(subjects[:4]):
        for group in groups[:3]:  # First 3 classes
            lesson = Lesson(
                lessons_per_week=3,
                length_per_lesson=1
            )
            lesson.teachers.append(bharat)
            lesson.subjects.append(subject)
            lesson.class_groups.append(group)
            db.add(lesson)
    db.commit()
    print(f"✅ Assigned lessons to {bharat.name}")

# Assign lessons to hari
if hari:
    print(f"\n📚 Assigning lessons to {hari.name}...")
    # Assign 3-4 subjects to hari
    for i, subject in enumerate(subjects[3:7]):
        for group in groups[3:6]:  # Next 3 classes
            lesson = Lesson(
                lessons_per_week=3,
                length_per_lesson=1
            )
            lesson.teachers.append(hari)
            lesson.subjects.append(subject)
            lesson.class_groups.append(group)
            db.add(lesson)
    db.commit()
    print(f"✅ Assigned lessons to {hari.name}")

# Verify
print("\n=== VERIFICATION ===")
all_lessons = db.query(Lesson).all()
print(f"Total lessons in database: {len(all_lessons)}")

if bharat:
    bharat_lessons = [l for l in all_lessons if bharat in l.teachers]
    print(f"{bharat.name}: {len(bharat_lessons)} lessons")

if hari:
    hari_lessons = [l for l in all_lessons if hari in l.teachers]
    print(f"{hari.name}: {len(hari_lessons)} lessons")

db.close()

print("\n✅ DONE! Now regenerate the timetable:")
print("   1. Open http://localhost:8000/timetable_page.html")
print("   2. Click 'Generate New Schedule'")
print("   3. Wait for generation to complete")
print("   4. Click 'Load Latest Timetable'")
print("   5. Check 'Load Factor' tab")
