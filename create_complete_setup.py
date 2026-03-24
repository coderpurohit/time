"""
Create Complete Setup - Teachers + Subjects + Rooms + Lessons + Time Slots
"""

import sqlite3

DB_PATH = 'backend/timetable.db'

def create_complete_setup():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("🚀 Creating complete timetable setup...")
    
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
    
    # 3. Create 15 Teachers
    print("\n3️⃣ Creating 15 teachers...")
    teachers = [
        ('Dr. Rajesh Kumar', 'rajesh.kumar@college.edu', 20),
        ('Prof. Priya Sharma', 'priya.sharma@college.edu', 18),
        ('Dr. Amit Singh', 'amit.singh@college.edu', 22),
        ('Prof. Neha Gupta', 'neha.gupta@college.edu', 19),
        ('Dr. Vikram Patel', 'vikram.patel@college.edu', 21),
        ('Prof. Sunita Joshi', 'sunita.joshi@college.edu', 18),
        ('Dr. Ravi Mehta', 'ravi.mehta@college.edu', 20),
        ('Prof. Kavya Reddy', 'kavya.reddy@college.edu', 19),
        ('Dr. Arjun Nair', 'arjun.nair@college.edu', 22),
        ('Prof. Deepika Shah', 'deepika.shah@college.edu', 18),
        ('Dr. Manish Agarwal', 'manish.agarwal@college.edu', 21),
        ('Prof. Pooja Verma', 'pooja.verma@college.edu', 19),
        ('Dr. Sanjay Kulkarni', 'sanjay.kulkarni@college.edu', 20),
        ('Prof. Anita Desai', 'anita.desai@college.edu', 18),
        ('Dr. Rohit Bansal', 'rohit.bansal@college.edu', 22)
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
    
    # 7. Create Lessons (Each class gets each subject)
    print("\n7️⃣ Creating lessons...")
    
    # Get IDs
    cursor.execute("SELECT id, name FROM class_groups")
    class_groups = cursor.fetchall()
    
    cursor.execute("SELECT id, name, code FROM subjects")
    subjects_list = cursor.fetchall()
    
    cursor.execute("SELECT id, name FROM teachers")
    teachers_list = cursor.fetchall()
    
    lesson_count = 0
    for class_id, class_name in class_groups:
        for subject_id, subject_name, subject_code in subjects_list:
            # Assign random teacher
            teacher_id = teachers_list[lesson_count % len(teachers_list)][0]
            
            cursor.execute("""
                INSERT INTO lessons (lessons_per_week, length_per_lesson) 
                VALUES (?, ?)
            """, (3, 60))
            
            lesson_id = cursor.lastrowid
            
            # Link lesson to subject, teacher, and class
            cursor.execute("INSERT INTO lesson_subjects (lesson_id, subject_id) VALUES (?, ?)", (lesson_id, subject_id))
            cursor.execute("INSERT INTO lesson_teachers (lesson_id, teacher_id) VALUES (?, ?)", (lesson_id, teacher_id))
            cursor.execute("INSERT INTO lesson_class_groups (lesson_id, class_group_id) VALUES (?, ?)", (lesson_id, class_id))
            
            lesson_count += 1
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ COMPLETE SETUP CREATED!")
    print(f"📊 Summary:")
    print(f"   - Classes: {len(classes)}")
    print(f"   - Teachers: {len(teachers)}")
    print(f"   - Subjects: {len(subjects)}")
    print(f"   - Rooms: {len(rooms)}")
    print(f"   - Lessons: {lesson_count}")
    print(f"   - Time Slots: {len(days) * len(times)}")
    print(f"\n🎯 Now you can generate timetables!")

if __name__ == '__main__':
    create_complete_setup()