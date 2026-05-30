#!/usr/bin/env python3
"""
Remove non-FE subjects from FE divisions
"""

import sqlite3

def remove_non_fe_subjects():
    conn = sqlite3.connect('timetable.db')
    cursor = conn.cursor()
    
    # Get FE division IDs
    cursor.execute("SELECT id FROM class_groups WHERE name LIKE 'FE-%'")
    fe_div_ids = [row[0] for row in cursor.fetchall()]
    print(f'FE Division IDs: {fe_div_ids}')
    
    # Get FE subject IDs
    fe_subjects = [
        'Applied Mechanics', 'Engineering Physics', 'Environmental Studies',
        'Linear Algebra and Differential Calculus', 'Statistical Methods',
        'Programming & Problem Solving', 'Fundamentals of Data Structure',
        'Computer Laboratory I', 'Computer Laboratory II',
        'Professional and Technical Communication', 'Design Thinking',
        'Critical Thinking and Problem Solving'
    ]
    
    subject_ids = []
    for subject in fe_subjects:
        cursor.execute('SELECT id FROM subjects WHERE name = ?', (subject,))
        result = cursor.fetchone()
        if result:
            subject_ids.append(result[0])
    
    print(f'FE Subject IDs: {subject_ids}')
    
    if not subject_ids:
        print("No FE subjects found!")
        conn.close()
        return
    
    # Delete all lessons for FE divisions that are NOT in FE subjects
    total_deleted = 0
    for div_id in fe_div_ids:
        placeholders = ','.join('?' * len(subject_ids))
        query = f'''
            SELECT l.id, s.name FROM lessons l
            JOIN lesson_class_groups lcg ON l.id = lcg.lesson_id
            JOIN lesson_subjects ls ON l.id = ls.lesson_id
            JOIN subjects s ON ls.subject_id = s.id
            WHERE lcg.class_group_id = ? AND ls.subject_id NOT IN ({placeholders})
        '''
        
        cursor.execute(query, (div_id,) + tuple(subject_ids))
        to_delete = cursor.fetchall()
        
        print(f'\nDivision ID {div_id}: Found {len(to_delete)} non-FE lessons to delete')
        for lesson_id, subject_name in to_delete:
            print(f'  Deleting: {subject_name} (ID: {lesson_id})')
            cursor.execute('DELETE FROM lesson_teachers WHERE lesson_id = ?', (lesson_id,))
            cursor.execute('DELETE FROM lesson_class_groups WHERE lesson_id = ?', (lesson_id,))
            cursor.execute('DELETE FROM lesson_subjects WHERE lesson_id = ?', (lesson_id,))
            cursor.execute('DELETE FROM lessons WHERE id = ?', (lesson_id,))
            total_deleted += 1
    
    conn.commit()
    
    # Verify
    print('\n=== VERIFICATION ===')
    for div_id in fe_div_ids:
        cursor.execute('''
            SELECT cg.name, COUNT(DISTINCT l.id) 
            FROM lessons l
            JOIN lesson_class_groups lcg ON l.id = lcg.lesson_id
            JOIN class_groups cg ON lcg.class_group_id = cg.id
            WHERE cg.id = ?
            GROUP BY cg.name
        ''', (div_id,))
        result = cursor.fetchone()
        if result:
            print(f'{result[0]}: {result[1]} lessons')
    
    # Show remaining subjects per FE division
    print('\n=== REMAINING FE SUBJECTS ===')
    cursor.execute('''
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
    ''')
    
    rows = cursor.fetchall()
    print(f"{'Division':<10} | {'Subject':<40} | {'Teacher'}")
    print("-" * 85)
    for row in rows:
        division, subject, teacher = row
        teacher_name = teacher if teacher else "NOT ASSIGNED"
        print(f"{division:<10} | {subject:<40} | {teacher_name}")
    
    conn.close()
    print(f'\n✓ Removed {total_deleted} non-FE subjects from FE divisions')

if __name__ == "__main__":
    remove_non_fe_subjects()
