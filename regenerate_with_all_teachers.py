import sqlite3
import requests
import time

# Connect to database
conn = sqlite3.connect('backend/timetable.db')
cursor = conn.cursor()

print("=== REGENERATING TIMETABLE WITH ALL TEACHERS ===\n")

# Step 1: Check current state
cursor.execute('SELECT COUNT(*) FROM lessons')
lesson_count = cursor.fetchone()[0]
print(f"Total lessons in database: {lesson_count}")

cursor.execute('''
    SELECT COUNT(DISTINCT t.id)
    FROM lesson_teachers lt
    JOIN teachers t ON lt.teacher_id = t.id
''')
teacher_count = cursor.fetchone()[0]
print(f"Teachers with lessons: {teacher_count}")

# Step 2: Delete current timetable
cursor.execute('DELETE FROM timetable_entries')
cursor.execute('DELETE FROM timetable_versions')
conn.commit()
print(f"\n✓ Deleted old timetable")

conn.close()

# Step 3: Trigger new generation via API
print("\n🔄 Generating new timetable via API...")
try:
    response = requests.post(
        'http://localhost:8000/api/solvers/generate',
        params={'method': 'csp'},
        timeout=120
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ Generation successful!")
        print(f"   Timetable ID: {result.get('timetable_id')}")
        print(f"   Status: {result.get('status')}")
        print(f"   Entries: {result.get('entries_count', 'N/A')}")
    else:
        print(f"\n❌ Generation failed: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nMake sure backend server is running: cd backend && start.bat")

# Step 4: Verify results
time.sleep(2)
conn = sqlite3.connect('backend/timetable.db')
cursor = conn.cursor()

cursor.execute('SELECT id FROM timetable_versions ORDER BY id DESC LIMIT 1')
result = cursor.fetchone()
if result:
    timetable_id = result[0]
    
    # Count entries per teacher
    cursor.execute('''
        SELECT t.name, COUNT(te.id) as entries
        FROM timetable_entries te
        JOIN teachers t ON te.teacher_id = t.id
        WHERE te.version_id = ?
        GROUP BY t.id, t.name
        ORDER BY entries DESC
    ''', (timetable_id,))
    
    teachers_used = cursor.fetchall()
    print(f"\n📊 VERIFICATION:")
    print(f"   Teachers used in timetable: {len(teachers_used)}")
    for name, count in teachers_used:
        print(f"     {name}: {count} entries")
    
    cursor.execute('SELECT COUNT(*) FROM timetable_entries WHERE version_id = ?', (timetable_id,))
    total_entries = cursor.fetchone()[0]
    print(f"\n   Total entries: {total_entries}")
    
    if len(teachers_used) < teacher_count:
        print(f"\n⚠️  WARNING: Only {len(teachers_used)}/{teacher_count} teachers are being used!")
        print("   This means the CSP solver is not scheduling all lessons.")
else:
    print("\n❌ No timetable found after generation")

conn.close()
