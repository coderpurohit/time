import sqlite3

conn = sqlite3.connect('backend/timetable.db')
cursor = conn.cursor()

print("=== WORKLOAD ANALYSIS ===\n")

# Count what the solver THINKS it needs to schedule
cursor.execute("SELECT COUNT(*) FROM class_groups")
total_groups = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM subjects")
total_subjects = cursor.fetchone()[0]

print(f"Current approach (WRONG):")
print(f"  Class Groups: {total_groups}")
print(f"  Subjects: {total_subjects}")
print(f"  Required assignments: {total_groups} × {total_subjects} = {total_groups * total_subjects}")
print(f"  (Trying to assign EVERY subject to EVERY class group)\n")

# Count what ACTUALLY needs to be scheduled based on lessons
cursor.execute("""
    SELECT 
        l.id,
        l.lessons_per_week,
        GROUP_CONCAT(DISTINCT c.name) as classes,
        GROUP_CONCAT(DISTINCT s.name) as subjects
    FROM lessons l
    LEFT JOIN lesson_class_groups lcg ON l.id = lcg.lesson_id
    LEFT JOIN class_groups c ON lcg.class_group_id = c.id
    LEFT JOIN lesson_subjects ls ON l.id = ls.lesson_id
    LEFT JOIN subjects s ON ls.subject_id = s.id
    GROUP BY l.id
""")

lessons = cursor.fetchall()
total_periods_needed = sum(lesson[1] for lesson in lessons)

print(f"Correct approach (using LESSONS table):")
print(f"  Total lessons defined: {len(lessons)}")
print(f"  Total periods needed per week: {total_periods_needed}")
print(f"\nLesson breakdown:")
for lesson in lessons:
    print(f"  Lesson {lesson[0]}: {lesson[1]} periods/week")
    print(f"    Classes: {lesson[2]}")
    print(f"    Subjects: {lesson[3]}")

# Check available capacity
cursor.execute("SELECT COUNT(*) FROM time_slots WHERE is_break = 0")
available_slots = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM rooms")
total_rooms = cursor.fetchone()[0]

print(f"\n=== CAPACITY ===")
print(f"Available time slots (non-break): {available_slots}")
print(f"Available rooms: {total_rooms}")
print(f"Total capacity: {available_slots} slots (can handle {available_slots} periods)")
print(f"\nFeasibility: {'✓ FEASIBLE' if total_periods_needed <= available_slots else '✗ NOT FEASIBLE'}")
print(f"  Need: {total_periods_needed} periods")
print(f"  Have: {available_slots} slots")

conn.close()
