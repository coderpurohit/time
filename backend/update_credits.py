from app.infrastructure.database import SQLALCHEMY_DATABASE_URL
import os
import sys

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# Import from backend.app...
from app.infrastructure.models import Subject

# Fix DB URL for script execution
if "sqlite" in SQLALCHEMY_DATABASE_URL:
    # Assuming running from root, DB is in backend/timetable.db
    # But SQLALCHEMY_DATABASE_URL might be "sqlite:///./timetable.db"
    # We force absolute path
    db_path = os.path.join(os.getcwd(), "backend", "timetable.db")
    SQLALCHEMY_DATABASE_URL = f"sqlite:///{db_path}"

print(f"Using DB: {SQLALCHEMY_DATABASE_URL}")

# Direct connection to avoid import issues
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

print("🔧 Updating Credits for Strict Schedule...")

# 1. Update Lectures (Target 25 slots total)
# 1. Update Lectures (Target 20 slots total -> 4 credits each)
lecture_updates = {
    "Data Structures & Algorithms": 4,
    "Database Management Systems": 4,
    "Machine Learning": 4,
    "Web Development": 4,
    "Computer Networks": 4
}

for name, credits in lecture_updates.items():
    s = db.query(Subject).filter(Subject.name == name).first()
    if s:
        s.credits = credits
        print(f"Updated {name} to {credits} credits")

# 2. Update Labs (Target 10 slots total = 5 days)
# ML Lab: 3 sessions * 2 hrs = 6 credits
# CN Lab: 2 sessions * 2 hrs = 4 credits
lab_updates = {
    "Machine Learning Lab": 6,
    "Computer Networks Lab": 4
}

for name, credits in lab_updates.items():
    s = db.query(Subject).filter(Subject.name == name).first()
    if s:
        s.credits = credits
        print(f"Updated {name} to {credits} credits")

db.commit()
db.close()
print("✅ Credits updated successfully!")
