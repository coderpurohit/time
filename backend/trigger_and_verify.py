
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def trigger_generation():
    print(f"Triggering generation via {BASE_URL}/api/solvers/generate?method=csp ...")
    try:
        resp = requests.post(f"{BASE_URL}/api/solvers/generate?method=csp")
        if resp.status_code == 200:
            data = resp.json()
            print(f"Success! New Timetable Version ID: {data.get('id')}")
            return data.get('id')
        else:
            print(f"FAILED: {resp.status_code} - {resp.text}")
            return None
    except Exception as e:
        print(f"Error connecting to server: {e}")
        return None

def verify_results(version_id):
    if not version_id:
        return
    
    print(f"\nVerifying Version {version_id}...")
    
    # Use absolute path for DB to avoid path issues
    import os
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    db_path = os.path.abspath("timetable.db")
    print(f"Connecting to DB at: {db_path}")
    
    engine = create_engine(f"sqlite:///{db_path}")
    SessionLocal = sessionmaker(bind=engine)
    
    from app.infrastructure import models
    
    db = SessionLocal()
    version = db.query(models.TimetableVersion).filter(models.TimetableVersion.id == version_id).first()
    
    if not version:
        print("Error: Version not found in DB")
        return

    entries = version.entries
    print(f"Found {len(entries)} entries.")

    # 1. Check for Forbidden Subjects
    FORBIDDEN_RULES = {
        "Kottawar": ["Professional and Technical Communication", "PTC"],
        "Sharma": ["Sustainable Development", "Energy"],
        "Gothane": ["Engineering Physics"]
    }
    
    total_forbidden = 0
    for e in entries:
        t_name = e.teacher.name if e.teacher else ""
        s_name = e.subject.name if e.subject else ""
        for t_key, fs_list in FORBIDDEN_RULES.items():
            if t_key.lower() in t_name.lower():
                if any(fs.lower() in s_name.lower() for fs in fs_list):
                    print(f"FAILURE: Found {s_name} for {t_name} at Slot {e.time_slot_id}")
                    total_forbidden += 1
    
    if total_forbidden == 0:
        print("PASSED: No forbidden subjects for target teachers.")
    else:
        print(f"FAILED: Found {total_forbidden} forbidden assignments.")

    # 2. Check for Consecutive Same-Subject Blocks
    # group_id -> day -> list of (period, subject_id)
    schedule = {}
    from collections import defaultdict
    group_day_map = defaultdict(lambda: defaultdict(list))
    
    for e in entries:
        slot = e.time_slot
        group_id = e.class_group_id
        group_day_map[group_id][slot.day].append((slot.period, e.subject_id, e.subject.name))
        
    consecutive_violations = 0
    for gid, days in group_day_map.items():
        for day, periods in days.items():
            sorted_p = sorted(periods, key=lambda x: x[0])
            for i in range(len(sorted_p) - 1):
                p1 = sorted_p[i]
                p2 = sorted_p[i+1]
                # If they are consecutive periods AND same subject
                if p2[0] == p1[0] + 1 and p2[1] == p1[1]:
                    # Check if it's a lab (many labs are 2 slots, which is NORMAL)
                    # We only alert if it's NOT a lab (actually, the user said "3 lectures continues")
                    # But the solver C7 should prevent even 2 for theory.
                    # Wait! If it's a lab, it SHOULD be 2.
                    # Let's count how many are in a row.
                    
                    # Search for 3 in a row
                    if i < len(sorted_p) - 2:
                        p3 = sorted_p[i+2]
                        if p3[0] == p2[0] + 1 and p3[1] == p2[1]:
                            print(f"FAILURE: 3 consecutive {p1[2]} for Group {gid} on {day} slots {p1[0]}-{p3[0]}")
                            consecutive_violations += 1
    
    if consecutive_violations == 0:
        print("PASSED: No 3-consecutive theory blocks found.")
    else:
        print(f"FAILED: Found {consecutive_violations} consecutive violations.")

    db.close()

if __name__ == "__main__":
    new_id = trigger_generation()
    if new_id:
        # Give a moment for DB commit if needed (though it should be immediate)
        time.sleep(1)
        verify_results(new_id)
