
import sqlite3

def inspect_entries():
    try:
        conn = sqlite3.connect('timetable.db')
        cursor = conn.cursor()
        
        # Check unique class_group_id in timetable_entries
        cursor.execute("""
            SELECT e.class_group_id, cg.name, COUNT(*) 
            FROM timetable_entries e
            LEFT JOIN class_groups cg ON e.class_group_id = cg.id
            GROUP BY e.class_group_id
        """)
        rows = cursor.fetchall()
        print(f"\n=== TIMETABLE ENTRIES CLASS DISTRIBUTION ===")
        for r in rows:
            print(f"ID: {r[0]}, Name: {r[1]}, Count: {r[2]}")
            
        conn.close()
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    inspect_entries()
