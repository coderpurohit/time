import sqlite3

conn = sqlite3.connect('backend/timetable.db')
cursor = conn.cursor()

print("=== COMPLETE FIX FOR ALL ISSUES ===\n")

# Step 1: Delete orphaned lessons (teachers that don't exist)
print("Step 1: Cleaning orphaned lessons...")
cursor.execute('''
    DELETE FROM lesson_teachers 
    WHERE teacher_id NOT IN (SELECT id FROM teachers)
''')
orphaned_count = cursor.rowcount
print(f"  Removed {orphaned_count} orphaned teacher-lesson links")

# Delete lessons that have no teachers after cleanup
cursor.execute('''
    DELETE FROM lessons 
    WHERE id NOT IN (SELECT DISTINCT lesson_id FROM lesson_teachers)
''')
deleted_lessons = cursor.rowcount
print(f"  Deleted {deleted_lessons} lessons with no teachers")

conn.commit()

# Step 2: Check remaining lessons
cursor.execute('''
    SELECT COUNT(DISTINCT l.id), SUM(l.lessons_per_week * l.length_per_lesson)
    FROM lessons l
    JOIN lesson_teachers lt ON l.id = lt.lesson_id
''')
lesson_count, total_periods = cursor.fetchone()
print(f"\nStep 2: After cleanup:")
print(f"  Remaining lessons: {lesson_count}")
print(f"  Total periods needed: {total_periods}")

# Step 3: Calculate target and adjust if needed
target_capacity = 275  # 11 classes × 25 periods
if total_periods > target_capacity:
    excess = total_periods - target_capacity
    print(f"\n⚠️  Still {excess} periods over capacity!")
    print(f"  Need to reduce lessons_per_week...")
    
    # Reduce lessons_per_week proportionally
    # Strategy: Reduce high-frequency lessons first
    cursor.execute('''
        SELECT l.id, l.lessons_per_week, l.length_per_lesson
        FROM lessons l
        JOIN lesson_teachers lt ON l.id = lt.lesson_id
        WHERE l.lessons_per_week > 2
        ORDER BY l.lessons_per_week DESC
    ''')
    
    high_freq_lessons = cursor.fetchall()
    periods_to_reduce = excess
    
    for lesson_id, per_week, length in high_freq_lessons:
        if periods_to_reduce <= 0:
            break
        
        # Reduce by 1 period per week
        new_per_week = max(2, per_week - 1)  # Don't go below 2
        reduction = (per_week - new_per_week) * length
        
        if reduction > 0:
            cursor.execute('''
                UPDATE lessons 
                SET lessons_per_week = ?
                WHERE id = ?
            ''', (new_per_week, lesson_id))
            periods_to_reduce -= reduction
            print(f"    Lesson {lesson_id}: {per_week} → {new_per_week} per week (saved {reduction} periods)")
    
    conn.commit()
    
    # Recalculate
    cursor.execute('''
        SELECT SUM(l.lessons_per_week * l.length_per_lesson)
        FROM lessons l
        JOIN lesson_teachers lt ON l.id = lt.lesson_id
    ''')
    new_total = cursor.fetchone()[0]
    print(f"\n  New total periods: {new_total}")
    
    if new_total > target_capacity:
        print(f"  ⚠️  Still {new_total - target_capacity} over - need more reduction")
    else:
        print(f"  ✅ Now fits within capacity!")

# Step 4: Verify teacher distribution
print(f"\nStep 3: Teacher distribution:")
cursor.execute('''
    SELECT t.name, COUNT(DISTINCT l.id) as lesson_count,
           SUM(l.lessons_per_week * l.length_per_lesson) as periods
    FROM teachers t
    JOIN lesson_teachers lt ON t.id = lt.teacher_id
    JOIN lessons l ON lt.lesson_id = l.id
    GROUP BY t.id, t.name
    ORDER BY periods DESC
''')

teachers = cursor.fetchall()
print(f"  Teachers with lessons: {len(teachers)}")
for name, lessons, periods in teachers:
    print(f"    {name}: {lessons} lessons, {periods} periods/week")

# Step 5: Delete failed timetable and prepare for regeneration
print(f"\nStep 4: Cleaning up failed timetable...")
cursor.execute('DELETE FROM timetable_entries')
cursor.execute('DELETE FROM timetable_versions')
conn.commit()
print(f"  ✓ Deleted old timetable")

conn.close()

print("\n" + "="*60)
print("✅ FIX COMPLETE!")
print("="*60)
print("\nNext step: Regenerate timetable via API")
print("  POST http://localhost:8000/api/solvers/generate?method=csp")
