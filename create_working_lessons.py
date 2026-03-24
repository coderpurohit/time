"""
Create Working Lessons for Timetable Generation
"""

import sqlite3

DB_PATH = 'backend/timetable.db'

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("=" * 60)
print("CREATING WORKING LESSONS")
print("=" * 60)

# Clear existing lessons
cursor.execute("DELETE FROM lesson_subjects")
cursor.execute("DELETE FROM lesson_teachers")
cursor.execute("DELETE FROM lesson_class_groups")
cursor.execute("DELETE FROM lessons")
conn.commit()

# Get data
cursor.execute("SELECT id, name FROM teachers LIMIT 10")
teachers = cursor.fetchall()

cursor.execute("SELECT id, name, code FROM subjects")
subjects = cursor.fetchall()

cursor.execute("SELECT id, name FROM class_groups WHERE name LIKE '%AIDS%'")
classes = cursor.fetchall()

print(f"\nAvailable:")
print(f"  Teachers: {len(teachers)}")
print(f"  Subjects: {len(subjects)}")
print(f"  Classes: {len(classes)}")

if not teachers or not subjects or not classes:
    print("\n❌ Missing required data!")
    conn.close()
    exit(1)

# Create lessons for each class-subject combination
lesson_id = 1
created = 0

for class_id, class_name in classes[:9]:  # Use first 9 classes
    for subject_id, subject_name, subject_code in subjects[:6]:  # Use first 6 subjects
        # Create lesson
        cursor.execute("""
            INSERT INTO lessons (id, lessons_per_week, length_per_lesson)
            VALUES (?, ?, ?)
        """, (lesson_id, 3, 1))  # 3 times per week, 1 slot each
        
        # Assign teacher (rotate through teachers)
        teacher_id = teachers[lesson_id % len(teachers)][0]
        cursor.execute("""
            INSERT INTO lesson_teachers (lesson_id, teacher_id)
            VALUES (?, ?)
        """, (lesson_id, teacher_id))
        
        # Assign subject
        cursor.execute("""
            INSERT INTO lesson_subjects (lesson_id, subject_id)
            VALUES (?, ?)
        """, (lesson_id, subject_id))
        
        # Assign class
        cursor.execute("""
            INSERT INTO lesson_class_groups (lesson_id, class_group_id)
            VALUES (?, ?)
        """, (lesson_id, class_id))
        
        print(f"  ✓ Lesson {lesson_id}: {class_name} - {subject_name} (Teacher {teacher_id})")
        
        lesson_id += 1
        created += 1

conn.commit()

print(f"\n{'=' * 60}")
print(f"CREATED {created} LESSONS")
print(f"{'=' * 60}")

# Verify
cursor.execute("SELECT COUNT(*) FROM lessons")
total_lessons = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM lesson_teachers")
total_teacher_links = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM lesson_subjects")
total_subject_links = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM lesson_class_groups")
total_class_links = cursor.fetchone()[0]

print(f"\nVerification:")
print(f"  Lessons: {total_lessons}")
print(f"  Teacher Links: {total_teacher_links}")
print(f"  Subject Links: {total_subject_links}")
print(f"  Class Links: {total_class_links}")

if total_lessons == total_teacher_links == total_subject_links == total_class_links:
    print("\n✅ All lessons properly configured!")
else:
    print("\n⚠️  Some lessons missing associations!")

conn.close()

print("\n" + "=" * 60)
print("NOW TRY GENERATING THE TIMETABLE")
print("=" * 60)
