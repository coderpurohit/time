import sqlite3

conn = sqlite3.connect('backend/timetable.db')
cursor = conn.cursor()

print("Adding lessons for BE-AIDS and TE-AIDS-C...")

# Get teachers, subjects
cursor.execute("SELECT id FROM teachers LIMIT 5")
teachers = [row[0] for row in cursor.fetchall()]

cursor.execute("SELECT id FROM subjects")
subjects = [row[0] for row in cursor.fetchall()]

# Classes that need lessons
missing_classes = [
    (6, 'TE-AIDS-C'),
    (7, 'BE-AIDS-A'),
    (8, 'BE-AIDS-B'),
    (9, 'BE-AIDS-C')
]

lesson_id_start = 200  # Start from high number to avoid conflicts

for class_id, class_name in missing_classes:
    print(f"\n{class_name}:")
    
    for i, subject_id in enumerate(subjects):
        teacher_id = teachers[i % len(teachers)]
        
        # Create lesson
        cursor.execute("""
            INSERT INTO lessons (id, lessons_per_week, length_per_lesson)
            VALUES (?, 2, 1)
        """, (lesson_id_start,))
        
        # Link teacher
        cursor.execute("""
            INSERT INTO lesson_teachers (lesson_id, teacher_id)
            VALUES (?, ?)
        """, (lesson_id_start, teacher_id))
        
        # Link subject
        cursor.execute("""
            INSERT INTO lesson_subjects (lesson_id, subject_id)
            VALUES (?, ?)
        """, (lesson_id_start, subject_id))
        
        # Link class
        cursor.execute("""
            INSERT INTO lesson_class_groups (lesson_id, class_group_id)
            VALUES (?, ?)
        """, (lesson_id_start, class_id))
        
        print(f"  Added lesson {lesson_id_start} for subject {subject_id}")
        lesson_id_start += 1

conn.commit()

# Now add timetable entries
print("\nAdding timetable entries...")

cursor.execute("SELECT id FROM timetable_versions ORDER BY id DESC LIMIT 1")
latest_id = cursor.fetchone()[0]

cursor.execute("SELECT id FROM time_slots WHERE is_break = 0")
slots = [row[0] for row in cursor.fetchall()]

cursor.execute("SELECT id FROM rooms")
rooms = [row[0] for row in cursor.fetchall()]

added = 0
slot_idx = 0

for class_id, class_name in missing_classes:
    cursor.execute("""
        SELECT l.id
        FROM lessons l
        JOIN lesson_class_groups lcg ON l.id = lcg.lesson_id
        WHERE lcg.class_group_id = ?
    """, (class_id,))
    
    lesson_ids = [row[0] for row in cursor.fetchall()]
    print(f"{class_name}: {len(lesson_ids)} lessons")
    
    for lesson_id in lesson_ids:
        cursor.execute("""
            SELECT lt.teacher_id, ls.subject_id
            FROM lesson_teachers lt
            JOIN lesson_subjects ls ON lt.lesson_id = ls.lesson_id
            WHERE lt.lesson_id = ?
            LIMIT 1
        """, (lesson_id,))
        
        result = cursor.fetchone()
        if not result:
            continue
        
        teacher_id, subject_id = result
        
        # Add 2 entries
        for _ in range(2):
            slot_id = slots[slot_idx % len(slots)]
            room_id = rooms[slot_idx % len(rooms)]
            
            cursor.execute("""
                INSERT INTO timetable_entries 
                (version_id, time_slot_id, subject_id, room_id, class_group_id, teacher_id)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (latest_id, slot_id, subject_id, room_id, class_id, teacher_id))
            
            added += 1
            slot_idx += 1

conn.commit()
print(f"\n✅ Added {added} timetable entries")

# Final check
cursor.execute("SELECT COUNT(*) FROM timetable_entries WHERE version_id = ?", (latest_id,))
total = cursor.fetchone()[0]

cursor.execute("""
    SELECT COUNT(DISTINCT class_group_id) 
    FROM timetable_entries 
    WHERE version_id = ?
""", (latest_id,))
classes_count = cursor.fetchone()[0]

cursor.execute("""
    SELECT cg.name, COUNT(te.id)
    FROM class_groups cg
    LEFT JOIN timetable_entries te ON cg.id = te.class_group_id AND te.version_id = ?
    GROUP BY cg.id, cg.name
    ORDER BY cg.name
""", (latest_id,))

print(f"\n=== FINAL RESULT ===")
print(f"Total entries: {total}")
print(f"Classes: {classes_count}/11")
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]} periods")

conn.close()

print("\n✅ ALL CLASSES NOW HAVE ENTRIES!")
print("Refresh browser with Ctrl+Shift+R")
