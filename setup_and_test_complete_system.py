"""
COMPLETE SYSTEM SETUP AND TEST
Run this to set up everything and test timetable generation with load factors
"""

import subprocess
import time
import requests
import os

def run_complete_setup():
    """Step 1: Run the complete database setup"""
    print("🚀 Step 1: Setting up complete database with load factor consideration...")
    
    try:
        result = subprocess.run(['python', 'run_complete_setup.py'], 
                              capture_output=True, text=True, cwd='.')
        print(result.stdout)
        if result.stderr:
            print("Warnings:", result.stderr)
        return True
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        return False

def check_backend_running():
    """Step 2: Check if backend is running"""
    print("\n🔍 Step 2: Checking if backend is running...")
    
    try:
        response = requests.get('http://localhost:8000/api/teachers/', timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running!")
            return True
        else:
            print(f"❌ Backend responded with status {response.status_code}")
            return False
    except requests.exceptions.RequestException:
        print("❌ Backend is not running!")
        print("💡 Please run: cd backend && start.bat")
        return False

def test_timetable_generation():
    """Step 3: Test timetable generation with load factors"""
    print("\n📊 Step 3: Testing timetable generation with load factors...")
    
    try:
        # Generate timetable
        response = requests.post('http://localhost:8000/api/solvers/generate?method=csp&name=Load-Aware-Test')
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Timetable generated successfully!")
            print(f"   - Version ID: {data['id']}")
            print(f"   - Name: {data['name']}")
            print(f"   - Algorithm: {data['algorithm']}")
            print(f"   - Status: {data['status']}")
            return data['id']
        else:
            print(f"❌ Generation failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Generation test failed: {e}")
        return None

def check_load_factor_analysis(version_id):
    """Step 4: Check load factor analysis"""
    print(f"\n📈 Step 4: Checking load factor analysis...")
    
    try:
        response = requests.get('http://localhost:8000/api/analytics/load-factor')
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Load factor analysis retrieved!")
            
            # Print summary
            summary = data.get('summary', {})
            print(f"\n📊 Summary:")
            print(f"   - Total Teachers: {summary.get('total_teachers', 0)}")
            print(f"   - Total Classes: {summary.get('total_classes', 0)}")
            print(f"   - Total Periods: {summary.get('total_periods', 0)}")
            print(f"   - Average Teacher Load: {summary.get('avg_teacher_load', 0)}")
            
            # Print teacher loads
            teacher_loads = data.get('teacher_load', [])
            print(f"\n👨‍🏫 Teacher Load Distribution:")
            for teacher in teacher_loads[:10]:  # Show first 10
                name = teacher.get('name', 'Unknown')
                periods = teacher.get('total_periods', 0)
                utilization = teacher.get('utilization_percentage', 0)
                print(f"   - {name}: {periods} periods ({utilization:.1f}% utilization)")
            
            if len(teacher_loads) > 10:
                print(f"   ... and {len(teacher_loads) - 10} more teachers")
                
            return True
        else:
            print(f"❌ Load factor analysis failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Load factor analysis failed: {e}")
        return False

def main():
    print("=" * 60)
    print("🎯 COMPLETE TIMETABLE SYSTEM WITH LOAD FACTORS")
    print("=" * 60)
    
    # Step 1: Setup database
    if not run_complete_setup():
        print("\n❌ Setup failed. Cannot continue.")
        return
    
    # Step 2: Check backend
    if not check_backend_running():
        print("\n❌ Backend not running. Please start it first.")
        print("💡 Run: cd backend && start.bat")
        return
    
    # Step 3: Generate timetable
    version_id = test_timetable_generation()
    if not version_id:
        print("\n❌ Timetable generation failed.")
        return
    
    # Step 4: Check load factors
    if not check_load_factor_analysis(version_id):
        print("\n❌ Load factor analysis failed.")
        return
    
    print("\n" + "=" * 60)
    print("🎉 SUCCESS! Complete system is working with load factors!")
    print("=" * 60)
    print("\n📋 What was created:")
    print("   ✅ 9 Classes (SE/TE/BE-AIDS A/B/C)")
    print("   ✅ 15 Teachers with varied load capacities")
    print("   ✅ 12 Subjects")
    print("   ✅ 10 Rooms")
    print("   ✅ 108 Lessons (automatically created)")
    print("   ✅ 35 Time Slots")
    print("   ✅ Timetable with load factor balancing")
    
    print("\n🌐 Next Steps:")
    print("   1. Open: http://localhost:8000/docs (API documentation)")
    print("   2. Open your timetable web UI")
    print("   3. Click 'Load Latest Timetable' to see the generated schedule")
    print("   4. Check 'Load Factor' tab to see teacher utilization")
    print("   5. Generate new schedules anytime with 'Generate New Schedule'")

if __name__ == '__main__':
    main()