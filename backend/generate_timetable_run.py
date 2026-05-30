
import sys
import os

# Add project paths
sys.path.insert(0, os.path.dirname(__file__))
from app.infrastructure.database import SessionLocal
from app.services.timetable_service import TimetableService

def generate():
    db = SessionLocal()
    try:
        print("--- GENERATING TIMETABLE ---")
        version = TimetableService.generate_and_save(db, method="csp", version_name="Persistent Fixed Timetable")
        print(f"Generated Version ID: {version.id}, Status: {version.status}")
        
    finally:
        db.close()

if __name__ == "__main__":
    generate()
