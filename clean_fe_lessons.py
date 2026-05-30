#!/usr/bin/env python3
"""
Clean up FE lessons - remove duplicates and fix teacher assignments
"""

import sqlite3

def clean_and_fix_fe_lessons():
    conn = sqlite3.connect('timetable.db')
    cursor = conn.cursor()
    
    print("=== CLEANING FE LESSONS ===")
    
    # Get FE division IDs
    cursor.execute("SELECT id, name FROM class_groups WHERE name LIKE 'FE-%'")
    fe_divisions = {row[1]: row[0] for row in cursor.fetchall()}
    print(f"FE Divisions: {list(fe_divisions.keys())}")
    
    # Get all FE subjects we want to keep
    fe_subjects = [
        'Applied Mechanics',
        'Engineering Physics',
        'Environmental Studies',
        'Linear Algebra and Differential Calculus',
        'Statistical Methods',
        'Programming & Problem Solving',
        'Fundamentals of Data Structure',
        'Computer Laboratory I',
        'Computer Laboratory II',
        'Professional and Technical Communication',
        'Design Thinking',
        'Critical Thinking and Problem Solving'
    ]
    
    # Get subject IDs
    subject_ids = {}
    for subject in fe_subjects:
        cursor.execute("SELECT id FROM subjects WHERE name = ?", (subject,))
        result = cursor.fetchone()
        if result:
            subject_ids[subject] = result[0]
    
    print(f"Found {len(subject_ids)} FE subjects")
    
    # Proper teacher mapping based on subject expertise
    teacher_map = {
        'Applied Mechanics': 5,  # Mrs. Manasi D. Karajgar
        'Engineering Physics': 3,  # Dr. Suvarna S. Gothane
        'Environmental Studies': 4,  # Dr. Bhaghyshri A. Tingare
        'Linear Algebra and Differential Calculus': 1,  # Dr. V. G. Kottawar
        'Statistical Methods': 6,  # Mrs. Neeta J. Mahale
        'Programming & Problem Solving': 2,  # Dr. Manish Sharma
        'Fundamentals of Data Structure': 7,  # Mrs. Rasika V. Wattamwar
        'Computer Laboratory I': 5,  # Mrs. Manasi D. Karajgar
        'Computer Laboratory II': 3,  # Dr. Suvarna S. Gothane
        'Professional and Technical Communication': 1,  # Dr. V. G. Kottawar
        'Design Thinking': 4,  # Dr. Bhaghyshri A. Tingare
        'Critical Thinking and Problem Solving': 2,  # Dr. Manish Sharma
    }
    
    # For each FE division, keep only one lesson per subject
    for div_name, div_id in fe_divisions.items():
        print(f"\nProcessing {div_name}:")
        
        for subject_name, subject_id in subject_ids.items():
            # Find all lessons for this division + subject
            cursor.execute("""
                SELECT l.id FROM lessons l
                JOIN lesson_class_groups lcg ON l.id = lcg.lesson_id
                JOIN lesson_subjects ls ON l.id = ls.lesson_id
                WHERE lcg.class_group_id = ? AND ls.subject_id = ?
            """, (div_id, subject_id))
            
            lessons = cursor.fetchall()
            lesson_ids = [row[0] for row in lessons]
            
            if len(lesson_ids) > 1:
                # Keep the first one, delete the rest
                keep_id = lesson_ids[0]
                delete_ids = lesson_ids[1:]
                
                for delete_id in delete_ids:
                    # Delete associations first
                    cursor.execute("DELETE FROM lesson_teachers WHERE lesson_id = ?", (delete_id,))
                    cursor.execute("DELETE FROM lesson_class_groups WHERE lesson_id = ?", (delete_id,))
                    cursor.execute("DELETE FROM lesson_subjects WHERE lesson_id = ?", (delete_id,))
                    cursor.execute("DELETE FROM lessons WHERE id = ?", (delete_id,))
                
                print(f"  {subject_name}: Removed {len(delete_ids)} duplicates, kept 1")
                
                # Assign correct teacher to the kept lesson
                teacher_id = teacher_map.get(subject_name)
                if teacher_id:
                    cursor.execute("DELETE FROM lesson_teachers WHERE lesson_id = ?", (keep_id,))
                    try:
                        cursor.execute(
                            "INSERT INTO lesson_teachers (lesson_id, teacher_id) VALUES (?, ?)",
                            (keep_id, teacher_id)
                        )
                    except sqlite3.IntegrityError:
                        pass
            elif len(lesson_ids) == 1:
                # Just fix the teacher assignment
                keep_id = lesson_ids[0]
                teacher_id = teacher_map.get(subject_name)
                if teacher_id:
                    cursor.execute("DELETE FROM lesson_teachers WHERE lesson_id = ?", (keep_id,))
                    try:
                        cursor.execute(
                            "INSERT INTO lesson_teachers (lesson_id, teacher_id) VALUES (?, ?)",
                            (keep_id, teacher_id)
                        )
                    except sqlite3.IntegrityError:
                        pass
                print(f"  {subject_name}: Fixed teacher assignment")
            else:
                print(f"  {subject_name}: No lesson found (will create)")
                # Create new lesson
                cursor.execute(
                    "INSERT INTO lessons (lessons_per_week, length_per_lesson) VALUES (3, 1)",
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
                teacher_id = teacher_map.get(subject_name)
                if teacher_id:
                    try:
                        cursor.execute(
                            "INSERT INTO lesson_teachers (lesson_id, teacher_id) VALUES (?, ?)",
                            (lesson_id, teacher_id)
                        )
                    except sqlite3.IntegrityError:
                        pass
    
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
    
    # Show teacher assignments
    print("\n=== FINAL TEACHER ASSIGNMENTS ===")
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
    print("\n✓ FE lessons cleaned and fixed!")

if __name__ == "__main__":
    clean_and_fix_fe_lessons()
