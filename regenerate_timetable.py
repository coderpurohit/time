import requests
import time

print("=== REGENERATING TIMETABLE ===\n")

# Check if server is running
try:
    response = requests.get("http://localhost:8000/api/health", timeout=2)
    print("✓ Server is running")
except:
    print("✗ Server is not running. Please start it with: cd backend && start.bat")
    exit(1)

# Clear old timetable versions
print("\nClearing old timetable versions...")
import sqlite3
conn = sqlite3.connect('backend/timetable.db')
cursor = conn.cursor()
cursor.execute("DELETE FROM timetable_entries")
cursor.execute("DELETE FROM timetable_versions")
conn.commit()
conn.close()
print("✓ Old timetables cleared")

# Generate new timetable
print("\nGenerating new timetable with CSP solver...")
print("This may take a minute with the 3 classes/day constraint...")

response = requests.post(
    "http://localhost:8000/api/solvers/generate",
    params={"method": "csp"},
    timeout=120
)

if response.status_code == 200:
    result = response.json()
    print(f"\n✓ Timetable generated successfully!")
    print(f"  Version ID: {result['id']}")
    print(f"  Name: {result['name']}")
    print(f"  Algorithm: {result['algorithm']}")
    print(f"  Status: {result['status']}")
    
    # Check how many entries were created
    conn = sqlite3.connect('backend/timetable.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM timetable_entries WHERE version_id = ?", (result['id'],))
    entry_count = cursor.fetchone()[0]
    print(f"  Total entries: {entry_count}")
    
    # Check entries per class
    cursor.execute("""
        SELECT cg.name, COUNT(*) as count
        FROM timetable_entries te
        JOIN class_groups cg ON cg.id = te.class_group_id
        WHERE te.version_id = ?
        GROUP BY cg.name
        ORDER BY cg.name
    """, (result['id'],))
    
    print("\n  Entries per class:")
    for class_name, count in cursor.fetchall():
        status = "✓" if count == 25 else "✗"
        print(f"    {status} {class_name}: {count}/25 periods")
    
    conn.close()
    
    print("\n✓ SUCCESS! Check the timetable page to verify.")
else:
    print(f"\n✗ Generation failed: {response.status_code}")
    print(response.text)
