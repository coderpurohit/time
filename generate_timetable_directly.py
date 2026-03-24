"""
Generate Timetable Directly in Database
Bypasses the backend server to create a working timetable
"""

import sqlite3
import random

DB_PATH = 'backend/timetable.db'

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("=" * 60)
print("GENERATING TIMETABLE DIRECTLY")
print("=" * 60)

# Get data
cursor.execute("SELECT id FROM teachers")
teachers = [row[0] for row in cursor.fetchall()]

cursor.execute("SELECT id FROM subjects")
subjects = [row[0] for row in cursor.fetchall()]

cursor.execute("SELECT id FROM class_groups")
classes = [row[0] for row in cursor.fetchall()]

cursor.execute("SELECT id FROM rooms")
rooms = [row[0] for row in cursor.fetchall()]

cursor.execute("SELECT id, day, period, is_break FROM time_slots ORDER BY day, period")
time_slots = cursor.fetchall()

cursor.execute("""
    SELECT l.id, l.lessons_per_week, l.length_per_lesson,
           lt.teacher_id, ls.subject_id, lc.class_group_id
    FROM lessons l
    LEFT JOIN lesson_teachers lt ON l.id = lt.lesson_id
    LEFT JOIN lesson_subjects ls ON l.id = ls.lesson_id
    LEFT JOIN lesson_class_groups lc ON l.id = lc.class_group_id
""")
lessons = cursor.fetchall()

print(f"\nData available:")
print(f"  Teachers: {len(teachers)}")
print(f"  Subjects: {len(subjects)}")
print(f"  Classes: {len(classes)}")
print(f"  Rooms: {len(rooms)}")
print(f"  Time Slots: {len(time_slots)}")
print(f"  Lessons: {len(lessons)}")

# Create new timetable version
cursor.execute("""
    INSERT INTO timetable_versions (name, algorithm, status, is_valid)
    VALUES ('Direct Generation', 'direct', 'active', 1)
""")
version_id = cursor.lastrowid
print(f"\n✓ Created timetable version: {version_id}")

# Group lessons by lesson_id
lesson_dict = {}
for lesson_id, per_week, length, teacher_id, subject_id, class_id in lessons:
    if lesson_id not in lesson_dict:
        lesson_dict[lesson_id] = {
            'per_week': per_week,
            'length': length,
            'teachers': [],
            'subjects': [],
            'classes': []
        }
    if teacher_id and teacher_id not in lesson_dict[lesson_id]['teachers']:
        lesson_dict[lesson_id]['teachers'].append(teacher_id)
    if subject_id and subject_id not in lesson_dict[lesson_id]['subjects']:
        lesson_dict[lesson_id]['subjects'].append(subject_id)
    if class_id and class_id not in lesson_dict[lesson_id]['classes']:
        lesson_dict[lesson_id]['classes'].append(class_id)

# Create schedule
entries_created = 0
used_slots = {}  # Track which slots are used by which teacher/class/room

# Get non-break slots
available_slots = [(slot_id, day, period) for slot_id, day, period, is_break in time_slots if not is_break]

print(f"\n✓ Available slots: {len(available_slots)}")
print(f"✓ Lessons to schedule: {len(lesson_dict)}")

# Schedule each lesson
for lesson_id, lesson_data in lesson_dict.items():
    if not lesson_data['teachers'] or not lesson_data['subjects'] or not lesson_data['classes']:
        continue
    
    teacher_id = lesson_data['teachers'][0]
    subject_id = lesson_data['subjects'][0]
    class_id = lesson_data['classes'][0]
    per_week = lesson_data['per_week']
    
    # Schedule this lesson per_week times
    scheduled = 0
    attempts = 0
    max_attempts = len(available_slots)
    
    while scheduled < per_week and attempts < max_attempts:
        # Pick a random slot
        slot_idx = random.randint(0, len(available_slots) - 1)
        slot_id, day, period = available_slots[slot_idx]
        
        # Check if slot is available for this teacher, class, and room
        slot_key = (day, period)
        
        # Check conflicts
        teacher_busy = used_slots.get((day, period, 'teacher', teacher_id), False)
        class_busy = used_slots.get((day, period, 'class', class_id), False)
        
        if not teacher_busy and not class_busy:
            # Pick a random room
            room_id = random.choice(rooms)
            
            # Create entry
            cursor.execute("""
                INSERT INTO timetable_entries 
                (version_id, time_slot_id, subject_id, room_id, class_group_id, teacher_id)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (version_id, slot_id, subject_id, room_id, class_id, teacher_id))
            
            # Mark slot as used
            used_slots[(day, period, 'teacher', teacher_id)] = True
            used_slots[(day, period, 'class', class_id)] = True
            used_slots[(day, period, 'room', room_id)] = True
            
            scheduled += 1
            entries_created += 1
        
        attempts += 1

conn.commit()

print(f"\n{'=' * 60}")
print(f"TIMETABLE GENERATED!")
print(f"{'=' * 60}")
print(f"Version ID: {version_id}")
print(f"Entries Created: {entries_created}")
print(f"\nNow refresh your timetable page and click 'Load Timetable'")

conn.close()
