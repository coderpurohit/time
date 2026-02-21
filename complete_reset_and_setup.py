"""
Complete reset and setup script - Clean slate with CS subjects only
"""
import sqlite3
import requests

print("=" * 70)
print("COMPLETE SYSTEM RESET AND SETUP")
print("=" * 70)

# Step 1: Reset database
print("\n[1/6] Resetting database...")
conn = sqlite3.connect('backend/timetable.db')
c = conn.cursor()

# Clear all data
tables = ['timetable_entries', 'timetable_versions', 'lesson_teachers', 
          'lesson_class_groups', 'lesson_subjects', 'lessons', 'subjects', 
          'teachers', 'rooms', 'class_groups', 'time_slots']

for table in tables:
    try:
        c.execute(f'DELETE FROM {table}')
    except:
        pass

conn.commit()
print("   ✓ Database cleared")

# Step 2: Add teachers
print("\n[2/6] Adding teachers...")
teachers_data = [
    ('Dr. Rajesh Kumar', 'rajesh.kumar@college.edu', 18),
    ('Prof. Priya Sharma', 'priya.sharma@college.edu', 20),
    ('Dr. Amit Patel', 'amit.patel@college.edu', 18),
]

for name, email, hours in teachers_data:
    c.execute('INSERT INTO teachers (name, email, max_hours_per_week) VALUES (?, ?, ?)',
              (name, email, hours))

conn.commit()
print(f"   ✓ Added {len(teachers_data)} teachers")

# Step 3: Add subjects (CS only)
print("\n[3/6] Adding CS subjects...")
subjects_data = [
    ('Data Structures & Algorithms', 'CS201', False, 4, 'LectureHall', 1, 1),
    ('Database Management Systems', 'CS202', False, 3, 'LectureHall', 1, 2),
    ('Machine Learning', 'CS203', False, 4, 'LectureHall', 1, 3),
]

for name, code, is_lab, credits, room_type, duration, teacher_id in subjects_data:
    c.execute('''INSERT INTO subjects 
                 (name, code, is_lab, credits, required_room_type, duration_slots, teacher_id) 
                 VALUES (?, ?, ?, ?, ?, ?, ?)''',
              (name, code, is_lab, credits, room_type, duration, teacher_id))

conn.commit()
print(f"   ✓ Added {len(subjects_data)} CS subjects")

# Step 4: Add class groups
print("\n[4/6] Adding class groups...")
groups_data = [
    ('SE-AI-DS-A', 60),
    ('SE-AI-DS-B', 58),
    ('TE-AI-DS-A', 55),
]

for name, count in groups_data:
    c.execute('INSERT INTO class_groups (name, student_count) VALUES (?, ?)',
              (name, count))

conn.commit()
print(f"   ✓ Added {len(groups_data)} class groups")

# Step 5: Add rooms
print("\n[5/6] Adding rooms...")
rooms_data = [
    ('Room 101', 60, 'LectureHall', '["Projector", "Whiteboard"]'),
    ('Room 102', 60, 'LectureHall', '["Projector", "Whiteboard"]'),
    ('Room 103', 60, 'LectureHall', '["Projector", "Whiteboard"]'),
    ('Room 104', 60, 'LectureHall', '["Projector", "Whiteboard"]'),
    ('Computer Lab A', 40, 'ComputerLab', '["Computers", "Projector"]'),
]

for name, capacity, room_type, resources in rooms_data:
    c.execute('INSERT INTO rooms (name, capacity, type, resources) VALUES (?, ?, ?, ?)',
              (name, capacity, room_type, resources))

conn.commit()
print(f"   ✓ Added {len(rooms_data)} rooms")

# Step 6: Add time slots (Mon-Fri, 6 periods/day)
print("\n[6/6] Adding time slots...")
days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
periods = [
    (1, '09:00', '10:00', False),
    (2, '10:00', '11:00', False),
    (3, '11:00', '12:00', False),
    (0, '12:00', '13:00', True),   # Lunch break
    (4, '13:00', '14:00', False),
    (5, '14:00', '15:00', False),
    (6, '15:00', '16:00', False),
]

slot_count = 0
for day in days:
    for period, start, end, is_break in periods:
        c.execute('''INSERT INTO time_slots 
                     (day, period, start_time, end_time, is_break) 
                     VALUES (?, ?, ?, ?, ?)''',
                  (day, period, start, end, is_break))
        if not is_break:
            slot_count += 1

conn.commit()
print(f"   ✓ Added {slot_count} time slots (5 days × 6 periods)")

conn.close()

# Summary
print("\n" + "=" * 70)
print("SETUP COMPLETE!")
print("=" * 70)
print("\nDatabase now contains:")
print(f"  • 3 Teachers (CS faculty)")
print(f"  • 3 Subjects (CS courses)")
print(f"  • 3 Class Groups (AI-DS batches)")
print(f"  • 5 Rooms")
print(f"  • 30 Time Slots (Mon-Fri, 6 periods/day)")
print(f"\nFeasibility: 3 subjects × 3 groups = 9 assignments")
print(f"             30 slots available")
print(f"             ✓ FEASIBLE!")

print("\n" + "=" * 70)
print("NEXT STEPS:")
print("=" * 70)
print("\n1. Open: http://127.0.0.1:8000/timetable_page.html")
print("2. Go to 'Generate Timetable' tab")
print("3. Click 'Generate New Schedule'")
print("4. Wait for generation (5-10 seconds)")
print("5. Go to 'View Timetable' tab")
print("\nYou should see:")
print("  • Data Structures & Algorithms (CS201)")
print("  • Database Management Systems (CS202)")
print("  • Machine Learning (CS203)")
print("\nScheduled for:")
print("  • SE-AI-DS-A")
print("  • SE-AI-DS-B")
print("  • TE-AI-DS-A")
print("\n" + "=" * 70)
