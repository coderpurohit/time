import sqlite3

conn = sqlite3.connect('backend/timetable.db')
cursor = conn.cursor()

# Check if Thursday slots exist
cursor.execute("SELECT COUNT(*) FROM time_slots WHERE day = 'Thursday'")
thursday_count = cursor.fetchone()[0]

if thursday_count == 0:
    print("Adding Thursday time slots...")
    
    # Add Thursday slots (7 periods: 6 teaching + 1 break)
    thursday_slots = [
        ('Thursday', 0, '12:00', '12:45', 1),  # Break
        ('Thursday', 1, '09:00', '10:00', 0),
        ('Thursday', 2, '10:00', '11:00', 0),
        ('Thursday', 3, '11:00', '12:00', 0),
        ('Thursday', 4, '12:45', '13:45', 0),
        ('Thursday', 5, '13:45', '14:45', 0),
        ('Thursday', 6, '14:45', '15:45', 0),
    ]
    
    for day, period, start, end, is_break in thursday_slots:
        cursor.execute("""
            INSERT INTO time_slots (day, period, start_time, end_time, is_break)
            VALUES (?, ?, ?, ?, ?)
        """, (day, period, start, end, is_break))
    
    conn.commit()
    print(f"✓ Added {len(thursday_slots)} Thursday slots")
else:
    print(f"Thursday slots already exist ({thursday_count} slots)")

# Show updated capacity
cursor.execute("SELECT COUNT(*) FROM time_slots WHERE is_break = 0")
total_slots = cursor.fetchone()[0]
print(f"\nTotal available slots (non-break): {total_slots}")
print(f"Required periods: 33")
print(f"Feasibility: {'✓ FEASIBLE' if 33 <= total_slots else '✗ STILL NOT FEASIBLE'}")

conn.close()
