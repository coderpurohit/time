import sqlite3

db_path = r'C:\Users\bhara\time\backend\timetable.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("="*60)
print("REMOVING OLD 14 TEACHERS (IDs 7-20)")
print("="*60)

# Delete old teachers (IDs 7-20)
for teacher_id in range(7, 21):
    cursor.execute("SELECT name FROM teachers WHERE id = ?", (teacher_id,))
    result = cursor.fetchone()
    if result:
        name = result[0]
        
        # Delete related data
        cursor.execute("DELETE FROM timetable_entries WHERE teacher_id = ?", (teacher_id,))
        cursor.execute("DELETE FROM teachers WHERE id = ?", (teacher_id,))
        
        print(f"  ✓ Deleted ID {teacher_id}: {name}")

conn.commit()

print("\n" + "="*60)
print("FINAL 15 TEACHERS (IDs 21-35):")
print("="*60)

cursor.execute("SELECT id, name, email, max_hours_per_week FROM teachers ORDER BY id")
teachers = cursor.fetchall()

for id, name, email, hours in teachers:
    print(f"ID {id:2d}: {name:30s} | {hours} hrs/week")

print(f"\nTotal: {len(teachers)} teachers")

if len(teachers) != 15:
    print(f"\n⚠️ WARNING: Expected 15 teachers, found {len(teachers)}")
else:
    print("\n✅ Perfect! Exactly 15 teachers.")

conn.close()
print("\n✅ Done! Refresh browser with Ctrl+Shift+R")
