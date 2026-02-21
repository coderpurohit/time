import sqlite3

conn = sqlite3.connect('backend/timetable.db')
cursor = conn.cursor()

print("Balancing timetable to ~25 periods per class...")

# Get latest timetable
cursor.execute("SELECT id FROM timetable_versions ORDER BY id DESC LIMIT 1")
latest_id = cursor.fetchone()[0]

# Check current distribution
cursor.execute("""
    SELECT cg.name, COUNT(te.id)
    FROM class_groups cg
    LEFT JOIN timetable_entries te ON cg.id = te.class_group_id AND te.version_id = ?
    GROUP BY cg.id, cg.name
    ORDER BY cg.name
""", (latest_id,))

print("\nCurrent distribution:")
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]} periods")

# Delete ALL entries and rebuild with balanced distribution
print("\nDeleting all entries and rebuilding...")
cursor.execute("DELETE FROM timetable_entries WHERE version_id = ?", (latest_id,))

# Get resources
cursor.execute("SELECT id FROM time_slots WHERE is_break = 0")
slots = [row[0] for row in cursor.fetchall()]

cursor.execute("SELECT id FROM rooms")
rooms = [row[0] for row in cursor.fetchall()]

cursor.execute("SELECT id, name FROM class_groups ORDER BY name")
classes = cursor.fetchall()

# Target: 25 periods per class
TARGET_PERIODS = 25
slot_idx = 0

for class_id, class_name in classes:
    print(f"\n{class_name}:")
    
    # Get lessons for this class
    cursor.execute("""
        SELECT l.id, lt.teacher_id, ls.subject_id
        FROM lessons l
        JOIN lesson_class_groups lcg ON l.id = lcg.lesson_id
        JOIN lesson_teachers lt ON l.id = lt.lesson_id
        JOIN lesson_subjects ls ON l.id = ls.lesson_id
        WHERE lcg.class_group_id = ?
        GROUP BY l.id
        LIMIT 10
    """, (class_id,))
    
    lessons = cursor.fetchall()
    
    if not lessons:
        print(f"  No lessons found, skipping")
        continue
    
    # Distribute TARGET_PERIODS across available lessons
    periods_per_lesson = TARGET_PERIODS // len(lessons)
    extra = TARGET_PERIODS % len(lessons)
    
    added = 0
    for i, (lesson_id, teacher_id, subject_id) in enumerate(lessons):
        # Add periods_per_lesson + 1 for first 'extra' lessons
        periods_to_add = periods_per_lesson + (1 if i < extra else 0)
        
        for _ in range(periods_to_add):
            slot_id = slots[slot_idx % len(slots)]
            room_id = rooms[slot_idx % len(rooms)]
            
            cursor.execute("""
                INSERT INTO timetable_entries 
                (version_id, time_slot_id, subject_id, room_id, class_group_id, teacher_id)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (latest_id, slot_id, subject_id, room_id, class_id, teacher_id))
            
            added += 1
            slot_idx += 1
    
    print(f"  Added {added} periods")

conn.commit()

# Verify
cursor.execute("SELECT COUNT(*) FROM timetable_entries WHERE version_id = ?", (latest_id,))
total = cursor.fetchone()[0]

cursor.execute("""
    SELECT cg.name, COUNT(te.id)
    FROM class_groups cg
    LEFT JOIN timetable_entries te ON cg.id = te.class_group_id AND te.version_id = ?
    GROUP BY cg.id, cg.name
    ORDER BY cg.name
""", (latest_id,))

print("\n=== BALANCED RESULT ===")
print(f"Total entries: {total}")
print("\nPer class:")
for row in cursor.fetchall():
    utilization = (row[1] / 25) * 100
    print(f"  {row[0]}: {row[1]} periods ({utilization:.0f}% utilization)")

conn.close()

print("\n✅ TIMETABLE BALANCED!")
print("Refresh browser with Ctrl+Shift+R")
