
import sqlite3

def inspect():
    try:
        conn = sqlite3.connect('timetable.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, name FROM class_groups")
        classes = cursor.fetchall()
        
        print(f"\n=== DATABASE CLASSES (Total: {len(classes)}) ===")
        for c in classes:
            print(f"ID: {c[0]}, Name: {c[1]}")
            
        cursor.execute("SELECT id, name FROM teachers")
        teachers = cursor.fetchall()
        print(f"\n=== DATABASE TEACHERS (Total: {len(teachers)}) ===")
        for t in teachers:
            print(f"ID: {t[0]}, Name: {t[1]}")
            
        conn.close()
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    inspect()
