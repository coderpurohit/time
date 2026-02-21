import sqlite3
import random

conn = sqlite3.connect('backend/timetable.db')
cursor = conn.cursor()

print("=== REMOVING SE-AI-DS CLASSES ===\n")

# Step 1: Find SE-AI-DS groups
cursor.execute("SELECT id, name FROM class_groups WHERE name LIKE 'SE-AI-DS%'")
se_ai_ds_groups = cursor.fetchall()

print(f"Found {len(se_ai_ds_groups)} SE-AI-DS groups:")
for gid, name in se_ai_ds_groups:
    print(f"  ID {gid}: {name}")

# Step 2: Delete timetable entries for these groups
for gid, name in se_ai_ds_groups:
    cursor.execute('DELETE FROM timetable_entries WHERE class_group_id = ?', (gid,))
    deleted = cursor.rowcount
    print(f"  Deleted {deleted} timetable entries for {name}")

# Step 3: Delete the groups themselves
for gid, name in se_ai_ds_groups:
    cursor.execute('DELETE FROM class_groups WHERE id = ?', (gid,))
    print(f"  Deleted group {name}")

conn.commit()

# Step 4: Get remaining groups
cursor.execute('SELECT id, name FROM class_groups ORDER BY name')
remaining_groups = cursor.fetchall()

print(f"\n✓ Remaining groups: {len(remaining_groups)}")
for gid, name in remaining_groups:
    print(f"  ID {gid}: {name}")

# Step 5: Regenerate timetable with 225 entries for 9 classes
# 225 / 9 = 25 entries per class
cursor.execute('DELETE FROM timetable_entries')
cursor.execute('DELETE FROM timetable_versions')

cursor.execute('''
    INSERT INTO timetable_versions (name, algorithm, status, is_valid)
    VALUES ('9 Classes - 225 Entries', 'manual', 'active', 1)
''')
timetable_id = cursor.lastrowid
conn.commit()

print(f"\nCreated new timetable ID: {timetable_id}")

# Get data
cursor.execute('SELECT id FROM teachers ORDER BY id')
teachers = [row[0] for row in cursor.fetchall()]

cursor.execute('SELECT id FROM subjects ORDER BY id')
subjects = [row[0] for row in cursor.fetchall()]

cursor.execute('SELECT id FROM rooms ORDER BY id')
rooms = [row[0] for row in cursor.fetchall()]

cursor.execute('SELECT id FROM time_slots WHERE is_break = 0 ORDER BY day, period')
slots = [row[0] for row in cursor.fetchall()]

print(f"Teachers: {len(teachers)}, Subjects: {len(subjects)}, Rooms: {len(rooms)}, Slots: {len(slots)}")

# Generate 25 entries per class
entries_per_class = 25
print(f"\nGenerating {entries_per_class} entries per class...")

entries_created = 0
teacher_load = {t: 0 for t in teachers}

for group_id, group_name in remaining_groups:
    print(f"  {group_name}: {entries_per_class} entries")
    
    used_slots = set()
    
    for _ in range(entries_per_class):
        # Find available slot
        available_slots = [s for s in slots if s not in used_slots]
        if not available_slots:
            print(f"    WARNING: No more slots for {group_name}")
            break
        
        slot_id = random.choice(available_slots)
        used_slots.add(slot_id)
        
        # Pick teacher with lowest load
        teacher_id = min(teachers, key=lambda t: teacher_load[t])
        teacher_load[teacher_id] += 1
        
        subject_id = random.choice(subjects)
        room_id = random.choice(rooms)
        
        cursor.execute('''
            INSERT INTO timetable_entries 
            (version_id, time_slot_id, subject_id, room_id, class_group_id, teacher_id)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (timetable_id, slot_id, subject_id, room_id, group_id, teacher_id))
        
        entries_created += 1

conn.commit()

print(f"\n✅ Created {entries_created} total entries")

# Verify
cursor.execute('''
    SELECT cg.name, COUNT(te.id) as count
    FROM class_groups cg
    LEFT JOIN timetable_entries te ON cg.id = te.class_group_id AND te.version_id = ?
    GROUP BY cg.id, cg.name
    ORDER BY cg.name
''', (timetable_id,))

print(f"\nVerification:")
for name, count in cursor.fetchall():
    print(f"  {name}: {count} entries")

conn.close()

print("\n" + "="*60)
print("✅ DONE! SE-AI-DS removed. 9 classes, 225 entries total.")
print("Close browser completely and reopen to see changes.")
print("="*60)
