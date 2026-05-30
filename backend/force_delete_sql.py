
import sqlite3

def force_delete():
    conn = sqlite3.connect('timetable.db')
    cur = conn.cursor()
    
    try:
        # Teachers to check: kottawar, sharma, gothane
        # Subjects to check: professional, technical, sustainable, physics, energy
        
        # 1. Find the Lesson IDs to delete
        # We need to join with lesson_teachers and lesson_subjects
        query = """
        SELECT DISTINCT l.id, t.name, s.name 
        FROM lessons l
        JOIN lesson_teachers lt ON l.id = lt.lesson_id
        JOIN teachers t ON lt.teacher_id = t.id
        JOIN lesson_subjects ls ON l.id = ls.lesson_id
        JOIN subjects s ON ls.subject_id = s.id
        WHERE (t.name LIKE '%Kottawar%' OR t.name LIKE '%Sharma%' OR t.name LIKE '%Gothane%')
          AND (s.name LIKE '%Professional%' OR s.name LIKE '%Technical%' OR s.name LIKE '%Sustainable%' OR s.name LIKE '%Physics%' OR s.name LIKE '%Energy%')
        """
        cur.execute(query)
        rows = cur.fetchall()
        
        lesson_ids = list(set([r[0] for r in rows]))
        print(f"Found Lesson IDs to delete: {lesson_ids}")
        
        for lid in lesson_ids:
            print(f"Deleting Lesson {lid}...")
            # Delete Timetable Entries that match the lesson's teacher/subject/group
            # (Simplest way to match is by the teacher and subject combination actually assigned in that lesson)
            cur.execute("""
                DELETE FROM timetable_entries 
                WHERE teacher_id IN (SELECT teacher_id FROM lesson_teachers WHERE lesson_id = ?)
                  AND subject_id IN (SELECT subject_id FROM lesson_subjects WHERE lesson_id = ?)
            """, (lid, lid))
            
            # Delete association rows
            cur.execute("DELETE FROM lesson_teachers WHERE lesson_id = ?", (lid,))
            cur.execute("DELETE FROM lesson_class_groups WHERE lesson_id = ?", (lid,))
            cur.execute("DELETE FROM lesson_subjects WHERE lesson_id = ?", (lid,))
            
            # Delete lesson itself
            cur.execute("DELETE FROM lessons WHERE id = ?", (lid,))
            
        # 2. Update teacher loads
        cur.execute("UPDATE teachers SET max_hours_per_week = 8 WHERE name LIKE '%Kottawar%'")
        cur.execute("UPDATE teachers SET max_hours_per_week = 8 WHERE name LIKE '%Sharma%'")
        cur.execute("UPDATE teachers SET max_hours_per_week = 13 WHERE name LIKE '%Gothane%'")
        
        # 3. Clear direct subject-teacher associations
        # (This avoids them appearing as 'owned' by these teachers in some UI lists)
        cur.execute("UPDATE subjects SET teacher_id = NULL WHERE name LIKE '%Professional%' OR name LIKE '%Technical%' OR name LIKE '%Sustainable%' OR name LIKE '%Physics%' OR name LIKE '%Energy%'")
        
        conn.commit()
        print("Success: Raw SQL deletion complete.")
        
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    force_delete()
