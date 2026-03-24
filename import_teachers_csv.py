"""
Import Teachers from CSV - Direct Database Method
Bypasses the API completely
"""

import sqlite3
import csv
import sys

DB_PATH = 'backend/timetable.db'

def import_teachers(csv_file, clear_existing=False):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if clear_existing:
        print("⚠️  Clearing existing teachers...")
        
        # Clear timetable first
        cursor.execute("DELETE FROM timetable_entries")
        cursor.execute("DELETE FROM timetable_versions")
        
        # Clear lessons and associations
        cursor.execute("DELETE FROM lesson_teachers")
        cursor.execute("DELETE FROM lesson_class_groups")
        cursor.execute("DELETE FROM lesson_subjects")
        cursor.execute("DELETE FROM lessons")
        
        # Clear subject-teacher associations
        cursor.execute("UPDATE subjects SET teacher_id = NULL")
        
        # Clear substitutions
        cursor.execute("DELETE FROM substitutions")
        
        # Delete teachers
        cursor.execute("DELETE FROM teachers")
        conn.commit()
        print("✅ Cleared all existing teachers")
    
    # Read CSV
    added = 0
    updated = 0
    errors = []
    
    with open(csv_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        
        # Normalize headers
        reader.fieldnames = [h.lower().strip() for h in reader.fieldnames]
        
        print(f"\nCSV Headers: {reader.fieldnames}")
        
        for idx, row in enumerate(reader, start=2):
            name = row.get('name', '').strip()
            email = row.get('email', '').strip()
            max_hours = row.get('max_hours_per_week', '18').strip()
            
            if not name:
                errors.append(f"Row {idx}: Missing name")
                continue
            
            # Auto-generate email if missing
            if not email:
                email = name.lower().replace(' ', '.').replace('dr.', '').replace('prof.', '').strip() + '@college.edu'
            
            try:
                max_hours = int(max_hours) if max_hours else 18
            except:
                max_hours = 18
            
            # Check if exists
            cursor.execute("SELECT id FROM teachers WHERE email = ?", (email,))
            existing = cursor.fetchone()
            
            if existing:
                # Update
                cursor.execute("""
                    UPDATE teachers 
                    SET name = ?, max_hours_per_week = ?
                    WHERE email = ?
                """, (name, max_hours, email))
                updated += 1
            else:
                # Insert
                cursor.execute("""
                    INSERT INTO teachers (name, email, max_hours_per_week)
                    VALUES (?, ?, ?)
                """, (name, email, max_hours))
                added += 1
    
    conn.commit()
    conn.close()
    
    print(f"\n{'='*60}")
    print(f"IMPORT COMPLETE!")
    print(f"{'='*60}")
    print(f"Added: {added}")
    print(f"Updated: {updated}")
    if errors:
        print(f"\nErrors:")
        for err in errors[:10]:
            print(f"  - {err}")
    print(f"{'='*60}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python import_teachers_csv.py <csv_file> [--clear]")
        print("\nExample:")
        print("  python import_teachers_csv.py teachers.csv")
        print("  python import_teachers_csv.py teachers.csv --clear")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    clear = '--clear' in sys.argv
    
    if clear:
        confirm = input("⚠️  This will DELETE all existing teachers! Type 'yes' to continue: ")
        if confirm.lower() != 'yes':
            print("Cancelled.")
            sys.exit(0)
    
    import_teachers(csv_file, clear)
