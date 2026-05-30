#!/usr/bin/env python3
"""
Recreate FE (First Year) lessons with proper teacher assignments
"""

import sqlite3

def recreate_fe_lessons():
    conn = sqlite3.connect('timetable.db')
    cursor = conn.cursor()
    
    print("=== RECREATING FE LESSONS ===")
    
    # Get FE division IDs
    cursor.execute("SELECT id, name FROM class_groups WHERE name LIKE 'FE-%'")
    fe_divisions = {row[1]: row[0] for row in cursor.fetchall()}
    print(f"FE Divisions: {list(fe_divisions.keys())}")
    
    # FE subjects with proper teacher assignments
    fe_curriculum = [
        ('Applied Mechanics', 5),  # Mrs. Manasi D. Karajgar
        ('Engineering Physics', 3),  # Dr. Suvarna S. Gothane
        ('Environmental Studies', 4),  # Dr. Bhaghyshri A. Tingare
        ('Linear Algebra and Differential Calculus', 1),  # Dr. V. G. Kottawar
        ('Statistical Methods', 6),  # Mrs. Neeta J. Mahale
        ('Programming & Problem Solving', 2),  # Dr. Manish Sharma
        ('Fundamentals of Data Structure', 7),  # Mrs. Rasika V. Wattamwar
        ('Computer Laboratory I', 5),  # Mrs. Manasi D. Karajgar
        ('Computer Laboratory II', 3),  # Dr. Suvarna S. Gothane
        ('Professional and Technical Communication', 1),  # Dr. V. G. Kottawar
        ('Design Thinking', 4),  # Dr. Bhaghyshri A. Tingare
        ('Critical Thinking and Problem Solving', 2),  # Dr. Manish Sharma
    ]
    
    # Get subject IDs
    subject_map = {}
    for subject_name, teacher_id in fe_curriculum:
        cursor.execute("SELECT id FROM subjects WHERE name = ?", (subject_name,))
        result = cursor.fetchone()
        if result:
            subject_map[subject_name] = result[0]
        else:
            print(f"⚠ Subject not found: {subject_name}")
    
    print(f"\nFound {len(subject_map)} FE subjects")
    
    # Get teacher names
    cursor.execute("SELECT id, name FROM teachers")
    teachers = {row[0]: row[1] for row in cursor.fetchall()}
    
    # Create lessons for each FE division
    total_created = 0
    for div_name, div_id in fe_divisions.items():
        print(f"\n--- Setting up {div_name} ---")
        
        for subject_name, teacher_id in fe_curriculum:
            subject_id = subject_map.get(subject_name)
            if not subject_id:
                continue
            
            # Check if lesson already exists
            cursor.execute("""
                SELECT l.id FROM lessons l
                JOIN lesson_class_groups lcg ON l.id = lcg.lesson_id
                JOIN lesson_subjects ls ON l.id = ls.lesson_id
                WHERE lcg.class_group_id = ? AND ls.subject_id = ?
            """, (div_id, subject_id))
            
            if cursor.fetchone():
                print(f"  ✓ {subject_name}: Already exists")
                continue
            
            # Create lesson
            cursor.execute(
                "INSERT INTO lessons (lessons_per_week, length_per_lesson) VALUES (3, 1)"
            )
            lesson_id = cursor.lastrowid
            
            # Link to class group
            cursor.execute(
                "INSERT INTO lesson_class_groups (lesson_id, class_group_id) VALUES (?, ?)",
                (lesson_id, div_id)
            )
            
            # Link to subject
            cursor.execute(
                "INSERT INTO lesson_subjects (lesson_id, subject_id) VALUES (?, ?)",
                (lesson_id, subject_id)
            )
            
            # Link to teacher
            if teacher_id:
                try:
                    cursor.execute(
                        "INSERT INTO lesson_teachers (lesson_id, teacher_id) VALUES (?, ?)",
                        (lesson_id, teacher_id)
                    )
                    teacher_name = teachers.get(teacher_id, "Unknown")
                    print(f"  ✓ {subject_name}: Assigned to {teacher_name}")
                except sqlite3.IntegrityError:
                    print(f"  ✗ {subject_name}: Failed to assign teacher")
            
            total_created += 1
    
    conn.commit()
    
    # Verify
    print("\n=== VERIFICATION ===")
    for div_name, div_id in fe_divisions.items():
        cursor.execute("""
            SELECT COUNT(DISTINCT l.id) FROM lessons l
            JOIN lesson_class_groups lcg ON l.id = lcg.lesson_id
            WHERE lcg.class_group_id = ?
        """, (div_id,))
        count = cursor.fetchone()[0]
        print(f"{div_name}: {count} lessons")
    
    # Show final assignments
    print("\n=== FINAL FE TEACHER ASSIGNMENTS ===")
    cursor.execute("""
        SELECT cg.name AS division, s.name AS subject, t.name AS teacher
        FROM lessons l
        JOIN lesson_class_groups lcg ON l.id = lcg.lesson_id
        JOIN class_groups cg ON lcg.class_group_id = cg.id
        JOIN lesson_subjects ls ON l.id = ls.lesson_id
        JOIN subjects s ON ls.subject_id = s.id
        LEFT JOIN lesson_teachers lt ON l.id = lt.lesson_id
        LEFT JOIN teachers t ON lt.teacher_id = t.id
        WHERE cg.name LIKE 'FE-%'
        ORDER BY cg.name, s.name
    """)
    
    rows = cursor.fetchall()
    print(f"{'Division':<10} | {'Subject':<40} | {'Teacher'}")
    print("-" * 85)
    for row in rows:
        division, subject, teacher = row
        teacher_name = teacher if teacher else "NOT ASSIGNED"
        print(f"{division:<10} | {subject:<40} | {teacher_name}")
    
    conn.close()
    print(f"\n✓ Created {total_created} new FE lessons")
    print("✓ FE lessons recreated successfully!")

if __name__ == "__main__":
    recreate_fe_lessons()
