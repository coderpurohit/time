import sqlite3

conn = sqlite3.connect('backend/timetable.db')
cursor = conn.cursor()

# Get latest timetable
cursor.execute('SELECT id FROM timetable_versions ORDER BY id DESC LIMIT 1')
timetable_id = cursor.fetchone()[0]

print(f"=== TIMETABLE {timetable_id} ANALYSIS ===\n")

# Teachers in timetable entries
cursor.execute('''
    SELECT DISTINCT t.id, t.name, COUNT(te.id) as entries
    FROM timetable_entries te
    JOIN teachers t ON te.teacher_id = t.id
    WHERE te.version_id = ?
    GROUP BY t.id, t.name
    ORDER BY entries DESC
''', (timetable_id,))

used_teachers = cursor.fetchall()
print(f"Teachers in TIMETABLE ENTRIES ({len(used_teachers)}):")
for tid, name, count in used_teachers:
    print(f"  {name} (ID:{tid}): {count} entries")

# Teachers in lessons
cursor.execute('''
    SELECT DISTINCT t.id, t.name, COUNT(DISTINCT l.id) as lesson_count
    FROM lesson_teachers lt
    JOIN teachers t ON lt.teacher_id = t.id
    JOIN lessons l ON lt.lesson_id = l.id
    GROUP BY t.id, t.name
    ORDER BY lesson_count DESC
''')

lesson_teachers = cursor.fetchall()
print(f"\nTeachers in LESSONS ({len(lesson_teachers)}):")
for tid, name, count in lesson_teachers:
    print(f"  {name} (ID:{tid}): {count} lessons")

# Find teachers in lessons but not in timetable
used_ids = {t[0] for t in used_teachers}
lesson_ids = {t[0] for t in lesson_teachers}
missing = lesson_ids - used_ids

if missing:
    print(f"\n⚠️  Teachers in LESSONS but NOT in TIMETABLE:")
    for tid, name, count in lesson_teachers:
        if tid in missing:
            print(f"  {name} (ID:{tid}): {count} lessons NOT scheduled")

conn.close()
