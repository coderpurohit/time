import sqlite3
import os
import sys

# Ensure backend directory is in path
sys.path.append(os.path.abspath("backend"))

db_path = "backend/timetable.db"

def inspect():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("--- Time Slots ---")
    cursor.execute("SELECT id, day, start_time, end_time FROM time_slots ORDER BY id")
    slots = cursor.fetchall()
    for s in slots:
        print(s)
    print(f"Total Slots: {len(slots)}")
    
    # Check slots per day
    days = set(s[1] for s in slots)
    print(f"Days: {days}")
    for d in days:
        day_slots = [s for s in slots if s[1] == d]
        print(f"Slots for {d}: {len(day_slots)}")

    print("\n--- Subjects ---")
    cursor.execute("SELECT id, name, credits, is_lab FROM subjects")
    subjects = cursor.fetchall()
    for s in subjects:
        print(s)

    print("\n--- Target Group ---")
    cursor.execute("SELECT id, name FROM class_groups WHERE name='SE-AI-DS-A'")
    print(cursor.fetchall())

    print("\n--- Teachers ---")
    cursor.execute("SELECT COUNT(*) FROM teachers")
    print(f"Teacher Count: {cursor.fetchone()[0]}")

    print("\n--- Rooms ---")
    cursor.execute("SELECT COUNT(*) FROM rooms")
    print(f"Room Count: {cursor.fetchone()[0]}")

    conn.close()

if __name__ == "__main__":
    inspect()
