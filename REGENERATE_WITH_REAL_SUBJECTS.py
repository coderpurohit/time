import sqlite3
import random

conn = sqlite3.connect('backend/timetable.db')
cursor = conn.cursor()

print("=== REGENERATING TIMETABLE WITH REAL SUBJECTS ONLY ===\n")

# Step 1: Get real subjects only (not CS4XX dummy ones)
cursor.execute('''
    SELECT id, code, name, is_lab, duration_slots 
    FROM subjects 
    WHERE code NOT LIKE 'CS4%'
    ORDER BY code
''')
real_subjects = cursor.fetchall()

print(f"Real subjects ({len(real_subjects)}):")
for sid, code, name, is_lab, duration in real_subjects:
    type_str = "Lab" if is_lab else "Theory"
    print(f"  {code:6} - {name:35} ({type_str}, {duration} period)")

# Step 2: Get all data
cursor.execute('SELECT id, name FROM teachers ORDER BY id')
teachers = cursor.fetchall()

cursor.execute('SELECT id, name FROM rooms ORDER BY id')
rooms = cursor.fetchall()

cursor.execute('SELECT id, name FROM class_groups ORDER BY name')
groups = cursor.fetchall()

cursor.execute('SELECT id, day, period FROM time_slots WHERE is_break = 0 ORDER BY day, period')
slots = cursor.fetchall()

print(f"\nTeachers: {len(teachers)}")
print(f"Rooms: {len(rooms)}")
print(f"Classes: {len(groups)}")
print(f"Time slots: {len(slots)}")

# Step 3: Delete old timetable
cursor.execute('DELETE FROM timetable_entries')
cursor.execute('DELETE FROM timetable_versions')

cursor.execute('''
    INSERT INTO timetable_versions (name, algorithm, status, is_valid)
    VALUES ('Real Subjects Only', 'manual', 'active', 1)
''')
timetable_id = cursor.lastrowid
conn.commit()

print(f"\nCreated timetable ID: {timetable_id}")

# Step 4: Generate realistic schedule
# Each class gets 25 periods distributed across the 7 subjects
# Theory subjects: ML(4), AI(4), CN(3), OS(4), HCI(3) = 18 periods
# Lab subjects: MLL(2x2=4), CNL(2x2=4) = 8 periods (labs are 2 periods each)
# Total: 18 + 8 = 26 periods, but we'll do 25 to fit

subject_distribution = {
    'ML': 4,   # Machine Learning - 4 periods
    'AI': 4,   # Artificial Intelligence - 4 periods  
    'CN': 3,   # Computer Networks - 3 periods
    'OS': 4,   # Operating Systems - 4 periods
    'HCI': 3,  # Human Computer Interaction - 3 periods
    'MLL': 2,  # ML Lab - 2 double periods = 4 slots
    'CNL': 2,  # CN Lab - 2 double periods = 4 slots
}

entries_created = 0
teacher_load = {t[0]: 0 for t in teachers}

print(f"\nGenerating schedule for {len(groups)} classes...")

for group_id, group_name in groups:
    print(f"\n  {group_name}:")
    used_slots = set()
    
    # Assign subjects according to distribution
    for subject_id, code, name, is_lab, duration in real_subjects:
        if code not in subject_distribution:
            continue
            
        periods_needed = subject_distribution[code]
        
        for occurrence in range(periods_needed):
            # Find available consecutive slots if lab (duration > 1)
            if duration > 1:
                # Find consecutive slots
                found = False
                for i in range(len(slots) - duration + 1):
                    consecutive = slots[i:i+duration]
                    # Check if all are same day and consecutive periods
                    if (len(set(s[1] for s in consecutive)) == 1 and  # Same day
                        all(s[0] not in used_slots for s in consecutive)):  # All available
                        # Use these slots
                        for slot_id, day, period in consecutive:
                            used_slots.add(slot_id)
                            
                            teacher_id = min(teachers, key=lambda t: teacher_load[t[0]])[0]
                            teacher_load[teacher_id] += 1
                            
                            room_id = random.choice(rooms)[0]
                            
                            cursor.execute('''
                                INSERT INTO timetable_entries 
                                (version_id, time_slot_id, subject_id, room_id, class_group_id, teacher_id)
                                VALUES (?, ?, ?, ?, ?, ?)
                            ''', (timetable_id, slot_id, subject_id, room_id, group_id, teacher_id))
                            
                            entries_created += 1
                        
                        found = True
                        break
                
                if not found:
                    print(f"    WARNING: Could not find {duration} consecutive slots for {code}")
            else:
                # Single period subject
                available = [s for s in slots if s[0] not in used_slots]
                if not available:
                    print(f"    WARNING: No more slots for {code}")
                    continue
                
                slot_id, day, period = random.choice(available)
                used_slots.add(slot_id)
                
                teacher_id = min(teachers, key=lambda t: teacher_load[t[0]])[0]
                teacher_load[teacher_id] += 1
                
                room_id = random.choice(rooms)[0]
                
                cursor.execute('''
                    INSERT INTO timetable_entries 
                    (version_id, time_slot_id, subject_id, room_id, class_group_id, teacher_id)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (timetable_id, slot_id, subject_id, room_id, group_id, teacher_id))
                
                entries_created += 1
        
        print(f"    {code}: {periods_needed} periods assigned")

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

print(f"\n📊 Verification:")
for name, count in cursor.fetchall():
    print(f"  {name}: {count} periods")

# Check subject distribution
cursor.execute('''
    SELECT s.code, s.name, COUNT(te.id) as count
    FROM subjects s
    LEFT JOIN timetable_entries te ON s.id = te.subject_id AND te.version_id = ?
    WHERE s.code NOT LIKE 'CS4%'
    GROUP BY s.id, s.code, s.name
    ORDER BY s.code
''', (timetable_id,))

print(f"\n📚 Subject Distribution:")
for code, name, count in cursor.fetchall():
    print(f"  {code:6} - {name:35}: {count} times")

conn.close()

print("\n" + "="*60)
print("✅ DONE! Refresh browser (Ctrl+Shift+R) to see real subjects")
print("="*60)
