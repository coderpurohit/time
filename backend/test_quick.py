"""
Quick Test Guide for Automated Teacher Substitution
Run this script to test all auto-assignment features
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_auto_substitution():
    print("=" * 70)
    print(" TESTING AUTOMATED TEACHER SUBSTITUTION SYSTEM")
    print("=" * 70)
    
    # Step 1: Check server health
    print("\n✅ STEP 1: Checking server health...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        health = response.json()
        print(f"   Status: {health['status']}")
        print(f"   Database: {health['database']}")
        print(f"   Teachers in DB: {health['teachers']}")
        print(f"   Timetables: {health['timetables']}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        print("   Make sure backend is running!")
        return
    
    # Step 2: Get list of teachers
    print("\n✅ STEP 2: Fetching teachers...")
    try:
        response = requests.get(f"{BASE_URL}/api/teachers/")
        teachers = response.json()
        print(f"   Found {len(teachers)} teachers:")
        for t in teachers[:3]:
            print(f"      • ID {t['id']}: {t['name']}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # Step 3: Generate a timetable if needed
    print("\n✅ STEP 3: Checking/Generating timetable...")
    try:
        response = requests.get(f"{BASE_URL}/api/timetables/")
        timetables = response.json()
        
        if not timetables:
            print("   No timetable found. Generating one...")
            response = requests.post(
                f"{BASE_URL}/api/solvers/generate",
                json={
                    "algorithm": "csp",
                    "class_groups": [1, 2, 3]
                }
            )
            if response.status_code == 200:
                print("   ✓ Timetable generated successfully!")
            else:
                print(f"   ⚠️  Generation returned {response.status_code}")
        else:
            print(f"   ✓ Timetable exists: {timetables[0]['name']}")
            print(f"      Entries: {len(timetables[0].get('entries', []))}")
    except Exception as e:
        print(f"   ⚠️  {e}")
    
    # Step 4: Test AUTO-ASSIGNMENT
    print("\n" + "=" * 70)
    print(" 🤖 TESTING AUTO-ASSIGNMENT")
    print("=" * 70)
    
    teacher_id = 1
    test_date = "2026-02-05"
    
    print(f"\n📍 Scenario: Teacher ID {teacher_id} is absent on {test_date}")
    print("   Let's auto-assign a substitute...\n")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/substitutions/auto-assign",
            params={
                "teacher_id": teacher_id,
                "date": test_date,
                "auto_notify": False
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print("🎉 AUTO-ASSIGNMENT SUCCESS!\n")
            print(f"📊 Summary:")
            print(f"   Absent Teacher: {result.get('teacher_name')}")
            print(f"   Date: {result.get('date')}")
            print(f"   Classes Affected: {result.get('affected_classes')}")
            
            if result.get('substitute_assigned'):
                print(f"\n✅ SUBSTITUTE ASSIGNED: {result.get('substitute_assigned')}")
                print(f"   Confidence Score: {result.get('confidence_score'):.1f}/230")
                
                breakdown = result.get('score_breakdown', {})
                print(f"\n   📈 Score Breakdown:")
                print(f"      Availability:      {breakdown.get('availability', 0):.0f}/100")
                print(f"      Subject Expertise: {breakdown.get('subject_expertise', 0):.0f}/80")
                print(f"      Workload Balance:  {breakdown.get('workload_balance', 0):.0f}/50")
                
                print(f"\n   📚 Classes Assigned:")
                for i, assignment in enumerate(result.get('assignments', [])[:3], 1):
                    print(f"      {i}. {assignment['subject']}")
                    print(f"         Time: {assignment['time_slot']}")
                    print(f"         Class: {assignment['class_group']} @ {assignment['room']}")
                
                # Show alternatives
                alternatives = result.get('alternative_substitutes', [])
                if alternatives:
                    print(f"\n   🔄 Top Alternatives:")
                    for i, alt in enumerate(alternatives[:2], 1):
                        avail = "✅" if alt.get('available') else "❌"
                        print(f"      {i}. {alt['teacher_name']:<20} Score: {alt.get('score', 0):.0f} {avail}")
            else:
                print(f"\n❌ No substitute available")
                print(f"   Reason: {result.get('reason')}")
        
        elif response.status_code == 404:
            error = response.json()
            print(f"❌ Error 404: {error.get('detail')}")
            print("\n💡 TIP: Generate a timetable first:")
            print("   POST /api/solvers/generate")
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
    
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Step 5: Test RANKED SUGGESTIONS
    print("\n" + "=" * 70)
    print(" 🎯 TESTING RANKED SUGGESTIONS")
    print("=" * 70)
    
    try:
        # Get a timetable entry to test with
        response = requests.get(f"{BASE_URL}/api/timetables/")
        timetables = response.json()
        
        if timetables and timetables[0].get('entries'):
            entry_id = timetables[0]['entries'][0]['id']
            
            print(f"\n📍 Getting ranked suggestions for entry ID {entry_id}...\n")
            
            response = requests.get(
                f"{BASE_URL}/api/substitutions/suggestions/{entry_id}/ranked",
                params={"top_n": 5}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Found {result.get('total_suggestions', 0)} suggestions:\n")
                
                for i, sub in enumerate(result.get('ranked_substitutes', [])[:5], 1):
                    status = "✅ Available" if sub.get('available') else "❌ Busy"
                    expertise = "🎯 Subject Expert" if sub.get('teaches_same_subject') else "📚 Other Subject"
                    
                    print(f"   {i}. {sub.get('teacher_name'):<20} Score: {sub.get('score', 0):>6.1f}")
                    print(f"      {status} | {expertise}")
                    if sub.get('available'):
                        print(f"      Current Workload: {sub.get('current_workload', 0)} classes")
                    else:
                        print(f"      Reason: {sub.get('reason', 'Conflict')}")
                    print()
    except Exception as e:
        print(f"   ⚠️  {e}")
    
    # Step 6: Test BULK AUTO-ASSIGNMENT
    print("\n" + "=" * 70)
    print(" 🚀 TESTING BULK AUTO-ASSIGNMENT")
    print("=" * 70)
    
    if len(teachers) >= 2:
        print(f"\n📍 Scenario: Multiple teachers absent on same day\n")
        
        bulk_absences = [
            {"teacher_id": teachers[0]['id'], "date": "2026-02-06"},
            {"teacher_id": teachers[1]['id'], "date": "2026-02-06"}
        ]
        
        print(f"   Teacher 1: {teachers[0]['name']}")
        print(f"   Teacher 2: {teachers[1]['name']}")
        print(f"   Date: 2026-02-06\n")
        
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
                print("✅ BULK ASSIGNMENT COMPLETE!\n")
                print(f"   Total Absences Processed: {result.get('total_absences_processed')}")
                print(f"   Successful Assignments: {result.get('successful_assignments')}")
                print(f"   Failed Assignments: {result.get('failed_assignments')}")
                print(f"   Total Classes Affected: {result.get('total_classes_affected')}")
            else:
                print(f"   ❌ Error: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 70)
    print(" ✅ ALL TESTS COMPLETE!")
    print("=" * 70)
    print("\n💡 Next Steps:")
    print("   • Visit http://localhost:8000/docs for interactive API testing")
    print("   • Try different teacher IDs and dates")
    print("   • Check /api/substitutions/by-date/{date} to view all substitutions")
    print()

if __name__ == "__main__":
    test_auto_substitution()
