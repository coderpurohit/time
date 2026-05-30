
import os
import sys

# Add the project root to sys.path
sys.path.append(os.getcwd())

from app.infrastructure.database import SessionLocal
from app.services.timetable_service import TimetableService

def trace():
    db = SessionLocal()
    try:
        print("Tracing Timetable Generation...")
        version = TimetableService.generate_and_save(db, method="csp", version_name="Trace Version")
        print(f"Generation Result: ID={version.id}, Status={version.status}")
        
        # Check entries count
        entries_count = len(version.entries)
        print(f"Entries generated: {entries_count}")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    trace()
