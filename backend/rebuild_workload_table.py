"""
Rebuild the workload_overrides table without FK constraint on version_id.
This allows standalone overrides (NULL version_id) for DOCX uploads before timetable generation.
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "timetable.db")

def rebuild_workload_overrides():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='workload_overrides'")
    exists = cursor.fetchone()
    
    if exists:
        # Backup existing data
        cursor.execute("SELECT id, version_id, report_data, created_at FROM workload_overrides")
        rows = cursor.fetchall()
        print(f"Found {len(rows)} existing override(s)")
        
        # Drop old table
        cursor.execute("DROP TABLE workload_overrides")
        print("Dropped old workload_overrides table")
    else:
        rows = []
        print("No existing workload_overrides table")
    
    # Create new table WITHOUT FK constraint
    cursor.execute("""
        CREATE TABLE workload_overrides (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            version_id INTEGER UNIQUE,
            report_data JSON,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS ix_workload_overrides_version_id ON workload_overrides (version_id)")
    print("Created new workload_overrides table (no FK constraint)")
    
    # Restore data
    for row in rows:
        cursor.execute(
            "INSERT INTO workload_overrides (id, version_id, report_data, created_at) VALUES (?, ?, ?, ?)",
            row
        )
    if rows:
        print(f"Restored {len(rows)} existing override(s)")
    
    conn.commit()
    conn.close()
    print("Done!")

if __name__ == "__main__":
    rebuild_workload_overrides()
