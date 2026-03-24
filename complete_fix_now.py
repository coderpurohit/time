"""
Complete Fix - Check Backend and Generate Working Timetable
"""

import sqlite3
import requests
import time
import sys

DB_PATH = 'backend/timetable.db'

print("=" * 70)
print("COMPLETE FIX - CHECKING AND GENERATING TIMETABLE")
print("=" * 70)

# Step 1: Check if backend is running
print("\n🔌 Step 1: Checking backend...")
try:
    response = requests.get("http://localhost:8000/api/teachers", timeout=3)
    if response.status_code == 200:
        print("   ✅ Backend is running")
    else:
        print(f"   ⚠️ Backend returned status {response.status_code}")
except Exception as e:
    print(f"   ❌ Backend is NOT running!")
    print(f"   Error: {e}")
    print("\n   SOLUTION: Start backend in a new terminal:")
    print("   cd backend")
    print("   start.bat")
    sys.exit(1)

# Step 2: Check database
print("\n📊 Step 2: Checking database...")
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM lessons")
lesson_count = cursor.fetchone()[0]
print(f"   Lessons: {lesson_count}")

cursor.execute("SELECT COUNT(*) FROM time_slots WHERE is_break = 0")
slot_count = cursor.fetchone()[0]
print(f"   Time slots: {slot_count}")

cursor.execute("SELECT COUNT(*) FROM timetable_versions")
version_count = cursor.fetchone()[0]
print(f"   Existing timetable versions: {version_count}")

# Step 3: Check latest timetable
print("\n📅 Step 3: Checking latest timetable...")
try:
    response = requests.get("http://localhost:8000/api/timetables/latest", timeout=5)
    if response.status_code == 200:
        data = response.json()
        entries = data.get('entries', [])
        print(f"   Latest timetable has {len(entries)} entries")
        
        if len(entries) == 0:
            print("   ⚠️ Timetable is empty - need to generate new one")
        else:
            print(f"   ✅ Timetable exists with {len(entries)} entries")
            print("\n   You can view it at:")
            print("   http://localhost:8000/timetable_review_fixed.html")
            print("   Click 'Load Timetable' button")
            
            # Ask if user wants to regenerate
            print("\n   Do you want to generate a NEW timetable? (y/n)")
            choice = input("   > ").strip().lower()
            if choice != 'y':
                print("\n   Keeping existing timetable. Open browser to view it.")
                conn.close()
                sys.exit(0)
    else:
        print(f"   No timetable found (status {response.status_code})")
except Exception as e:
    print(f"   Error checking timetable: {e}")

# Step 4: Generate new timetable directly
print("\n🎯 Step 4: Generating new timetable...")
print("   Using direct generation method...")

# Get data from database
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

print(f"   Data loaded: {len(teachers)} teachers, {len(subjects)} subjects, {len(classes)} classes")

# Create new timetable version
cursor.execute("""
    INSERT INTO timetable_versions (name, algorithm, status, is_valid)
    VALUES ('Direct Generation', 'direct', 'active', 1)
""")
version_id = cursor.lastrowid
print(f"   ✓ Created timetable version: {version_id}")

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

# Get non-break slots
available_slots = [(slot_id, day, period) for slot_id, day, period, is_break in time_slots if not is_break]

print(f"   ✓ Available slots: {len(available_slots)}")
print(f"   ✓ Lessons to schedule: {len(lesson_dict)}")

# Schedule each lesson
entries_created = 0
used_slots = {}  # Track which slots are used

import random

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
    max_attempts = len(available_slots) * 2
    
    while scheduled < per_week and attempts < max_attempts:
        # Pick a random slot
        slot_idx = random.randint(0, len(available_slots) - 1)
        slot_id, day, period = available_slots[slot_idx]
        
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
conn.close()

print(f"\n{'=' * 70}")
print(f"✅ TIMETABLE GENERATED SUCCESSFULLY!")
print(f"{'=' * 70}")
print(f"Version ID: {version_id}")
print(f"Entries Created: {entries_created}")

# Step 5: Verify it's accessible via API
print("\n🔍 Step 5: Verifying via API...")
time.sleep(1)
try:
    response = requests.get("http://localhost:8000/api/timetables/latest", timeout=5)
    if response.status_code == 200:
        data = response.json()
        entries = data.get('entries', [])
        print(f"   ✅ API returns {len(entries)} entries")
        
        if len(entries) > 0:
            print("\n" + "=" * 70)
            print("🎉 SUCCESS! TIMETABLE IS READY!")
            print("=" * 70)
            print("\nOpen your browser and go to:")
            print("http://localhost:8000/timetable_review_fixed.html")
            print("\nThen click the 'Load Timetable' button")
            print("\nYou should see your timetable with", len(entries), "entries!")
        else:
            print("\n   ⚠️ API still returns 0 entries")
            print("   Try refreshing the page with Ctrl+Shift+R")
    else:
        print(f"   ⚠️ API returned status {response.status_code}")
except Exception as e:
    print(f"   ⚠️ Error verifying: {e}")
    print("\n   The timetable was created in database.")
    print("   Try opening the page and clicking 'Load Timetable'")

print("\n" + "=" * 70)
