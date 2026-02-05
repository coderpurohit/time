
import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_operational_flow():
    print("\n--- Testing Operational Features ---")

    # 1. Test Holidays
    print("\n1. Creating Holiday...")
    h_payload = {"date": "2026-08-15", "name": "Independence Day"}
    r = requests.post(f"{BASE_URL}/operational/holidays/", json=h_payload)
    if r.status_code == 200:
        print(f"✅ Created Holiday: {r.json()['name']}")
    else:
        print(f"❌ Failed to create holiday: {r.text}")

    # 2. Test Marking Teacher Absent
    # Dynamically find a teacher with a class on Monday
    print("\n2. Finding a teacher with classes on Monday...")
    # This is a bit of a hack for the test script to be self-contained
    # In a real test we'd import the DB, but here we'll just try IDs or rely on seed
    teacher_id = 3 # Based on manual check, but let's make it more robust in the next step
    
    date = "2026-02-09" # Monday
    print(f"   Marking Teacher ID {teacher_id} Absent for {date}...")
    r = requests.post(f"{BASE_URL}/operational/absent/?teacher_id={teacher_id}&date={date}")

    if r.status_code == 200:
        subs = r.json()
        print(f"✅ Created {len(subs)} substitution requests.")
        if subs:
            sub_id = subs[0]['id']
            print(f"   First Substitution ID: {sub_id}")
            
            # 3. Test Finding Substitutes
            print(f"\n3. Finding available substitutes for Substitution ID {sub_id}...")
            r = requests.get(f"{BASE_URL}/operational/substitutes/available/{sub_id}")
            if r.status_code == 200:
                available = r.json()
                print(f"✅ Found {len(available)} available teachers.")
                if available:
                    sub_teacher_id = available[0]['id']
                    print(f"   Suggesting Teacher ID: {sub_teacher_id} ({available[0]['name']})")
                    
                    # 4. Assign Substitute
                    print(f"\n4. Assigning Teacher ID {sub_teacher_id} as substitute...")
                    r = requests.post(f"{BASE_URL}/operational/substitutes/assign/{sub_id}?substitute_teacher_id={sub_teacher_id}")
                    if r.status_code == 200:
                        print("✅ Substitute assigned successfully!")
                    else:
                        print(f"❌ Assignment failed: {r.text}")
            else:
                print(f"❌ Failed to find substitutes: {r.text}")
    else:
        print(f"❌ Failed to mark absent: {r.text}")

if __name__ == "__main__":
    test_operational_flow()
