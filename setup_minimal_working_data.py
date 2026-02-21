"""
Setup minimal working data for timetable generation
Keeps only 3 subjects and 3 class groups for a feasible 9-assignment problem
"""
import sqlite3

conn = sqlite3.connect('backend/timetable.db')
cursor = conn.cursor()

print("=== SETTING UP MINIMAL WORKING DATA ===\n")

# Step 1: Clear timetables
print("1. Clearing old timetables...")
cursor.execute("DELETE FROM timetable_entries")
cursor.execute("DELETE FROM timetable_versions")
conn.commit()
print("   ✓ Cleared\n")

# Step 2: Keep only 3 class groups
print("2. Reducing to 3 class groups...")
cursor.execute("SELECT id, name FROM class_groups ORDER BY id LIMIT 3")
keep_groups = [row[0] for row in cursor.fetchall()]
print(f"   Keeping groups: {keep_groups}")

cursor.execute(f"DELETE FROM class_groups WHERE id NOT IN ({','.join(map(str, keep_groups))})")
conn.commit()
print(f"   ✓ Reduced to 3 groups\n")

# Step 3: Keep only 3 subjects (with teachers)
print("3. Reducing to 3 subjects...")
cursor.execute("SELECT id, name, teacher_id FROM subjects WHERE teacher_id IS NOT NULL ORDER BY id LIMIT 3")
subjects = cursor.fetchall()
keep_subjects = [row[0] for row in subjects]
print(f"   Keeping subjects: {[f'{s[1]} (ID:{s[0]})' for s in subjects]}")

cursor.execute(f"DELETE FROM subjects WHERE id NOT IN ({','.join(map(str, keep_subjects))})")
conn.commit()
print(f"   ✓ Reduced to 3 subjects\n")

# Step 4: Verify final state
print("4. Final data summary:")
cursor.execute("SELECT COUNT(*) FROM teachers")
print(f"   Teachers: {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM subjects WHERE teacher_id IS NOT NULL")
print(f"   Subjects (with teachers): {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM class_groups")
print(f"   Class Groups: {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM rooms")
print(f"   Rooms: {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM time_slots WHERE is_break = 0")
slots = cursor.fetchone()[0]
print(f"   Time Slots (non-break): {slots}")

required = 3 * 3
print(f"\n   Required assignments: 3 × 3 = {required}")
print(f"   Available slots: {slots}")
print(f"   Feasibility: {'✓ FEASIBLE' if required <= slots else '✗ NOT FEASIBLE'}")

conn.close()

print("\n=== SETUP COMPLETE ===")
print("\nNow try generating the timetable from the web interface:")
print("http://127.0.0.1:8000/timetable_page.html")
print("\nClick 'Generate New Schedule' - it should work now!")
