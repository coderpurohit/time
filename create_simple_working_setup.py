import sqlite3

conn = sqlite3.connect('backend/timetable.db')
cursor = conn.cursor()

print("=== CREATING SIMPLE WORKING SETUP ===\n")

# Clear everything
print("Clearing database...")
cursor.execute("DELETE FROM timetable_entries")
cursor.execute("DELETE FROM timetable_versions")
cursor.execute("DELETE FROM lesson_teachers")
cursor.execute("DELETE FROM lesson_class_groups")
cursor.execute("DELETE FROM lesson_subjects")
cursor.execute("DELETE FROM lessons")
cursor.execute("DELETE FROM subjects")
cursor.execute("DELETE FROM teachers")
cursor.execute("DELETE FROM class_groups")
conn.commit()
print("✓ Database cleared\n")

# Create 15 teachers (5 original + 10 new)
print("Creating 15 teachers...")
teachers = [
    (1, "Dr. Rajesh Kumar", "rajesh@college.edu", 20),
    (2, "Prof. Priya Sharma", "priya@college.edu", 20),
    (3, "Dr. Amit Patel", "amit@college.edu", 20),
    (4, "Dr. Sneha Desai", "sneha@college.edu", 20),
    (5, "Prof. Vikram Singh", "vikram@college.edu", 20),
    (6, "Dr. Kavita Joshi", "kavita@college.edu", 20),
    (7, "Prof. Rahul Mehta", "rahul@college.edu", 20),
    (8, "Dr. Anita Rao", "anita@college.edu", 20),
    (9, "Prof. Suresh Nair", "suresh@college.edu", 20),
    (10, "Dr. Meera Iyer", "meera@college.edu", 20),
    (11, "Prof. Arun Reddy", "arun@college.edu", 20),
    (12, "Dr. Pooja Gupta", "pooja@college.edu", 20),
    (13, "Prof. Kiran Shah", "kiran@college.edu", 20),
    (14, "Dr. Deepak Verma", "deepak@college.edu", 20),
    (15, "Prof. Neha Kapoor", "neha@college.edu", 20)
]
for t in teachers:
    cursor.execute("""
        INSERT INTO teachers (id, name, email, max_hours_per_week, available_slots, created_at)
        VALUES (?, ?, ?, ?, '[]', datetime('now'))
    """, t)
    print(f"  ✓ {t[1]}")

# Create 7 subjects with distributed teacher assignments
print("\nCreating 7 subjects...")
subjects = [
    (1, "Machine Learning", "ML", 0, 4, "LectureHall", 1, 1),
    (2, "Artificial Intelligence", "AI", 0, 4, "LectureHall", 1, 2),
    (3, "Computer Networks", "CN", 0, 3, "LectureHall", 1, 3),
    (4, "Human Computer Interaction", "HCI", 0, 3, "LectureHall", 1, 4),
    (5, "Operating Systems", "OS", 0, 4, "LectureHall", 1, 5),
    (6, "CN Lab", "CNL", 1, 2, "ComputerLab", 2, 6),
    (7, "ML Lab", "MLL", 1, 2, "ComputerLab", 2, 7)
]
for s in subjects:
    cursor.execute("""
        INSERT INTO subjects (id, name, code, is_lab, credits, required_room_type, duration_slots, teacher_id, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
    """, s)
    lab_marker = " (Lab)" if s[3] else ""
    print(f"  ✓ {s[1]}{lab_marker} - Default Teacher {s[7]}")

# Create 9 class groups (SE, TE, BE with A, B, C divisions)
print("\nCreating 9 class groups...")
groups = [
    (1, "SE-AIDS-A", 60),
    (2, "SE-AIDS-B", 60),
    (3, "SE-AIDS-C", 60),
    (4, "TE-AIDS-A", 55),
    (5, "TE-AIDS-B", 55),
    (6, "TE-AIDS-C", 55),
    (7, "BE-AIDS-A", 50),
    (8, "BE-AIDS-B", 50),
    (9, "BE-AIDS-C", 50)
]
for g in groups:
    cursor.execute("""
        INSERT INTO class_groups (id, name, student_count, created_at)
        VALUES (?, ?, ?, datetime('now'))
    """, g)
    print(f"  ✓ {g[1]}")

# Create lessons with distributed teacher assignments
# Strategy: Assign different teachers to different sections to balance load
print("\nCreating lessons with balanced teacher distribution...")

