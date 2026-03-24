import sqlite3
import json

c = sqlite3.connect('timetable.db')
c.row_factory = sqlite3.Row

data = {
    'teachers': [dict(r) for r in c.execute('SELECT * FROM teachers').fetchall()],
    'subjects': [dict(r) for r in c.execute('SELECT * FROM subjects').fetchall()],
    'class_groups': [dict(r) for r in c.execute('SELECT * FROM class_groups').fetchall()],
    'time_slots': [dict(r) for r in c.execute('SELECT * FROM time_slots').fetchall()]
}

with open('db_dump.json', 'w') as f:
    json.dump(data, f, indent=2)

print("Dumped to db_dump.json")
