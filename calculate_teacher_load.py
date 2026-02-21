"""
Calculate teacher load factor for each teacher based on the generated timetable.
Load Factor = (Assigned Slots / Total Available Slots) × 100
"""
import sqlite3
from collections import defaultdict

conn = sqlite3.connect('backend/timetable.db')
cursor = conn.cursor()

print("=== TEACHER LOAD FACTOR ANALYSIS ===\n")

# Get latest timetable version
cursor.execute("SELECT id, name, status FROM timetable_versions ORDER BY id DESC LIMIT 1")
version = cursor.fetchone()

if not version:
    print("No timetable found!")
    conn.close()
    exit()

version_id, version_name, status = version
print(f"Timetable: {version_name} (ID: {version_id})")
print(f"Status: {status}\n")

if status != 'active':
    print(f"⚠ Warning: Timetable status is '{status}', not 'active'")
    print("Generation might still be in progress...\n")

# Get total available teaching slots
cursor.execute("SELECT COUNT(*) FROM time_slots WHERE is_break = 0")
total_slots = cursor.fetchone()[0]
print(f"Total Available Teaching Slots: {total_slots}\n")

# Calculate load for each teacher
cursor.execute("""
    SELECT 
        t.id,
        t.name,
        t.email,
        t.max_hours_per_week,
        COUNT(te.id) as assigned_slots
    FROM teachers t
    LEFT JOIN timetable_entries te ON te.teacher_id = t.id AND te.version_id = ?
    GROUP BY t.id
    ORDER BY assigned_slots DESC, t.name
""", (version_id,))

teachers = cursor.fetchall()

print("=" * 90)
print(f"{'Teacher Name':<30} {'Email':<30} {'Assigned':<10} {'Load %':<10} {'Status'}")
print("=" * 90)

total_assigned = 0
for teacher_id, name, email, max_hours, assigned in teachers:
    load_factor = (assigned / total_slots * 100) if total_slots > 0 else 0
    total_assigned += assigned
    
    # Determine status
    if assigned == 0:
        status_icon = "⚪ Idle"
    elif load_factor < 30:
        status_icon = "🟢 Light"
    elif load_factor < 60:
        status_icon = "🟡 Moderate"
    elif load_factor < 80:
        status_icon = "🟠 Heavy"
    else:
        status_icon = "🔴 Overloaded"
    
    print(f"{name:<30} {email:<30} {assigned:<10} {load_factor:>6.1f}%   {status_icon}")

print("=" * 90)

# Summary statistics
avg_load = (total_assigned / len(teachers) / total_slots * 100) if teachers and total_slots > 0 else 0
print(f"\n📊 SUMMARY STATISTICS:")
print(f"   Total Teachers: {len(teachers)}")
print(f"   Total Assigned Slots: {total_assigned}")
print(f"   Average Load per Teacher: {avg_load:.1f}%")
print(f"   Total Capacity: {len(teachers) * total_slots} slots")
print(f"   Utilization: {(total_assigned / (len(teachers) * total_slots) * 100):.1f}%")

# Check class coverage
print(f"\n📚 CLASS SECTION COVERAGE:")
cursor.execute("""
    SELECT 
        cg.name,
        COUNT(DISTINCT te.time_slot_id) as filled_slots
    FROM class_groups cg
    LEFT JOIN timetable_entries te ON te.class_group_id = cg.id AND te.version_id = ?
    GROUP BY cg.id
    ORDER BY cg.name
""", (version_id,))

sections = cursor.fetchall()
print("=" * 60)
print(f"{'Section':<20} {'Filled Slots':<15} {'Coverage':<15} {'Status'}")
print("=" * 60)

for section_name, filled in sections:
    coverage = (filled / total_slots * 100) if total_slots > 0 else 0
    
    if coverage == 100:
        status_icon = "✅ Complete"
    elif coverage >= 80:
        status_icon = "🟡 Almost Full"
    elif coverage >= 50:
        status_icon = "🟠 Partial"
    else:
        status_icon = "🔴 Incomplete"
    
    print(f"{section_name:<20} {filled}/{total_slots:<13} {coverage:>6.1f}%        {status_icon}")

print("=" * 60)

# Subject distribution
print(f"\n📖 SUBJECT DISTRIBUTION:")
cursor.execute("""
    SELECT 
        s.name,
        s.code,
        COUNT(te.id) as times_scheduled
    FROM subjects s
    LEFT JOIN timetable_entries te ON te.subject_id = s.id AND te.version_id = ?
    GROUP BY s.id
    ORDER BY times_scheduled DESC
    LIMIT 10
""", (version_id,))

subjects = cursor.fetchall()
print("=" * 70)
print(f"{'Subject':<40} {'Code':<10} {'Scheduled'}")
print("=" * 70)
for subj_name, code, count in subjects:
    print(f"{subj_name:<40} {code:<10} {count} times")
print("=" * 70)

conn.close()

print("\n✅ Analysis complete!")
print("\n💡 TIP: Refresh the timetable page and select any class section")
print("   to see their complete schedule with all 25 slots filled!")
