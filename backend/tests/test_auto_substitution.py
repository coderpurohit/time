"""
Test script for automated teacher substitution system
Tests the auto-assignment functionality with existing database
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def print_section(title):
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}\n")

def test_auto_assignment():
    """Test the auto-assignment endpoint"""
    
    print_section("AUTOMATED TEACHER SUBSTITUTION TEST")
    
    # Step 1: Check if backend is running and get teachers
    print("1️⃣  Fetching all teachers...")
    try:
        response = requests.get(f"{BASE_URL}/api/teachers/")
        response.raise_for_status()
        teachers = response.json()
        
        if not teachers:
            print("❌ No teachers found in database. Please run setup_database.py first.")
            return
        
        print(f"✅ Found {len(teachers)} teachers:")
        for teacher in teachers:
            print(f"   - ID {teacher['id']}: {teacher['name']} ({teacher['email']})")
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend. Please start the server:")
        print("   uvicorn app.main:app --reload")
        return
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # Step 2: Get timetable to verify data exists
    print("\n2️⃣  Checking timetable...")
    try:
        response = requests.get(f"{BASE_URL}/api/timetables/")
        timetables = response.json()
        
        if not timetables:
            print("❌ No timetables found. Please generate a timetable first.")
            print("   POST /api/solvers/generate")
            return
        
        print(f"✅ Found {len(timetables)} timetable(s)")
        latest = timetables[0]
        print(f"   Latest: {latest['name']} ({latest['algorithm']}) - {len(latest.get('entries', []))} entries")
        
    except Exception as e:
        print(f"❌ Error checking timetable: {e}")
        return
    
    # Step 3: Test auto-assignment
    # Use the first teacher for testing
    test_teacher_id = teachers[0]['id']
    test_date = "2026-02-05"
    
    print(f"\n3️⃣  Testing AUTO-ASSIGNMENT for Teacher ID {test_teacher_id}...")
    print(f"   Absent Teacher: {teachers[0]['name']}")
    print(f"   Date: {test_date}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/substitutions/auto-assign",
            params={
                "teacher_id": test_teacher_id,
                "date": test_date,
                "auto_notify": False
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print("\n🎉 AUTO-ASSIGNMENT SUCCESSFUL!")
            print(f"\n📊 Summary:")
            print(f"   Absent Teacher: {result.get('teacher_name')}")
            print(f"   Date: {result.get('date')}")
            print(f"   Affected Classes: {result.get('affected_classes')}")
            
            if result.get('substitute_assigned'):
                print(f"\n✅ Substitute Assigned: {result.get('substitute_assigned')}")
                print(f"   Confidence Score: {result.get('confidence_score'):.1f}/230")
                
                breakdown = result.get('score_breakdown', {})
                print(f"\n   Score Breakdown:")
                print(f"      • Availability: {breakdown.get('availability', 0):.1f}/100")
                print(f"      • Subject Expertise: {breakdown.get('subject_expertise', 0):.1f}/80")
                print(f"      • Workload Balance: {breakdown.get('workload_balance', 0):.1f}/50")
                
                print(f"\n📚 Classes Assigned:")
                for i, assignment in enumerate(result.get('assignments', []), 1):
                    print(f"   {i}. {assignment['subject']}")
                    print(f"      Time: {assignment['time_slot']}")
                    print(f"      Class: {assignment['class_group']} in {assignment['room']}")
                
                # Show alternatives
                alternatives = result.get('alternative_substitutes', [])
                if alternatives:
                    print(f"\n🔄 Alternative Substitutes:")
                    for i, alt in enumerate(alternatives[:3], 1):
                        print(f"   {i}. {alt['teacher_name']} - Score: {alt.get('score', 0):.1f}")
            else:
                print(f"\n❌ No substitute found")
                print(f"   Reason: {result.get('reason', 'Unknown')}")
        
        elif response.status_code == 404:
            error = response.json()
            print(f"\n❌ Error 404: {error.get('detail')}")
        else:
            print(f"\n❌ Error {response.status_code}: {response.text}")
        
    except Exception as e:
        print(f"❌ Error during auto-assignment: {e}")
        return
    
    # Step 4: Test ranked suggestions
    print(f"\n4️⃣  Testing RANKED SUGGESTIONS...")
    
    if latest.get('entries'):
        test_entry_id = latest['entries'][0]['id']
        
        try:
            response = requests.get(
                f"{BASE_URL}/api/substitutions/suggestions/{test_entry_id}/ranked",
                params={"top_n": 5}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"\n✅ Found {result.get('total_suggestions', 0)} suggestions for entry {test_entry_id}:")
                
                for i, sub in enumerate(result.get('ranked_substitutes', [])[:5], 1):
                    status = "✅ Available" if sub.get('available') else "❌ Busy"
                    expertise = "🎯 Expert" if sub.get('teaches_same_subject') else "📚 Other"
                    
                    print(f"\n   {i}. {sub.get('teacher_name')} - Score: {sub.get('score', 0):.1f}")
                    print(f"      {status} | {expertise}")
                    
                    if sub.get('available'):
                        print(f"      Workload: {sub.get('current_workload', 0)} classes")
            else:
                print(f"❌ Error: {response.status_code}")
        
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Step 5: Test bulk auto-assignment
    print(f"\n5️⃣  Testing BULK AUTO-ASSIGNMENT...")
    
    if len(teachers) >= 2:
        bulk_absences = [
            {"teacher_id": teachers[0]['id'], "date": "2026-02-06"},
            {"teacher_id": teachers[1]['id'], "date": "2026-02-06"}
        ]
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/substitutions/auto-assign-bulk",
                json={
                    "absences": bulk_absences,
                    "auto_notify": False
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"\n✅ Bulk Assignment Complete!")
                print(f"   Total Absences: {result.get('total_absences_processed')}")
                print(f"   Successful: {result.get('successful_assignments')}")
                print(f"   Failed: {result.get('failed_assignments')}")
                print(f"   Total Classes: {result.get('total_classes_affected')}")
            else:
                print(f"❌ Error: {response.status_code}")
        
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "="*60)
    print(" TEST COMPLETE ✅")
    print("="*60)

if __name__ == "__main__":
    test_auto_assignment()
