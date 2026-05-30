#!/usr/bin/env python3
"""
Add missing FE teachers from load distribution sheet
"""

import sqlite3

def add_fe_teachers():
    conn = sqlite3.connect('timetable.db')
    cursor = conn.cursor()
    
    print("=== ADDING FE TEACHERS ===")
    
    # FE teachers from load distribution sheet
    fe_teachers = [
        ("Ms. Neeta Katariya", "neeta.katariya@college.edu"),
        ("T & P", "t.p@college.edu"),
        ("HASS", "hass@college.edu"),
        ("Mr. Amit Uphad", "amit.uphad@college.edu"),
        ("Dr. N. Beedri", "n.beedri@college.edu"),
        ("Mrs. Savita Jatti", "savita.jatti@college.edu"),
        ("Mrs. Subhashini Ramteke", "subhashini.ramteke@college.edu"),
        ("Mr. Sunil Payghan", "sunil.payghan@college.edu"),
    ]
    
    teacher_ids = {}
    for name, email in fe_teachers:
        # Check if teacher already exists
        cursor.execute("SELECT id FROM teachers WHERE name = ?", (name,))
        result = cursor.fetchone()
        
        if result:
            teacher_ids[name] = result[0]
            print(f"✓ {name} already exists (ID: {result[0]})")
        else:
            cursor.execute(
                "INSERT INTO teachers (name, email, max_hours_per_week) VALUES (?, ?, 20)",
                (name, email)
            )
            teacher_ids[name] = cursor.lastrowid
            print(f"✓ Added {name} (ID: {cursor.lastrowid})")
    
    conn.commit()
    
    # Now update FE lessons with correct teachers based on load distribution
    print("\n=== UPDATING FE LESSONS WITH CORRECT TEACHERS ===")
    
    # Get FE division IDs
    cursor.execute("SELECT id, name FROM class_groups WHERE name LIKE 'FE-%'")
    fe_divisions = {row[1]: row[0] for row in cursor.fetchall()}
    
    # Teacher assignments based on load distribution sheet
    fe_assignments = [
        # (Subject, Teacher, Divisions)
        ("Engineering Physics", "Mr. Amit Uphad", ["FE-A", "FE-B"]),
        ("Engineering Physics", "Dr. N. Beedri", ["FE-C"]),
        ("Applied Mechanics", "Mrs. Savita Jatti", ["FE-A"]),
        ("Applied Mechanics", "Mrs. Subhashini Ramteke", ["FE-B"]),
        ("Applied Mechanics", "Mr. Sunil Payghan", ["FE-C"]),
        ("Linear Algebra and Differential Calculus", "Ms. Neeta Katariya", ["FE-B", "FE-C"]),
    ]
    
    for subject_name, teacher_name, divisions in fe_assignments:
        teacher_id = teacher_ids.get(teacher_name)
        
        # Get subject ID
        cursor.execute("SELECT id FROM subjects WHERE name = ?", (subject_name,))
        subject_result = cursor.fetchone()
        
        if not subject_result:
            print(f"⚠ Subject not found: {subject_name}")
            continue
        
        subject_id = subject_result[0]
        
        for div_name in divisions:
            div_id = fe_divisions.get(div_name)
            if not div_id:
                continue
            
            # Find the lesson
            cursor.execute("""
                SELECT l.id FROM lessons l
                JOIN lesson_class_groups lcg ON l.id = lcg.lesson_id
                JOIN lesson_subjects ls ON l.id = ls.lesson_id
                WHERE lcg.class_group_id = ? AND ls.subject_id = ?
            """, (div_id, subject_id))
            
            lesson_result = cursor.fetchone()
            if lesson_result:
                lesson_id = lesson_result[0]
                
                # Remove existing teacher assignments
                cursor.execute("DELETE FROM lesson_teachers WHERE lesson_id = ?", (lesson_id,))
                
                # Add correct teacher
                if teacher_id:
                    try:
                        cursor.execute(
                            "INSERT INTO lesson_teachers (lesson_id, teacher_id) VALUES (?, ?)",
                            (lesson_id, teacher_id)
                        )
                        print(f"✓ {div_name} | {subject_name} -> {teacher_name}")
                    except sqlite3.IntegrityError:
                        print(f"✗ Failed to assign {teacher_name} to {div_name} | {subject_name}")
    
    conn.commit()
    
    # Show final FE assignments
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
    print("\n✓ FE teachers added and assigned!")

if __name__ == "__main__":
    add_fe_teachers()
