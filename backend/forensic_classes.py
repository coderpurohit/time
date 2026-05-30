
import sqlite3
import re

def forensic():
    conn = sqlite3.connect('timetable.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, name FROM class_groups")
    rows = cursor.fetchall()
    print(f"DB Class Table Count: {len(rows)}")
    for r in rows:
        print(f"  {r[1]}")
    
    # Check if there are unique class names in timetable_entries
    cursor.execute("SELECT DISTINCT class_group_id FROM timetable_entries")
    entry_cgids = cursor.fetchall()
    print(f"Unique Class IDs in TimetableEntries: {len(entry_cgids)}")
    
    # Check all subjects too
    cursor.execute("SELECT COUNT(*) FROM subjects")
    sc = cursor.fetchone()[0]
    print(f"Total Subjects: {sc}")
    
    # Check the analytics.py file for any shadow reassignments
    with open('app/api/routers/analytics.py', 'r') as f:
        content = f.read()
        assignments = re.findall(r'classes\s*=\s*.*', content)
        print(f"\nAssignments to 'classes' in analytics.py:")
        for a in assignments:
            print(f"  {a}")
            
    conn.close()

if __name__ == "__main__":
    forensic()
