"""
COMPLETE SETUP - Creates everything needed for timetable generation
Run this ONCE to set up the entire system with load factor consideration
"""

import sqlite3
import random

DB_PATH = 'backend/timetable.db'

def create_complete_setup_with_load_factor():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("🚀 Creating complete timetable setup with load factor...")
    
    # 1. Clear everything first
    print("\n1️⃣ Clearing existing data...")
    cursor.execute("DELETE FROM timetable_entries")
    cursor.execute("DELETE FROM timetable_versions")
    cursor.execute("DELETE FROM lesson_teachers")
    cursor.execute("DELETE FROM lesson_class_groups")
    cursor.execute("DELETE FROM lesson_subjects")
    cursor.execute("DELETE FROM lessons")
    cursor.execute("DELETE FROM time_slots")
    cursor.execute("DELETE FROM substitutions")
    cursor.execute("UPDATE subjects SET teacher_id = NULL")
    cursor.execute("DELETE FROM teachers")
    cursor.execute("DELETE FROM subjects")
    cursor.execute("DELETE FROM rooms")
    cursor.execute("DELETE FROM class_groups")
    conn.commit()
    
    # 2. Create 9 Classes
    print("\n2️⃣ Creating 9 AIDS classes...")
    classes = [
        ('SE-AIDS-A', 60), ('SE-AIDS-B', 60), ('SE-AIDS-C', 60),
        ('TE-AIDS-A', 55), ('TE-AIDS-B', 55), ('TE-AIDS-C', 55),
        ('BE-AIDS-A', 50), ('BE-AIDS-B', 50), ('BE-AIDS-C', 50)
    ]
    
    for name, count in classes:
        cursor.execute("INSERT INTO class_groups (name, student_count) VALUES (?, ?)", (name, count))
    
    # 3. Create 15 Teachers with different load capacities
    print("\n3️⃣ Creating 15 teachers with varied load capacities...")
    teachers = [
        ('Dr. Rajesh Kumar', 'rajesh.kumar@college.edu', 22),      # High capacity
        ('Prof. Priya Sharma', 'priya.sharma@college.edu', 20),   # High capacity
        ('Dr. Amit Singh', 'amit.singh@college.edu', 18),         # Medium capacity
        ('Prof. Neha Gupta', 'neha.gupta@college.edu', 18),       # Medium capacity
        ('Dr. Vikram Patel', 'vikram.patel@college.edu', 20),     # High capacity
        ('Prof. Sunita Joshi', 'sunita.joshi@college.edu', 16),   # Lower capacity
        ('Dr. Ravi Mehta', 'ravi.mehta@college.edu', 19),         # Medium capacity
        ('Prof. Kavya Reddy', 'kavya.reddy@college.edu', 17),     # Lower capacity
        ('Dr. Arjun Nair', 'arjun.nair@college.edu', 21),        # High capacity
        ('Prof. Deepika Shah', 'deepika.shah@college.edu', 16),   # Lower capacity
        ('Dr. Manish Agarwal', 'manish.agarwal@college.edu', 19), # Medium capacity
        ('Prof. Pooja Verma', 'pooja.verma@college.edu', 17),     # Lower capacity
        ('Dr. Sanjay Kulkarni', 'sanjay.kulkarni@college.edu', 20), # High capacity
        ('Prof. Anita Desai', 'anita.desai@college.edu', 18),     # Medium capacity
        ('Dr. Rohit Bansal', 'rohit.bansal@college.edu', 21)      # High capacity
    ]
    
    for name, email, hours in teachers:
        cursor.execute("INSERT INTO teachers (name, email, max_hours_per_week) VALUES (?, ?, ?)", (name, email, hours))
    
    # 4. Create Rooms
    print("\n4️⃣ Creating rooms...")
    rooms = [
        ('Room-101', 60, 'LectureHall'),
        ('Room-102', 60, 'LectureHall'),
        ('Room-103', 60, 'LectureHall'),
        ('Lab-201', 30, 'ComputerLab'),
        ('Lab-202', 30, 'ComputerLab'),
        ('Lab-203', 30, 'ComputerLab'),
        ('Room-301', 40, 'LectureHall'),
        ('Room-302', 40, 'LectureHall'),
        ('Auditorium', 200, 'LectureHall'),
        ('Seminar-Hall', 80, 'LectureHall')
    ]
    
    for name, capacity, room_type in rooms:
        cursor.execute("INSERT INTO rooms (name, capacity, type, resources) VALUES (?, ?, ?, ?)", 
                      (name, capacity, room_type, '[]'))
    
    # 5. Create Subjects
    print("\n5️⃣ Creating subjects...")
    subjects = [
        ('Data Structures', 'DS', False, 4, 'LectureHall', 1),
        ('Algorithms', 'ALGO', False, 4, 'LectureHall', 1),
        ('Database Systems', 'DBMS', False, 3, 'LectureHall', 1),
        ('Computer Networks', 'CN', False, 3, 'LectureHall', 1),
        ('Operating Systems', 'OS', False, 4, 'LectureHall', 1),
        ('Software Engineering', 'SE', False, 3, 'LectureHall', 1),
        ('Web Development', 'WD', True, 3, 'ComputerLab', 2),
        ('Machine Learning', 'ML', False, 4, 'LectureHall', 1),
        ('Artificial Intelligence', 'AI', False, 3, 'LectureHall', 1),
        ('Cybersecurity', 'CS', False, 3, 'LectureHall', 1),
        ('Mobile App Development', 'MAD', True, 3, 'ComputerLab', 2),
        ('Cloud Computing', 'CC', False, 3, 'LectureHall', 1)
    ]
    
    for name, code, is_lab, credits, room_type, duration in subjects:
        cursor.execute("INSERT INTO subjects (name, code, is_lab, credits, required_room_type, duration_slots) VALUES (?, ?, ?, ?, ?, ?)", 
                      (name, code, is_lab, credits, room_type, duration))
    
    # 6. Create Time Slots (Monday to Friday, 9 AM to 4 PM)
    print("\n6️⃣ Creating time slots...")
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    times = [
        (1, '09:00', '10:00'),
        (2, '10:00', '11:00'),
        (3, '11:00', '12:00'),
        (4, '12:00', '13:00'),  # Lunch
        (5, '13:00', '14:00'),
        (6, '14:00', '15:00'),
        (7, '15:00', '16:00')
    ]
    
    for day in days:
        for period, start, end in times:
            is_break = (period == 4)  # Lunch break
            cursor.execute("""
                INSERT INTO time_slots (day, period, start_time, end_time, is_break) 
                VALUES (?, ?, ?, ?, ?)
            """, (day, period, start, end, is_break))
    
    # 7. Create Lessons with Load Factor Distribution
    print("\n7️⃣ Creating lessons with load factor consideration...")
    
    # Get IDs
    cursor.execute("SELECT id, name FROM class_groups")
    class_groups = cursor.fetchall()
    
    cursor.execute("SELECT id, name, code FROM subjects")
    subjects_list = cursor.fetchall()
    
    cursor.execute("SELECT id, name, max_hours_per_week FROM teachers ORDER BY max_hours_per_week DESC")
    teachers_list = cursor.fetchall()
    
    # Create teacher load tracking
    teacher_loads = {t[0]: 0 for t in teachers_list}  # teacher_id: current_load
    
    lesson_count = 0
    for class_id, class_name in class_groups:
        for subject_id, subject_name, subject_code in subjects_list:
            # Find teacher with lowest current load who can handle more
            available_teachers = [(tid, name, max_hours) for tid, name, max_hours in teachers_list 
                                if teacher_loads[tid] < max_hours - 3]  # Leave some buffer
            
            if not available_teachers:
                # If all teachers are at capacity, use the one with most capacity
                teacher_id = max(teachers_list, key=lambda x: x[2])[0]
            else:
                # Choose teacher with lowest current load
                teacher_id = min(available_teachers, key=lambda x: teacher_loads[x[0]])[0]
            
            # Create lesson
            cursor.execute("""
                INSERT INTO lessons (lessons_per_week, length_per_lesson) 
                VALUES (?, ?)
            """, (3, 60))  # 3 lessons per week, 60 minutes each
            
            lesson_id = cursor.lastrowid
            
            # Link lesson to subject, teacher, and class
            cursor.execute("INSERT INTO lesson_subjects (lesson_id, subject_id) VALUES (?, ?)", (lesson_id, subject_id))
            cursor.execute("INSERT INTO lesson_teachers (lesson_id, teacher_id) VALUES (?, ?)", (lesson_id, teacher_id))
            cursor.execute("INSERT INTO lesson_class_groups (lesson_id, class_group_id) VALUES (?, ?)", (lesson_id, class_id))
            
            # Update teacher load
            teacher_loads[teacher_id] += 3  # 3 lessons per week
            lesson_count += 1
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ COMPLETE SETUP WITH LOAD FACTOR CREATED!")
    print(f"📊 Summary:")
    print(f"   - Classes: {len(classes)}")
    print(f"   - Teachers: {len(teachers)}")
    print(f"   - Subjects: {len(subjects)}")
    print(f"   - Rooms: {len(rooms)}")
    print(f"   - Lessons: {lesson_count}")
    print(f"   - Time Slots: {len(days) * len(times)}")
    
    print(f"\n📈 Teacher Load Distribution:")
    for teacher_id, load in teacher_loads.items():
        teacher_name = next(name for tid, name, _ in teachers_list if tid == teacher_id)
        teacher_max = next(max_h for tid, _, max_h in teachers_list if tid == teacher_id)
        utilization = (load / teacher_max * 100) if teacher_max > 0 else 0
        print(f"   - {teacher_name}: {load}/{teacher_max} lessons ({utilization:.1f}% utilization)")
    
    print(f"\n🎯 Now you can generate timetables with proper load balancing!")

if __name__ == '__main__':
    create_complete_setup_with_load_factor()