
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.infrastructure import models
from app.infrastructure.database import SQLALCHEMY_DATABASE_URL

def seed_data():
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    print("Seeding Reference Data...")

    # 1. Time Slots (Mon-Fri, 9-5)
    existing_slots = db.query(models.TimeSlot).count()
    if existing_slots == 0:
        print("  - Adding TimeSlots...")
        slots = []
        for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
            for i in range(1, 9): # 8 periods
                slots.append(models.TimeSlot(
                    day=day, 
                    period=i, 
                    start_time=f"{8+i}:00", 
                    end_time=f"{9+i}:00",
                    is_break=(i==4) # Lunch break at period 4
                ))
        db.add_all(slots)
        db.commit()
    else:
        print(f"  - TimeSlots exist ({existing_slots})")

    # 2. Class Groups
    existing_groups = db.query(models.ClassGroup).count()
    if existing_groups == 0:
        print("  - Adding ClassGroups...")
        groups = [
            models.ClassGroup(name="SE-AI-DS-A", student_count=60),
            models.ClassGroup(name="SE-AI-DS-B", student_count=60),
            models.ClassGroup(name="TE-AI-DS-A", student_count=50)
        ]
        db.add_all(groups)
        db.commit()
    else:
        print(f"  - ClassGroups exist ({existing_groups})")

    db.close()
    print("Seed Complete.")

if __name__ == "__main__":
    seed_data()
