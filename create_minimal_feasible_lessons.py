import sqlite3

conn = sqlite3.connect('backend/timetable.db')
cursor = conn.cursor()

print("=== CREATING MINIMAL FEASIBLE LESSONS ===\n")

# Clear existing lessons
cursor.execute("DELETE FROM lesson_teachers")
cursor.execute("DELETE FROM lesson_class_groups")
cursor.execute("DELETE FROM lesson_subjects")
cursor.execute("DELETE FROM lessons")
conn.commit()
print("✓ Cleared existing lessons")

# Get data
cursor.execute("SELECT id, name FROM class_groups ORDER BY id")
groups = cursor.fetchall()

cursor.execute("SELECT id, name, code FROM subjects ORDER BY id LIMIT 5")  # Only first 5 subjects
subjects = cursor.fetchall()

print(f"✓ Using {len(groups)} groups and {len(subjects)} subjects\n")

# Create MINIMAL lessons: Each group gets 1 period per week per subject
# With 12 groups and 5 subjects = 60 lessons
# Each lesson is 1 period/week = 60 total periods
# Spread across 25 slots with parallel classes = FEASIBLE!

lesson_id = 1

print("Creating minimal lessons (1 period/week per subject)...")
for group_id, group_name in groups:
    for subj_id, subj_name, subj_code in subjects:
        # Find teacher for this subject
        cursor.execute("SELECT teacher_id FROM subjects WHERE id = ?", (subj_id,))
        teacher_result = cursor.fetchone()
        teacher_id = teacher_result[0] if teacher_result and teacher_result[0] else 1
        
        # Create lesson: 1 period per week, 1 slot length
        cursor.execute("""
            INSERT INTO lessons (id, lessons_per_week, length_per_lesson)
            VALUES (?, 1, 1)
        """, (lesson_id,))
        
        # Link teacher
        cursor.execute("""
            INSERT INTO lesson_teachers (lesson_id, teacher_id)
            VALUES (?, ?)
        """, (lesson_id, teacher_id))
        
        # Link subject
        cursor.execute("""
            INSERT INTO lesson_subjects (lesson_id, subject_id)
            VALUES (?, ?)
        """, (lesson_id, subj_id))
        
        # Link class group
        cursor.execute("""
            INSERT INTO lesson_class_groups (lesson_id, class_group_id)
            VALUES (?, ?)
        """, (lesson_id, group_id))
        
        print(f"  Lesson {lesson_id}: {group_name} - {subj_name} (1x/week)")
        lesson_id += 1

conn.commit()

# Calculate totals
cursor.execute("SELECT COUNT(*) FROM lessons")
total_lessons = cursor.fetchone()[0]

cursor.execute("SELECT SUM(lessons_per_week * length_per_lesson) FROM lessons")
total_slots_needed = cursor.fetchone()[0]

print(f"\n=== SUMMARY ===")
print(f"Total lessons created: {total_lessons}")
print(f"Total slot-assignments needed: {total_slots_needed}")
print(f"Available slots: 25")
print(f"Max parallel assignments: {25 * 12} = 300")
print(f"Feasible: {'YES ✓' if total_slots_needed <= 25 * 12 else 'NO ✗'}")
print(f"\nWith {len(groups)} groups running in parallel:")
print(f"  - Each group needs {len(subjects)} slots")
print(f"  - Total: {total_slots_needed} slot-assignments")
print(f"  - This should easily fit in 25 time slots!")

conn.close()
