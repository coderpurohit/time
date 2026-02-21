"""
Quick Demo Runner
This script:
1. Seeds the database with demo data
2. Generates a timetable
3. Provides instructions to view the result
"""
import requests
import time

API_BASE_URL = 'http://localhost:8000'

def check_backend():
    """Check if backend is running"""
    try:
        response = requests.get(f'{API_BASE_URL}/health', timeout=5)
        if response.ok:
            data = response.json()
            print(f"✅ Backend is running")
            print(f"   - Teachers: {data.get('teachers', 0)}")
            print(f"   - Timetables: {data.get('timetables', 0)}")
            return True
    except requests.exceptions.ConnectionError:
        print("❌ Backend is not running")
        print("   Please start the backend first using:")
        print("   cd backend && .\\start.bat")
        return False
    except Exception as e:
        print(f"❌ Error checking backend: {e}")
        return False

def seed_database():
    """Seed the database using start.bat auto-seed feature"""
    print("\n📊 The backend auto-seeds on startup")
    print("   The database should already contain sample data")
    return True

def generate_timetable():
    """Generate a new timetable"""
    print("\n🔄 Generating new timetable...")
    try:
        response = requests.post(
            f'{API_BASE_URL}/api/solvers/generate',
            json={
                'algorithm': 'csp',
                'name': 'Demo Schedule'
            },
            timeout=60
        )
        
        if response.ok:
            data = response.json()
            print(f"✅ Timetable generated successfully!")
            print(f"   - ID: {data.get('id')}")
            print(f"   - Name: {data.get('name')}")
            print(f"   - Total slots: {len(data.get('slots', []))}")
            return True
        else:
            print(f"❌ Failed to generate timetable: {response.status_code}")
            print(f"   {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error generating timetable: {e}")
        return False

def main():
    print("="*60)
    print(" TIMETABLE DEMO - QUICK RUNNER")
    print("="*60)
    
    # Step 1: Check backend
    print("\n[1/3] Checking backend status...")
    if not check_backend():
        return
    
    # Step 2: Note about seeding
    print("\n[2/3] Database seeding...")
    seed_database()
    
    # Step 3: Generate timetable
    print("\n[3/3] Timetable generation...")
    if generate_timetable():
        print("\n" + "="*60)
        print(" ✅ DEMO SETUP COMPLETE!")
        print("="*60)
        print("\n📋 Next Steps:")
        print("   1. Open demo_timetable.html in your web browser")
        print("   2. Click 'Load Latest Timetable' button")
        print("   3. View your generated timetable!")
        print("\n💡 Tips:")
        print("   - The timetable shows Monday-Friday")
        print("   - Lunch break is at 12:00 PM - 1:00 PM (highlighted)")
        print("   - 6 teaching hours per day")
        print("   - Click 'Generate New Schedule' to create a different layout")
    else:
        print("\n⚠️  Timetable generation failed")
        print("   You can still view any existing timetable by opening demo_timetable.html")

if __name__ == "__main__":
    main()
