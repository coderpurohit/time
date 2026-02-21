import sqlite3
import json
import os
import sys

# Add backend directory to path
sys.path.append(os.path.abspath("backend"))

db_path = "backend/timetable.db"

def export_json():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get latest version ID
    cursor.execute("SELECT id FROM timetable_versions ORDER BY created_at DESC LIMIT 1")
    version_id = cursor.fetchone()[0]

    # Get Class Group ID for SE-AI-DS-A
    cursor.execute("SELECT id FROM class_groups WHERE name='SE-AI-DS-A'")
    group_id = cursor.fetchone()[0]

    # Fetch entries
    query = """
    SELECT 
        ts.day,
        ts.period,
        ts.start_time,
        ts.end_time,
        s.name as subject,
        t.name as faculty,
        r.name as room,
        s.is_lab
    FROM timetable_entries te
    JOIN time_slots ts ON te.time_slot_id = ts.id
    JOIN subjects s ON te.subject_id = s.id
    JOIN teachers t ON te.teacher_id = t.id
    JOIN rooms r ON te.room_id = r.id
    WHERE te.version_id = ? AND te.class_group_id = ?
    ORDER BY ts.id
    """
    
    cursor.execute(query, (version_id, group_id))
    rows = cursor.fetchall()
    
    timetable = []
    for r in rows:
        entry = {
            "day": r[0],
            "time_slot": f"{r[2]} - {r[3]}",
            "subject": r[4],
            "faculty": r[5],
            "room": r[6],
            "type": "Lab" if r[7] else "Lecture"
        }
        timetable.append(entry)

    print(json.dumps(timetable, indent=2))
    conn.close()

if __name__ == "__main__":
    export_json()
