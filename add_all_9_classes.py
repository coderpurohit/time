import sqlite3

# Connect to database
conn = sqlite3.connect('backend/timetable.db')
cursor = conn.cursor()

# Classes to add: SE, TE, BE with A, B, C sections
classes = [
    ('SE-AIDS-A', 60),
    ('SE-AIDS-B', 60),
    ('SE-AIDS-C', 60),
    ('TE-AIDS-A', 60),
    ('TE-AIDS-B', 60),
    ('TE-AIDS-C', 60),
    ('BE-AIDS-A', 60),
    ('BE-AIDS-B', 60),
    ('BE-AIDS-C', 60),
]

print("Adding 9 classes (SE, TE, BE with A, B, C sections)...")

for class_name, student_count in classes:
    # Check if class already exists
    cursor.execute("SELECT id FROM class_groups WHERE name = ?", (class_name,))
    existing = cursor.fetchone()
    
    if existing:
        print(f"✓ {class_name} already exists")
    else:
        cursor.execute("""
            INSERT INTO class_groups (name, student_count)
            VALUES (?, ?)
        """, (class_name, student_count))
        print(f"✓ Added {class_name} with {student_count} students")

conn.commit()

# Verify
cursor.execute("SELECT name, student_count FROM class_groups ORDER BY name")
all_classes = cursor.fetchall()

print("\n" + "="*50)
print("ALL CLASSES IN DATABASE:")
print("="*50)
for name, count in all_classes:
    print(f"  {name}: {count} students")

print(f"\nTotal: {len(all_classes)} classes")

conn.close()
print("\n✅ Done! Refresh your browser to see all classes.")
