
import sqlite3

def inspect():
    try:
        conn = sqlite3.connect('timetable.db')
        cur = conn.cursor()
        
        print("\n=== CLASS GROUPS ===")
        cur.execute("SELECT id, name FROM class_groups")
        for row in cur.fetchall():
            print(f"ID={row[0]}, NAME='{row[1]}'")
            
        print("\n=== SUBJECTS ===")
        cur.execute("SELECT id, name FROM subjects")
        for row in cur.fetchall():
            print(f"ID={row[0]}, NAME='{row[1]}'")
            
        print("\n=== TEACHERS (First 5) ===")
        cur.execute("SELECT id, name FROM teachers LIMIT 5")
        for row in cur.fetchall():
            print(f"ID={row[0]}, NAME='{row[1]}'")
            
        conn.close()
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    inspect()
