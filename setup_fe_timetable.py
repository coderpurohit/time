#!/usr/bin/env python3
"""
Setup FE (First Year) Divisions with proper teacher assignments
FE-A, FE-B, FE-C with appropriate subjects and load distribution
"""

import sqlite3
import sys
sys.path.append('backend')

def setup_fe_divisions():
    conn = sqlite3.connect('timetable.db')
    cursor = conn.cursor()
    
    # Check if FE divisions already exist
    cursor.execute("SELECT id, name FROM class_groups WHERE name LIKE 'FE-%'")
    existing = cursor.fetchall()
    print(f"Existing FE divisions: {existing}")
    
    # Add FE divisions if they don't exist
    fe_divisions = ['FE-A', 'FE-B', 'FE-C']
    fe_ids = {}
    
    for div in fe_divisions:
        cursor.execute("SELECT id FROM class_groups WHERE name = ?", (div,))
        result = cursor.fetchone()
        if result:
            fe_ids[div] = result[0]
            print(f"{div} already exists with ID: {result[0]}")
        else:
            cursor.execute("INSERT INTO class_groups (name, student_count) VALUES (?, 60)", (div,))
            fe_ids[div] = cursor.lastrowid
            print(f"Created {div} with ID: {cursor.lastrowid}")
    
    conn.commit()
    
    # Get all teachers
    cursor.execute("SELECT id, name FROM teachers")
    teachers = cursor.fetchall()
    print(f"\nAvailable teachers: {len(teachers)}")
    
    # Get FE subjects (common first year subjects)
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
    subject_map = {}
    for subj_name in fe_subjects:
        cursor.execute("SELECT id FROM subjects WHERE name = ?", (subj_name,))
        result = cursor.fetchone()
        if result:
            subject_map[subj_name] = result[0]
    
    print(f"\nFE Subjects found: {len(subject_map)}")
    
    # Assign teachers to FE subjects (distribute evenly)
    teacher_assignments = {
        'Applied Mechanics': ['Mrs. Manasi D. Karajgar'],
        'Engineering Physics': ['Dr. Suvarna S. Gothane'],
        'Environmental Studies': ['Mrs. Kanchan C. Patil'],
        'Linear Algebra and Differential Calculus': ['Dr. Aryani Gangadhara'],
        'Statistical Methods': ['Dr. Aryani Gangadhara'],
        'Programming & Problem Solving': ['Dr. Deepali Sale'],
        'Fundamentals of Data Structure': ['Mrs. Pallavi R. Shingade'],
        'Computer Laboratory I': ['Mrs. Aparna Lavangade'],
        'Computer Laboratory II': ['Mrs. Kanchan C. Patil'],
        'Professional and Technical Communication': ['Dr. V. G. Kottawar', 'Mrs. Pallavi R. Shingade'],
        'Design Thinking': ['Mrs. Rajshri T. Ingle'],
        'Critical Thinking and Problem Solving': ['Dr. V. G. Kottawar']
    }
    
    # Create lessons for each FE division
    lessons_created = 0
    for div_name, div_id in fe_ids.items():
        print(f"\nSetting up lessons for {div_name}:")
        
        for subject_name, subject_id in subject_map.items():
            # Check if lesson already exists for this division and subject
            cursor.execute("""
                SELECT l.id FROM lessons l
                JOIN lesson_class_groups lcg ON l.id = lcg.lesson_id
                JOIN lesson_subjects ls ON l.id = ls.lesson_id
                WHERE lcg.class_group_id = ? AND ls.subject_id = ?
            """, (div_id, subject_id))
            
            if cursor.fetchone():
                continue
            
            # Get teacher for this subject
            teacher_names = teacher_assignments.get(subject_name, [])
            teacher_id = None
            
            for t_name in teacher_names:
                cursor.execute("SELECT id FROM teachers WHERE name = ?", (t_name,))
                t_result = cursor.fetchone()
                if t_result:
                    teacher_id = t_result[0]
                    break
            
            # Create lesson
            cursor.execute("""
                INSERT INTO lessons (lessons_per_week, length_per_lesson)
                VALUES (?, ?)
            """, (3, 1))
            
            lesson_id = cursor.lastrowid
            
            # Link to class group
            cursor.execute("""
                INSERT INTO lesson_class_groups (lesson_id, class_group_id)
                VALUES (?, ?)
            """, (lesson_id, div_id))
            
            # Link to subject (ignore if already exists)
            try:
                cursor.execute("""
                    INSERT INTO lesson_subjects (lesson_id, subject_id)
                    VALUES (?, ?)
                """, (lesson_id, subject_id))
            except sqlite3.IntegrityError:
                pass
            
            # Link to teacher if found (ignore if already exists)
            if teacher_id:
                try:
                    cursor.execute("""
                        INSERT INTO lesson_teachers (lesson_id, teacher_id)
                        VALUES (?, ?)
                    """, (lesson_id, teacher_id))
                except sqlite3.IntegrityError:
                    pass
            
            lessons_created += 1
            print(f"  Created lesson for {subject_name}")
    
    conn.commit()
    print(f"\n✓ Total lessons created: {lessons_created}")
    
    # Verify setup
    print("\n--- Verification ---")
    for div_name, div_id in fe_ids.items():
        cursor.execute("""
            SELECT COUNT(*) FROM lessons l
            JOIN lesson_class_groups lcg ON l.id = lcg.lesson_id
            WHERE lcg.class_group_id = ?
        """, (div_id,))
        count = cursor.fetchone()[0]
        print(f"{div_name}: {count} lessons")
    
    conn.close()
    print("\n✓ FE Divisions setup complete!")

if __name__ == "__main__":
    setup_fe_divisions()
