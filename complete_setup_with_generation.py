"""
Complete setup WITH automatic timetable generation
"""
import sqlite3
import requests
import time

API_BASE = "http://localhost:8000/api"

print("=" * 70)
print("COMPLETE SETUP WITH TIMETABLE GENERATION")
print("=" * 70)

# Step 1: Reset database
print("\n[1/7] Resetting database...")
conn = sqlite3.connect('backend/timetable.db')
c = conn.cursor()

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
print("\n[2/7] Adding teachers...")
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

# Step 3: Add subjects
print("\n[3/7] Adding CS subjects...")
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
print("\n[4/7] Adding class groups...")
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
print("\n[5/7] Adding rooms...")
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

# Step 6: Add time slots
print("\n[6/7] Adding time slots...")
days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
periods = [
    (1, '09:00', '10:00', False),
    (2, '10:00', '11:00', False),
    (3, '11:00', '12:00', False),
    (0, '12:00', '13:00', True),
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
conn.close()
print(f"   ✓ Added {slot_count} time slots")

# Step 7: GENERATE TIMETABLE
print("\n[7/7] Generating timetable...")
try:
    response = requests.post(
        f"{API_BASE}/solvers/generate",
        params={"method": "csp", "name": "Initial Timetable"}
    )
    
    if response.status_code == 200:
        version = response.json()
        print(f"   ✓ Generation started (Version ID: {version['id']})")
        
        # Wait for generation to complete
        print("   Waiting for generation to complete...", end="", flush=True)
        for i in range(30):
            time.sleep(1)
            print(".", end="", flush=True)
            
            latest = requests.get(f"{API_BASE}/timetables/latest").json()
            status = latest.get('status')
            
            if status == 'active':
                entries = len(latest.get('entries', []))
                print(f"\n   ✓ SUCCESS! Generated {entries} timetable entries")
                break
            elif status in ['failed', 'error']:
                print(f"\n   ✗ FAILED: {status}")
                break
        else:
            print("\n   ⏱️  Timeout (but may still be processing)")
    else:
        error = response.json()
        print(f"   ✗ Failed: {error.get('detail', response.status_code)}")
        
except Exception as e:
    print(f"   ✗ Error: {e}")

# Final verification
print("\n" + "=" * 70)
print("VERIFICATION")
print("=" * 70)

try:
    r = requests.get(f"{API_BASE}/timetables/latest")
    if r.status_code == 200:
        data = r.json()
        print(f"\n✓ Timetable Status: {data.get('status')}")
        print(f"✓ Entries: {len(data.get('entries', []))}")
        print(f"✓ Algorithm: {data.get('algorithm')}")
    else:
        print(f"\n✗ No timetable found (Status: {r.status_code})")
except Exception as e:
    print(f"\n✗ Error checking timetable: {e}")

print("\n" + "=" * 70)
print("READY TO USE!")
print("=" * 70)
print("\nOpen: http://127.0.0.1:8000/timetable_page.html")
print("Go to 'View Timetable' tab")
print("Click 'Refresh' button")
print("\nYou should see the generated timetable with CS subjects!")
print("=" * 70)
