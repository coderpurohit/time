import sqlite3

conn = sqlite3.connect('backend/timetable.db')
cursor = conn.cursor()

# Check if Saturday slots exist
cursor.execute("SELECT COUNT(*) FROM time_slots WHERE day = 'Saturday'")
saturday_count = cursor.fetchone()[0]

if saturday_count == 0:
    print("Adding Saturday time slots...")
    
    # Add Saturday slots (7 periods: 6 teaching + 1 break)
    saturday_slots = [
        ('Saturday', 0, '12:00', '12:45', 1),  # Break
        ('Saturday', 1, '09:00', '10:00', 0),
        ('Saturday', 2, '10:00', '11:00', 0),
        ('Saturday', 3, '11:00', '12:00', 0),
        ('Saturday', 4, '12:45', '13:45', 0),
        ('Saturday', 5, '13:45', '14:45', 0),
        ('Saturday', 6, '14:45', '15:45', 0),
    ]
    
    for day, period, start, end, is_break in saturday_slots:
        cursor.execute("""
            INSERT INTO time_slots (day, period, start_time, end_time, is_break)
            VALUES (?, ?, ?, ?, ?)
        """, (day, period, start, end, is_break))
    
    conn.commit()
    print(f"✓ Added {len(saturday_slots)} Saturday slots")
else:
    print(f"Saturday slots already exist ({saturday_count} slots)")

# Show updated capacity
cursor.execute("SELECT COUNT(*) FROM time_slots WHERE is_break = 0")
total_slots = cursor.fetchone()[0]
print(f"\nTotal available slots (non-break): {total_slots}")
print(f"Required periods: 33")
print(f"Feasibility: {'✓ FEASIBLE' if 33 <= total_slots else '✗ STILL NOT FEASIBLE'}")

conn.close()
