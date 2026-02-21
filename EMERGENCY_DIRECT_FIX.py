import sqlite3
import random

conn = sqlite3.connect('backend/timetable.db')
cursor = conn.cursor()

print("=== EMERGENCY DIRECT TIMETABLE GENERATION ===\n")

# Step 1: Get all data
cursor.execute('SELECT id, name FROM teachers ORDER BY id')
teachers = cursor.fetchall()

cursor.execute('SELECT id, name FROM subjects ORDER BY id')
subjects = cursor.fetchall()

cursor.execute('SELECT id, name FROM rooms ORDER BY id')
rooms = cursor.fetchall()

cursor.execute('SELECT id, name FROM class_groups ORDER BY id')
groups = cursor.fetchall()

cursor.execute('SELECT id, day, period FROM time_slots WHERE is_break = 0 ORDER BY day, period')
slots = cursor.fetchall()

print(f"Teachers: {len(teachers)}")
print(f"Subjects: {len(subjects)}")
print(f"Rooms: {len(rooms)}")
print(f"Groups: {len(groups)}")
print(f"Slots: {len(slots)}")

# Step 2: Create a new timetable version
cursor.execute('''
    INSERT INTO timetable_versions (name, algorithm, status, is_valid)
    VALUES ('Emergency Fix', 'manual', 'active', 1)
''')
timetable_id = cursor.lastrowid
print(f"\nCreated timetable ID: {timetable_id}")

# Step 3: Distribute teachers evenly across all classes
# Target: 25 periods per class, distributed across all teachers
target_per_class = 25
teacher_ids = [t[0] for t in teachers]
subject_ids = [s[0] for s in subjects]
room_ids = [r[0] for r in rooms]

entries_created = 0
teacher_load = {t[0]: 0 for t in teachers}

print(f"\nGenerating {len(groups)} × {target_per_class} = {len(groups) * target_per_class} entries...")

for group_id, group_name in groups:
    print(f"  Scheduling {group_name}...")
    
    # Track used slots for this group
    used_slots = set()
    
    for period_num in range(target_per_class):
        # Find an available slot
        available_slots = [s for s in slots if s[0] not in used_slots]
        if not available_slots:
            print(f"    WARNING: No more slots available for {group_name}")
            break
        
        slot = random.choice(available_slots)
        slot_id = slot[0]
        used_slots.add(slot_id)
        
        # Pick teacher with lowest load
        teacher_id = min(teacher_ids, key=lambda t: teacher_load[t])
        teacher_load[teacher_id] += 1
        
        # Pick random subject and room
        subject_id = random.choice(subject_ids)
        room_id = random.choice(room_ids)
        
        # Insert entry
        cursor.execute('''
            INSERT INTO timetable_entries 
            (version_id, time_slot_id, subject_id, room_id, class_group_id, teacher_id)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (timetable_id, slot_id, subject_id, room_id, group_id, teacher_id))
        
        entries_created += 1

conn.commit()

print(f"\n✅ Created {entries_created} timetable entries")

# Step 4: Show teacher distribution
print(f"\n📊 Teacher Load Distribution:")
cursor.execute('''
    SELECT t.name, COUNT(te.id) as entries
    FROM teachers t
    LEFT JOIN timetable_entries te ON t.id = te.teacher_id AND te.version_id = ?
    GROUP BY t.id, t.name
    ORDER BY entries DESC
''', (timetable_id,))

for name, count in cursor.fetchall():
    load_pct = (count / target_per_class) * 100 if target_per_class > 0 else 0
    print(f"  {name}: {count} periods ({load_pct:.1f}%)")

# Step 5: Show class coverage
print(f"\n📚 Class Coverage:")
cursor.execute('''
    SELECT cg.name, COUNT(te.id) as entries
    FROM class_groups cg
    LEFT JOIN timetable_entries te ON cg.id = te.class_group_id AND te.version_id = ?
    GROUP BY cg.id, cg.name
    ORDER BY cg.name
''', (timetable_id,))

for name, count in cursor.fetchall():
    coverage = (count / target_per_class) * 100 if target_per_class > 0 else 0
    print(f"  {name}: {count}/{target_per_class} periods ({coverage:.0f}%)")

conn.close()

print("\n" + "="*60)
print("✅ EMERGENCY FIX COMPLETE!")
print("="*60)
print("\nRefresh your browser (Ctrl+Shift+R) to see the new timetable!")
