"""
Remove Duplicate Subjects from Database
Keep only one instance of each subject based on name
"""

import sqlite3
from collections import defaultdict

DB_PATH = 'backend/timetable.db'

def remove_duplicate_subjects():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("=" * 60)
    print("REMOVING DUPLICATE SUBJECTS")
    print("=" * 60)
    
    # Get all subjects
    cursor.execute("SELECT id, name, code FROM subjects ORDER BY id")
    subjects = cursor.fetchall()
    
    print(f"\nTotal subjects in database: {len(subjects)}")
    
    # Group by name (case-insensitive)
    subject_groups = defaultdict(list)
    for subject_id, name, code in subjects:
        key = name.lower().strip()
        subject_groups[key].append((subject_id, name, code))
    
    # Find duplicates
    duplicates_found = 0
    subjects_to_delete = []
    
    for name_key, group in subject_groups.items():
        if len(group) > 1:
            duplicates_found += 1
            print(f"\n❌ DUPLICATE: '{group[0][1]}'")
            print(f"   Found {len(group)} instances:")
            
            # Keep the first one, delete the rest
            keep_id = group[0][0]
            for i, (subject_id, name, code) in enumerate(group):
                if i == 0:
                    print(f"   ✅ KEEP: ID={subject_id}, Code={code}")
                else:
                    print(f"   🗑️  DELETE: ID={subject_id}, Code={code}")
                    subjects_to_delete.append(subject_id)
    
    if not subjects_to_delete:
        print("\n✅ No duplicate subjects found!")
        conn.close()
        return
    
    print(f"\n{'=' * 60}")
    print(f"Total duplicates to remove: {len(subjects_to_delete)}")
    print(f"{'=' * 60}")
    
    # Delete lessons associated with duplicate subjects first
    for subject_id in subjects_to_delete:
        cursor.execute("SELECT COUNT(*) FROM lessons WHERE subject_id = ?", (subject_id,))
        lesson_count = cursor.fetchone()[0]
        if lesson_count > 0:
            print(f"Deleting {lesson_count} lessons for subject ID {subject_id}")
            cursor.execute("DELETE FROM lessons WHERE subject_id = ?", (subject_id,))
    
    # Delete duplicate subjects
    for subject_id in subjects_to_delete:
        cursor.execute("DELETE FROM subjects WHERE id = ?", (subject_id,))
        print(f"✅ Deleted subject ID: {subject_id}")
    
    conn.commit()
    
    # Show final count
    cursor.execute("SELECT COUNT(*) FROM subjects")
    final_count = cursor.fetchone()[0]
    
    print(f"\n{'=' * 60}")
    print(f"CLEANUP COMPLETE!")
    print(f"{'=' * 60}")
    print(f"Subjects before: {len(subjects)}")
    print(f"Subjects after: {final_count}")
    print(f"Removed: {len(subjects_to_delete)} duplicates")
    
    # Show remaining subjects
    print(f"\n{'=' * 60}")
    print("REMAINING SUBJECTS:")
    print(f"{'=' * 60}")
    cursor.execute("SELECT id, name, code FROM subjects ORDER BY name")
    remaining = cursor.fetchall()
    for subject_id, name, code in remaining:
        print(f"  {subject_id:3d}. {name:40s} ({code})")
    
    conn.close()

if __name__ == "__main__":
    remove_duplicate_subjects()
