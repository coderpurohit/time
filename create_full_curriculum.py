"""
Create a complete curriculum with enough subjects to fill all 25 time slots
for each class section, then calculate teacher load factors.
"""
import sqlite3
import requests

API_BASE = "http://localhost:8000/api"

# Connect to database
conn = sqlite3.connect('backend/timetable.db')
cursor = conn.cursor()

print("=== CREATING FULL CURRICULUM ===\n")

# Get current data
cursor.execute("SELECT id, name FROM class_groups")
class_groups = cursor.fetchall()
print(f"Class Groups: {len(class_groups)}")

cursor.execute("SELECT COUNT(*) FROM time_slots WHERE is_break = 0")
available_slots = cursor.fetchone()[0]
print(f"Available Teaching Slots: {available_slots}")

# Define a comprehensive curriculum (typical college subjects)
subjects_data = [
    # Core CS subjects
    ("Data Structures & Algorithms", "CS201", False, 4, "LectureHall"),
    ("Database Management Systems", "CS202", False, 4, "LectureHall"),
    ("Machine Learning", "CS203", False, 4, "LectureHall"),
    ("Operating Systems", "CS204", False, 4, "LectureHall"),
    ("Computer Networks", "CS205", False, 4, "LectureHall"),
    ("Software Engineering", "CS206", False, 3, "LectureHall"),
    ("Web Technologies", "CS207", False, 3, "LectureHall"),
    ("Artificial Intelligence", "CS208", False, 4, "LectureHall"),
    
    # Labs
    ("DBMS Lab", "CS202L", True, 2, "ComputerLab"),
    ("ML Lab", "CS203L", True, 2, "ComputerLab"),
    ("OS Lab", "CS204L", True, 2, "ComputerLab"),
    ("Networks Lab", "CS205L", True, 2, "ComputerLab"),
    ("Web Tech Lab", "CS207L", True, 2, "ComputerLab"),
    
    # Additional subjects
    ("Mathematics III", "MATH301", False, 3, "LectureHall"),
    ("Discrete Mathematics", "MATH302", False, 3, "LectureHall"),
    ("Theory of Computation", "CS301", False, 3, "LectureHall"),
    ("Compiler Design", "CS302", False, 3, "LectureHall"),
    ("Cloud Computing", "CS303", False, 3, "LectureHall"),
    ("Cyber Security", "CS304", False, 3, "LectureHall"),
    ("Mobile App Development", "CS305", False, 3, "LectureHall"),
    
    # Electives
    ("Data Science", "CS401", False, 3, "LectureHall"),
    ("Blockchain Technology", "CS402", False, 3, "LectureHall"),
    ("IoT Systems", "CS403", False, 3, "LectureHall"),
    ("Big Data Analytics", "CS404", False, 3, "LectureHall"),
    ("Natural Language Processing", "CS405", False, 3, "LectureHall"),
]

# Create more teachers to handle the load
teachers_data = [
    ("Dr. Rajesh Kumar", "rajesh.kumar@college.edu", 25),
    ("Prof. Priya Sharma", "priya.sharma@college.edu", 25),
    ("Dr. Amit Patel", "amit.patel@college.edu", 25),
    ("Dr. Sneha Desai", "sneha.desai@college.edu", 25),
    ("Prof. Vikram Singh", "vikram.singh@college.edu", 25),
    ("Dr. Anita Rao", "anita.rao@college.edu", 25),
    ("Prof. Rahul Mehta", "rahul.mehta@college.edu", 25),
    ("Dr. Kavita Joshi", "kavita.joshi@college.edu", 25),
    ("Prof. Suresh Nair", "suresh.nair@college.edu", 25),
    ("Dr. Pooja Gupta", "pooja.gupta@college.edu", 25),
    ("Prof. Arun Kumar", "arun.kumar@college.edu", 25),
    ("Dr. Meera Iyer", "meera.iyer@college.edu", 25),
    ("Prof. Kiran Reddy", "kiran.reddy@college.edu", 25),
    ("Dr. Deepak Shah", "deepak.shah@college.edu", 25),
    ("Prof. Nisha Verma", "nisha.verma@college.edu", 25),
]

