#!/usr/bin/env python
"""
Reset database schema to match current models

This script:
1. Deletes all tables
2. Recreates all tables with current schema
3. Seeds default data (optional)
"""

import sys
sys.path.insert(0, '.')

from app.infrastructure.database import engine, SessionLocal
from app.infrastructure import models

print("=" * 70)
print("DATABASE SCHEMA RESET")
print("=" * 70)

# Drop all tables
print("\n1️⃣  Dropping existing tables...")
try:
    models.Base.metadata.drop_all(bind=engine)
    print("   ✅ Tables dropped")
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# Recreate all tables
print("\n2️⃣  Creating tables from current models...")
try:
    models.Base.metadata.create_all(bind=engine)
    print("   ✅ Tables created")
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# Create default schedule config
print("\n3️⃣  Creating default schedule configuration...")
try:
    db = SessionLocal()
    
    # Check if config exists
    existing = db.query(models.ScheduleConfig).first()
    if not existing:
        config = models.ScheduleConfig(
            day_start_time="09:00",
            day_end_time="17:00",
            working_minutes_per_day=480,  # 8 hours
            number_of_periods=8,
            period_duration_minutes=60,
            lunch_break_start="12:00",
            lunch_break_end="13:00",
            schedule_days=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        )
        db.add(config)
        db.commit()
        print("   ✅ Default configuration created")
    else:
        print("   ℹ️  Configuration already exists")
    
    db.close()
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

print("\n" + "=" * 70)
print("✅ DATABASE RESET COMPLETE")
print("=" * 70)
print("\nYou can now run: python backend/run_uvicorn.py")
