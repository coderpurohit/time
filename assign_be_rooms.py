#!/usr/bin/env python3
"""
Assign specific classrooms to BE divisions:
- BE-A -> Classroom 12
- BE-B -> Classroom 11
- BE-C -> Any available classroom
"""

import sqlite3

def assign_rooms():
    conn = sqlite3.connect('timetable.db')
    cursor = conn.cursor()
    
    print("=== ASSIGNING ROOMS TO BE DIVISIONS ===")
    
    # Get room IDs
    cursor.execute("SELECT id, name FROM rooms WHERE name LIKE '%12%'")
    room_12 = cursor.fetchone()
    
    cursor.execute("SELECT id, name FROM rooms WHERE name LIKE '%11%'")
    room_11 = cursor.fetchone()
    
    if not room_12:
        print("❌ Classroom 12 not found!")
        # Create it
        cursor.execute("INSERT INTO rooms (name, capacity, type) VALUES ('Classroom 12', 60, 'classroom')")
        room_12_id = cursor.lastrowid
        print(f"✓ Created Classroom 12 (ID: {room_12_id})")
    else:
        room_12_id = room_12[0]
        print(f"✓ Classroom 12 ID: {room_12_id}")
    
    if not room_11:
        print("❌ Classroom 11 not found!")
        # Create it
        cursor.execute("INSERT INTO rooms (name, capacity, type) VALUES ('Classroom 11', 60, 'classroom')")
        room_11_id = cursor.lastrowid
        print(f"✓ Created Classroom 11 (ID: {room_11_id})")
    else:
        room_11_id = room_11[0]
        print(f"✓ Classroom 11 ID: {room_11_id}")
    
    # Get BE division IDs
    cursor.execute("SELECT id, name FROM class_groups WHERE name = 'BE-A'")
    be_a_id = cursor.fetchone()[0]
    
    cursor.execute("SELECT id, name FROM class_groups WHERE name = 'BE-B'")
    be_b_id = cursor.fetchone()[0]
    
    cursor.execute("SELECT id, name FROM class_groups WHERE name = 'BE-C'")
    be_c_id = cursor.fetchone()[0]
    
    print(f"\nBE-A ID: {be_a_id}")
    print(f"BE-B ID: {be_b_id}")
    print(f"BE-C ID: {be_c_id}")
    
    # Update lessons to have preferred rooms
    # We'll add a marker in the lessons table or use a different approach
    # Since lessons table doesn't have room_id, we need to use lesson_rooms table
    
    # Check if lesson_rooms table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='lesson_rooms'")
    if not cursor.fetchone():
        print("\n⚠ lesson_rooms table doesn't exist. Creating it...")
        cursor.execute("""
            CREATE TABLE lesson_rooms (
                lesson_id INTEGER,
                room_id INTEGER,
                PRIMARY KEY (lesson_id, room_id),
                FOREIGN KEY (lesson_id) REFERENCES lessons(id),
                FOREIGN KEY (room_id) REFERENCES rooms(id)
            )
        """)
        conn.commit()
        print("✓ Created lesson_rooms table")
    
    # Assign rooms to BE-A lessons
    print("\n=== ASSIGNING ROOMS ===")
    
    # Get BE-A lessons
    cursor.execute("""
        SELECT l.id, s.name as subject
        FROM lessons l
        JOIN lesson_class_groups lcg ON l.id = lcg.lesson_id
        JOIN lesson_subjects ls ON l.id = ls.lesson_id
        JOIN subjects s ON ls.subject_id = s.id
        WHERE lcg.class_group_id = ?
    """, (be_a_id,))
    
    be_a_lessons = cursor.fetchall()
    print(f"\nBE-A: {len(be_a_lessons)} lessons -> Classroom 12")
    
    for lesson_id, subject in be_a_lessons:
        # Clear any existing room assignments
        cursor.execute("DELETE FROM lesson_rooms WHERE lesson_id = ?", (lesson_id,))
        # Assign Classroom 12
        cursor.execute(
            "INSERT OR IGNORE INTO lesson_rooms (lesson_id, room_id) VALUES (?, ?)",
            (lesson_id, room_12_id)
        )
    
    # Get BE-B lessons
    cursor.execute("""
        SELECT l.id, s.name as subject
        FROM lessons l
        JOIN lesson_class_groups lcg ON l.id = lcg.lesson_id
        JOIN lesson_subjects ls ON l.id = ls.lesson_id
        JOIN subjects s ON ls.subject_id = s.id
        WHERE lcg.class_group_id = ?
    """, (be_b_id,))
    
    be_b_lessons = cursor.fetchall()
    print(f"BE-B: {len(be_b_lessons)} lessons -> Classroom 11")
    
    for lesson_id, subject in be_b_lessons:
        # Clear any existing room assignments
        cursor.execute("DELETE FROM lesson_rooms WHERE lesson_id = ?", (lesson_id,))
        # Assign Classroom 11
        cursor.execute(
            "INSERT OR IGNORE INTO lesson_rooms (lesson_id, room_id) VALUES (?, ?)",
            (lesson_id, room_11_id)
        )
    
    conn.commit()
    
    # Verify assignments
    print("\n=== VERIFICATION ===")
    cursor.execute("""
        SELECT cg.name as division, r.name as room, COUNT(*) as count
        FROM lessons l
        JOIN lesson_class_groups lcg ON l.id = lcg.lesson_id
        JOIN class_groups cg ON lcg.class_group_id = cg.id
        JOIN lesson_rooms lr ON l.id = lr.lesson_id
        JOIN rooms r ON lr.room_id = r.id
        WHERE cg.name LIKE 'BE-%'
        GROUP BY cg.name, r.name
    """)
    
    for row in cursor.fetchall():
        print(f"  {row[0]} -> {row[1]} ({row[2]} lessons)")
    
    conn.close()
    print("\n✓ Room assignments complete!")

if __name__ == "__main__":
    assign_rooms()
