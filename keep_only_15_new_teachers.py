import sqlite3

db_path = r'C:\Users\bhara\time\backend\timetable.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("="*60)
print("REMOVING OLD 5 TEACHERS (IDs 1-5)")
print("="*60)

# Delete old teachers (IDs 1-5)
old_teacher_ids = [1, 2, 3, 4, 5]

for teacher_id in old_teacher_ids:
    cursor.execute("SELECT name FROM teachers WHERE id = ?", (teacher_id,))
    result = cursor.fetchone()
    if result:
        name = result[0]
        
        # Delete related data
        cursor.execute("DELETE FROM timetable_entries WHERE teacher_id = ?", (teacher_id,))
        deleted_entries = cursor.rowcount
        
        # Delete the teacher
        cursor.execute("DELETE FROM teachers WHERE id = ?", (teacher_id,))
        
        print(f"✓ Deleted ID {teacher_id}: {name} (removed {deleted_entries} timetable entries)")

# Also delete the "string" test teacher (ID 6)
cursor.execute("SELECT name FROM teachers WHERE id = 6")
result = cursor.fetchone()
if result and result[0] == "string":
    cursor.execute("DELETE FROM timetable_entries WHERE teacher_id = 6")
    cursor.execute("DELETE FROM teachers WHERE id = 6")
    print(f"✓ Deleted ID 6: string (test teacher)")

conn.commit()

print("\n" + "="*60)
print("FINAL 14 TEACHERS:")
print("="*60)

cursor.execute("SELECT id, name, email FROM teachers ORDER BY id")
teachers = cursor.fetchall()

for id, name, email in teachers:
    print(f"ID {id:2d}: {name}")

print(f"\nTotal: {len(teachers)} teachers")

conn.close()
print("\n✅ Done! Refresh browser with Ctrl+Shift+R")