# Teacher assignment strategy for each subject across 9 sections
# We'll rotate teachers to distribute load evenly
teacher_rotation = {
    1: [1, 8, 11, 1, 8, 11, 1, 8, 11],   # ML: Teachers 1, 8, 11 (3 teachers × 3 sections each)
    2: [2, 9, 12, 2, 9, 12, 2, 9, 12],   # AI: Teachers 2, 9, 12
    3: [3, 10, 13, 3, 10, 13, 3, 10, 13], # CN: Teachers 3, 10, 13
    4: [4, 14, 4, 14, 4, 14, 4, 14, 4],   # HCI: Teachers 4, 14 (alternating)
    5: [5, 15, 5, 15, 5, 15, 5, 15, 5],   # OS: Teachers 5, 15 (alternating)
    6: [6, 10, 13, 6, 10, 13, 6, 10, 13], # CN Lab: Teachers 6, 10, 13
    7: [7, 8, 11, 7, 8, 11, 7, 8, 11]     # ML Lab: Teachers 7, 8, 11
}

# Define how many periods per week each subject gets
subject_periods = {
    1: 5,  # Machine Learning - 5 periods/week
    2: 4,  # Artificial Intelligence - 4 periods/week
    3: 4,  # Computer Networks - 4 periods/week
    4: 3,  # Human Computer Interaction - 3 periods/week
    5: 5,  # Operating Systems - 5 periods/week
    6: 2,  # CN Lab - 2 periods/week
    7: 2   # ML Lab - 2 periods/week
}
# Total: 25 periods per class per week

lesson_id = 1
total_lessons = 0

for idx, (group_id, group_name, _) in enumerate(groups):
    print(f"\n  {group_name}:")
    for subj_id, subj_name, _, _, _, _, _, _ in subjects:
        periods_per_week = subject_periods[subj_id]
        teacher_id = teacher_rotation[subj_id][idx]
        
        # Create one lesson with multiple periods per week
        cursor.execute("""
            INSERT INTO lessons (id, lessons_per_week, length_per_lesson, created_at)
            VALUES (?, ?, 1, datetime('now'))
        """, (lesson_id, periods_per_week))
        
        # Link teacher (using rotated teacher for this section)
        cursor.execute("""
            INSERT INTO lesson_teachers (lesson_id, teacher_id)
            VALUES (?, ?)
        """, (lesson_id, teacher_id))
        
        # Link subject
        cursor.execute("""
            INSERT INTO lesson_subjects (lesson_id, subject_id)
            VALUES (?, ?)
        """, (lesson_id, subj_id))
        
        # Link class group
        cursor.execute("""
            INSERT INTO lesson_class_groups (lesson_id, class_group_id)
            VALUES (?, ?)
        """, (lesson_id, group_id))
        
        teacher_name = next(t[1] for t in teachers if t[0] == teacher_id)
        print(f"    ✓ {subj_name}: {periods_per_week} periods/week (Teacher: {teacher_name})")
        total_lessons += periods_per_week
        lesson_id += 1

conn.commit()

# Calculate teacher load
print("\n=== TEACHER LOAD CALCULATION ===")
teacher_loads = {}
for teacher_id, teacher_name, _, max_hours in teachers:
    # Count how many periods this teacher teaches
    cursor.execute("""
        SELECT SUM(l.lessons_per_week)
        FROM lessons l
        JOIN lesson_teachers lt ON lt.lesson_id = l.id
        WHERE lt.teacher_id = ?
    """, (teacher_id,))
    total_periods = cursor.fetchone()[0] or 0
    teacher_loads[teacher_id] = total_periods
    load_pct = (total_periods / 25 * 100) if total_periods > 0 else 0
    status = "✓" if total_periods <= 20 else "⚠"
    print(f"{status} {teacher_name}: {total_periods} periods/week (Load: {load_pct:.1f}%)")

print("\n=== SUMMARY ===")
print("Teachers: 15")
print("Subjects: 7 (5 theory + 2 labs)")
print("Class Groups: 9 (SE-A/B/C, TE-A/B/C, BE-A/B/C)")
print(f"Total lessons: {lesson_id - 1}")
print(f"Total slot-assignments needed: {total_lessons}")
print("Available slots: 25")
print(f"Slots per class: 25 (ALL FILLED)")
print("\nLoad is now distributed across 15 teachers!")
print(f"Average load per teacher: {sum(teacher_loads.values()) / len(teachers):.1f} periods/week")

conn.close()
