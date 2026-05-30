#!/usr/bin/env python3
"""
Create BE (Final Year) curriculum and lessons for all BE divisions
"""

import sqlite3
from sqlite3 import IntegrityError

def create_be_curriculum():
    conn = sqlite3.connect('timetable.db')
    cursor = conn.cursor()
    
    print("=== CREATING BE CURRICULUM ===")
    
    # BE Subjects (typical final year computer engineering subjects)
    be_subjects = [
        ("Machine Learning", "ML", False, 1),
        ("Information Retrieval", "IR", False, 1),
        ("Soft Computing", "SC", False, 1),
        ("Elective III - EAC", "E3-EAC", False, 1),
        ("Elective IV - IR", "E4-IR", False, 1),
        ("Machine Learning Lab", "ML-Lab", True, 2),
        ("Information Retrieval Lab", "IR-Lab", True, 2),
        ("Project Stage I", "Project", True, 4),
    ]
    
    # Insert subjects
    subject_ids = {}
    for name, code, is_lab, duration in be_subjects:
        cursor.execute(
            "INSERT OR IGNORE INTO subjects (name, code, is_lab, duration_slots) VALUES (?, ?, ?, ?)",
            (name, code, is_lab, duration)
        )
        conn.commit()
        cursor.execute("SELECT id FROM subjects WHERE name = ?", (name,))
        result = cursor.fetchone()
        if result:
            subject_ids[name] = result[0]
            print(f"✓ Subject: {name} (ID: {subject_ids[name]})")
        else:
            print(f"✗ Failed to get ID for: {name}")
    
    conn.commit()
    
    # Get BE division IDs
    cursor.execute("SELECT id, name FROM class_groups WHERE name LIKE 'BE-%'")
    be_divisions = {row[1]: row[0] for row in cursor.fetchall()}
    print(f"\nBE Divisions: {be_divisions}")
    
    # Get teachers for BE
    cursor.execute("SELECT id, name FROM teachers WHERE name LIKE '%Neeta%' OR name LIKE '%Snehal%' OR name LIKE '%Manasi%'")
    teachers = {row[1]: row[0] for row in cursor.fetchall()}
    print(f"\nAvailable teachers: {list(teachers.keys())}")
    
    # Create lessons for each BE division
    print("\n=== CREATING LESSONS ===")
    
    # Teacher assignments (simplified)
    teacher_assignments = {
        "Machine Learning": "Mrs. Snehal Malpani",
        "Information Retrieval": "Mrs. Neeta J. Mahale",
        "Soft Computing": "Dr. Manish Sharma",
        "Elective III - EAC": "Mrs. Manasi D. Karajgar",
        "Elective IV - IR": "Mrs. Neeta J. Mahale",
        "Machine Learning Lab": "Mrs. Snehal Malpani",
        "Information Retrieval Lab": "Mrs. Neeta J. Mahale",
        "Project Stage I": "Dr. V. G. Kottawar",
    }
    
    lessons_created = 0
    for div_name, div_id in be_divisions.items():
        print(f"\n--- {div_name} ---")
        for subject_name, subject_id in subject_ids.items():
            # Create lesson
            cursor.execute(
                "INSERT INTO lessons (lessons_per_week, length_per_lesson) VALUES (1, 1)",
            )
            lesson_id = cursor.lastrowid
            
            # Link to class group
            try:
                cursor.execute(
                    "INSERT INTO lesson_class_groups (lesson_id, class_group_id) VALUES (?, ?)",
                    (lesson_id, div_id)
                )
            except IntegrityError:
                pass
            
            # Link to subject
            try:
                cursor.execute(
                    "INSERT INTO lesson_subjects (lesson_id, subject_id) VALUES (?, ?)",
                    (lesson_id, subject_id)
                )
            except IntegrityError:
                pass
            
            # Link to teacher
            teacher_name = teacher_assignments.get(subject_name)
            if teacher_name and teacher_name in teachers:
                teacher_id = teachers[teacher_name]
                try:
                    cursor.execute(
                        "INSERT INTO lesson_teachers (lesson_id, teacher_id) VALUES (?, ?)",
                        (lesson_id, teacher_id)
                    )
                except IntegrityError:
                    pass
            
            lessons_created += 1
            print(f"  ✓ {subject_name}")
    
    conn.commit()
    conn.close()
    
    print(f"\n✓ Created {lessons_created} lessons for BE divisions!")

if __name__ == "__main__":
    create_be_curriculum()
