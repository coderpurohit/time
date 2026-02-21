"""
Complete database reset - remove ALL old data and start fresh
"""
import sqlite3

conn = sqlite3.connect('backend/timetable.db')
c = conn.cursor()

print("=== COMPLETE DATABASE RESET ===\n")

# 1. Clear timetables
c.execute('DELETE FROM timetable_entries')
c.execute('DELETE FROM timetable_versions')
print("1. ✓ Cleared timetables")

# 2. Clear lessons
c.execute('DELETE FROM lesson_teachers')
c.execute('DELETE FROM lesson_class_groups')
c.execute('DELETE FROM lesson_subjects')
c.execute('DELETE FROM lessons')
print("2. ✓ Cleared lessons")

# 3. Clear all subjects
c.execute('DELETE FROM subjects')
print("3. ✓ Cleared ALL subjects")

# 4. Clear all class groups
c.execute('DELETE FROM class_groups')
print("4. ✓ Cleared ALL class groups")

# 5. Clear all teachers
c.execute('DELETE FROM teachers')
print("5. ✓ Cleared ALL teachers")

# 6. Clear all rooms
c.execute('DELETE FROM rooms')
print("6. ✓ Cleared ALL rooms")

conn.commit()

print("\n=== DATABASE IS NOW COMPLETELY EMPTY ===")
print("\nNow run: python test_bulk_import.py")
print("This will import fresh CS data from the sample CSV files")

conn.close()