print("\n=== STEP 1: Clear existing data ===")
cursor.execute("DELETE FROM timetable_entries")
cursor.execute("DELETE FROM timetable_versions")
cursor.execute("DELETE FROM lesson_subjects")
cursor.execute("DELETE FROM lesson_class_groups")
cursor.execute("DELETE FROM lesson_teachers")
cursor.execute("DELETE FROM lessons")
cursor.execute("DELETE FROM subjects")
cursor.execute("DELETE FROM teachers WHERE id > 3")  # Keep first 3 teachers
conn.commit()
print("✓ Cleared old data")

print("\n=== STEP 2: Create Teachers ===")
teacher_ids = {}
for name, email, max_hours in teachers_data:
    try:
        response = requests.post(f"{API_BASE}/teachers/", json={
            "name": name,
            "email": email,
            "max_hours_per_week": max_hours,
            "available_slots": []
        })
        if response.status_code == 200:
            teacher_id = response.json()["id"]
            teacher_ids[name] = teacher_id
            print(f"✓ Created: {name} (ID: {teacher_id})")
        else:
            # Teacher might already exist, get from DB
            cursor.execute("SELECT id FROM teachers WHERE email = ?", (email,))
            result = cursor.fetchone()
            if result:
                teacher_ids[name] = result[0]
                print(f"✓ Exists: {name} (ID: {result[0]})")
    except Exception as e:
        print(f"✗ Error creating {name}: {e}")

print(f"\nTotal Teachers: {len(teacher_ids)}")

print("\n=== STEP 3: Create Subjects ===")
subject_ids = {}
teacher_names = list(teacher_ids.keys())
for i, (name, code, is_lab, credits, room_type) in enumerate(subjects_data):
    # Assign teachers in round-robin fashion
    teacher_name = teacher_names[i % len(teacher_names)]
    teacher_id = teacher_ids[teacher_name]
    
    try:
        response = requests.post(f"{API_BASE}/subjects/", json={
            "name": name,
            "code": code,
            "is_lab": is_lab,
            "credits": credits,
            "required_room_type": room_type,
            "duration_slots": 1,
            "teacher_id": teacher_id
        })
        if response.status_code == 200:
            subject_id = response.json()["id"]
            subject_ids[code] = subject_id
            print(f"✓ Created: {name} ({code}) - Teacher: {teacher_name}")
    except Exception as e:
        print(f"✗ Error creating {name}: {e}")

print(f"\nTotal Subjects: {len(subject_ids)}")

print("\n=== STEP 4: Create Lessons (Subject-Class Mappings) ===")
# For each class group, assign all subjects
lesson_count = 0
for group_id, group_name in class_groups:
    print(f"\nCreating lessons for {group_name}...")
    
    for code, subject_id in subject_ids.items():
        # Get teacher for this subject
        cursor.execute("SELECT teacher_id FROM subjects WHERE id = ?", (subject_id,))
        teacher_id = cursor.fetchone()[0]
        
        try:
            response = requests.post(f"{API_BASE}/lessons/", json={
                "teacher_ids": [teacher_id],
                "class_group_ids": [group_id],
                "subject_ids": [subject_id],
                "lessons_per_week": 1,
                "length_per_lesson": 1
            })
            if response.status_code == 200:
                lesson_count += 1
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    print(f"  ✓ Created {len(subject_ids)} lessons for {group_name}")

print(f"\n✓ Total Lessons Created: {lesson_count}")

print("\n=== STEP 5: Generate Timetable ===")
try:
    response = requests.post(f"{API_BASE}/solvers/generate", 
                            params={"method": "csp"},
                            data={"name": "Complete Curriculum Timetable"})
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Timetable generation started!")
        print(f"  Version ID: {result.get('id')}")
        print(f"  Status: {result.get('status')}")
    else:
        print(f"✗ Generation failed: {response.text}")
except Exception as e:
    print(f"✗ Error: {e}")

print("\n=== SUMMARY ===")
print(f"Teachers: {len(teacher_ids)}")
print(f"Subjects: {len(subject_ids)}")
print(f"Class Groups: {len(class_groups)}")
print(f"Lessons: {lesson_count}")
print(f"Required Slots per Class: {len(subject_ids)}")
print(f"Available Slots: {available_slots}")
print(f"Feasible: {'YES' if available_slots >= len(subject_ids) else 'NO'}")

conn.close()

print("\n✓ Setup complete! Wait 10-15 seconds for generation to finish.")
print("Then refresh the timetable page and select any class to see full schedule.")
