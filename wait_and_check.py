import sys
sys.path.insert(0, 'backend')
import time

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///backend/timetable.db"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

from backend.app.infrastructure import models

print("Waiting for solver to complete...")
for i in range(10):
    time.sleep(2)
    db = Session()
    latest = db.query(models.TimetableVersion).order_by(models.TimetableVersion.id.desc()).first()
    if latest:
        entries = db.query(models.TimetableEntry).filter(models.TimetableEntry.version_id == latest.id).count()
        print(f"[{i*2}s] Status: {latest.status}, Entries: {entries}")
        
        if latest.status != 'processing':
            print(f"\nFinal status: {latest.status}")
            if entries > 0:
                print(f"✓ SUCCESS! Generated {entries} timetable entries")
            else:
                print("✗ Failed - no entries generated")
            db.close()
            break
    db.close()
