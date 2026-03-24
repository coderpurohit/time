"""
Remove Generic CS301-CS515 Subjects
Keep only meaningful named subjects
"""

import sqlite3

DB_PATH = 'backend/timetable.db'

def clean_generic_subjects():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("=" * 60)
    print("CLEANING GENERIC SUBJECTS")
    print("=" * 60)
    
    # Find all generic CS### subjects
    cursor.execute("""
        SELECT id, name, code 
        FROM subjects 
        WHERE code LIKE 'CS3%' OR code LIKE 'CS4%' OR code LIKE 'CS5%'
        ORDER BY code
    """)
    
    generic_subjects = cursor.fetchall()
    
    print(f"\nFound {len(generic_subjects)} generic CS subjects:")
    for subject_id, name, code in generic_subjects:
        print(f"  ID {subject_id:3d}: {name:30s} ({code})")
    
    if not generic_subjects:
        print("\n✅ No generic subjects to remove!")
        conn.close()
        return
    
    # Delete lessons first
    subject_ids = [s[0] for s in generic_subjects]
    placeholders = ','.join('?' * len(subject_ids))
    
    # Check lesson_subjects junction table
    cursor.execute(f"SELECT COUNT(*) FROM lesson_subjects WHERE subject_id IN ({placeholders})", subject_ids)
    lesson_subject_count = cursor.fetchone()[0]
    
    if lesson_subject_count > 0:
        print(f"\n🗑️  Deleting {lesson_subject_count} lesson-subject associations...")
        cursor.execute(f"DELETE FROM lesson_subjects WHERE subject_id IN ({placeholders})", subject_ids)
    
    # Delete the subjects
    print(f"\n🗑️  Deleting {len(generic_subjects)} generic subjects...")
    cursor.execute(f"DELETE FROM subjects WHERE id IN ({placeholders})", subject_ids)
    
    conn.commit()
    
    # Show remaining subjects
    cursor.execute("SELECT id, name, code FROM subjects ORDER BY name")
    remaining = cursor.fetchall()
    
    print(f"\n{'=' * 60}")
    print(f"CLEANUP COMPLETE!")
    print(f"{'=' * 60}")
    print(f"Removed: {len(generic_subjects)} generic subjects")
    print(f"Remaining: {len(remaining)} subjects\n")
    
    print("REMAINING SUBJECTS:")
    print("-" * 60)
    for subject_id, name, code in remaining:
        print(f"  {subject_id:3d}. {name:40s} ({code})")
    
    conn.close()

if __name__ == "__main__":
    clean_generic_subjects()
