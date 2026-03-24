"""
List All Subjects in Database
"""

import sqlite3

DB_PATH = 'backend/timetable.db'

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("=" * 80)
print("ALL SUBJECTS IN DATABASE")
print("=" * 80)

cursor.execute("""
    SELECT s.id, s.name, s.code, s.credits, s.is_lab, s.duration_slots, 
           t.name as teacher_name
    FROM subjects s
    LEFT JOIN teachers t ON s.teacher_id = t.id
    ORDER BY s.name
""")

subjects = cursor.fetchall()

print(f"\nTotal: {len(subjects)} subjects\n")
print(f"{'ID':<5} {'Name':<40} {'Code':<10} {'Credits':<8} {'Type':<8} {'Duration':<10} {'Teacher':<20}")
print("-" * 120)

for subject_id, name, code, credits, is_lab, duration, teacher in subjects:
    type_str = "Lab" if is_lab else "Theory"
    teacher_str = teacher if teacher else "Not Assigned"
    print(f"{subject_id:<5} {name:<40} {code:<10} {credits:<8} {type_str:<8} {duration:<10} {teacher_str:<20}")

conn.close()
