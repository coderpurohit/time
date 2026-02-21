import sqlite3

conn = sqlite3.connect('backend/timetable.db')
c = conn.cursor()

# Clear old timetables
c.execute('DELETE FROM timetable_entries')
c.execute('DELETE FROM timetable_versions')
conn.commit()
print('✓ Cleared old timetable\n')

# Show current subjects
c.execute('SELECT id, name, code FROM subjects ORDER BY id')
print('Current subjects in database:')
for row in c.fetchall():
    print(f'  {row[0]}. {row[1]} ({row[2]})')

print()

# Show current class groups
c.execute('SELECT id, name, student_count FROM class_groups ORDER BY id')
print('Current class groups:')
for row in c.fetchall():
    print(f'  {row[0]}. {row[1]} - {row[2]} students')

print()

# Show current teachers
c.execute('SELECT id, name, email FROM teachers ORDER BY id LIMIT 5')
print('Current teachers (first 5):')
for row in c.fetchall():
    print(f'  {row[0]}. {row[1]} ({row[2]})')

conn.close()

print('\n✓ Database is ready')
print('\nNow:')
print('1. Go to http://127.0.0.1:8000/timetable_page.html')
print('2. Click on "Generate Timetable" tab')
print('3. Click "Generate New Schedule"')
print('4. Wait for generation to complete')
print('5. Click "View Timetable" tab to see the result')
