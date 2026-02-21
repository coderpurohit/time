import requests
import time
import sys

BASE_URL = "http://localhost:8000"

def trigger_generation():
    print("🚀 Triggering timetable generation...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/solvers/generate",
            json={"algorithm": "csp", "name": "Lab Update Verification"}
        )
        if response.status_code == 200:
            print("✅ Generation triggered successfully!")
            return True
        else:
            print(f"❌ Generation failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

def verify_labs():
    print("\n🔍 Verifying lab scheduling...")
    # Wait a bit for generation
    time.sleep(2)
    
    try:
        response = requests.get(f"{BASE_URL}/api/timetables/latest")
        if response.status_code != 200:
            print(f"❌ Failed to fetch timetable: {response.status_code}")
            return

        data = response.json()
        entries = data.get("entries", [])
        
        lab_subjects = ["Computer Networks Lab", "Machine Learning Lab"]
        lab_entries = [e for e in entries if e["subject"]["name"] in lab_subjects]
        
        if not lab_entries:
            print("❌ No lab entries found! Scheduling might have failed to assign them.")
            return

        all_correct = True
        for entry in lab_entries:
            subject = entry["subject"]["name"]
            period = entry["time_slot"]["period"]
            day = entry["time_slot"]["day"]
            
            print(f"  - {subject} on {day} Period {period}")
            
            if period <= 4:
                print(f"    ❌ VIOLATION: {subject} scheduled before/during lunch (Period {period})")
                all_correct = False
            else:
                print(f"    ✅ Correct (Afternoon)")

        if all_correct:
            print("\n🎉 All labs are correctly scheduled after lunch!")
        else:
            print("\n⚠️ Some labs are misplaced.")

    except Exception as e:
        print(f"❌ Verification failed: {e}")

if __name__ == "__main__":
    if trigger_generation():
        # Wait loop to ensure it's finished? 
        # The API is synchronous for CSP usually, or returns quickly if async. 
        # Let's assume it blocks or finishes quickly for demo data.
        time.sleep(5) 
        verify_labs()
