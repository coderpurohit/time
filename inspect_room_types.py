import sqlite3
import os
import sys

sys.path.append(os.path.abspath("backend"))

db_path = "backend/timetable.db"

def inspect():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("--- Subject Room Requirements ---")
    cursor.execute("SELECT name, is_lab, required_room_type FROM subjects")
    for s in cursor.fetchall():
        print(s)

    print("\n--- Room Types ---")
    cursor.execute("SELECT name, type, capacity FROM rooms")
    for r in cursor.fetchall():
        print(r)

    conn.close()

if __name__ == "__main__":
    inspect()
