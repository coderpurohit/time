import sqlite3

# Path to the user's database
db_path = r'C:\Users\bhara\time\backend\timetable.db'

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("="*50)
print("REMOVING OLD CLASSES (SE-AI-DS, TE-AI-DS)")
print("="*50)

# Classes to delete (old naming)
old_classes = ['SE-AI-DS-A', 'SE-AI-DS-B', 'SE-AI-DS-C', 'TE-AI-DS-A']

for class_name in old_classes:
    cursor.execute("SELECT id FROM class_groups WHERE name = ?", (class_name,))
    result = cursor.fetchone()
    if result:
        class_id = result[0]
        
        # Delete related timetable entries first
        cursor.execute("DELETE FROM timetable_entries WHERE class_group_id = ?", (class_id,))
        deleted_entries = cursor.rowcount
        
        # Delete the class
        cursor.execute("DELETE FROM class_groups WHERE id = ?", (class_id,))
        
        print(f"✓ Deleted {class_name} (removed {deleted_entries} timetable entries)")
    else:
        print(f"  {class_name} not found (already deleted)")

conn.commit()

print("\n" + "="*50)
print("FINAL 9 CLASSES (AIDS ONLY):")
print("="*50)
cursor.execute("SELECT name, student_count FROM class_groups ORDER BY name")
all_classes = cursor.fetchall()

for name, count in all_classes:
    print(f"  {name}: {count} students")

print(f"\nTotal: {len(all_classes)} classes")

if len(all_classes) != 9:
    print(f"\n⚠️ WARNING: Expected 9 classes, found {len(all_classes)}")
else:
    print("\n✅ Perfect! Exactly 9 classes as expected.")

conn.close()
print("\n✅ Done! Refresh browser with Ctrl+Shift+R")
