"""
Create a REALISTIC curriculum where each class section has different subjects
based on their year/specialization, filling all 25 slots per section.
"""
import sqlite3
import requests

API_BASE = "http://localhost:8000/api"

conn = sqlite3.connect('backend/timetable.db')
cursor = conn.cursor()

print("=== CREATING REALISTIC CURRICULUM ===\n")

# Clear everything
print("Step 1: Clearing database...")
cursor.execute("DELETE FROM timetable_entries")
cursor.execute("DELETE FROM timetable_versions")
cursor.execute("DELETE FROM lesson_subjects")
cursor.execute("DELETE FROM lesson_class_groups")
cursor.execute("DELETE FROM lesson_teachers")
cursor.execute("DELETE FROM lessons")
cursor.execute("DELETE FROM subjects")
cursor.execute("DELETE FROM teachers WHERE id > 3")
conn.commit()
print("✓ Cleared\n")

# Get class groups
cursor.execute("SELECT id, name FROM class_groups ORDER BY name")
class_groups = cursor.fetchall()

# Create teachers
teachers_data = [
    ("Dr. Rajesh Kumar", "rajesh.kumar@college.edu"),
    ("Prof. Priya Sharma", "priya.sharma@college.edu"),
    ("Dr. Amit Patel", "amit.patel@college.edu"),
    ("Dr. Sneha Desai", "sneha.desai@college.edu"),
    ("Prof. Vikram Singh", "vikram.singh@college.edu"),
    ("Dr. Anita Rao", "anita.rao@college.edu"),
    ("Prof. Rahul Mehta", "rahul.mehta@college.edu"),
    ("Dr. Kavita Joshi", "kavita.joshi@college.edu"),
]

print("Step 2: Creating teachers...")
teacher_ids = {}
for name, email in teachers_data:
    try:
        response = requests.post(f"{API_BASE}/teachers/", json={
            "name": name,
            "email": email,
            "max_hours_per_week": 25
        })
        if response.status_code == 200:
            teacher_ids[name] = response.json()["id"]
            print(f"✓ {name}")
        else:
            cursor.execute("SELECT id FROM teachers WHERE email = ?", (email,))
            result = cursor.fetchone()
            if result:
                teacher_ids[name] = result[0]
    except:
        pass

print(f"\nTotal Teachers: {len(teacher_ids)}\n")

# Define curriculum by year/specialization
# SE = Second Year, TE = Third Year, BE = Fourth Year
# Each class gets 5 subjects, each subject scheduled 5 times per week = 25 slots filled

curricula = {
    "SE": [  # Second Year - 5 core subjects
        ("Data Structures", "SE-DS", 4),
        ("Database Systems", "SE-DB", 4),
        ("Operating Systems", "SE-OS", 4),
        ("Computer Networks", "SE-CN", 4),
        ("Web Technologies", "SE-WT", 4),
        ("DS Lab", "SE-DSL", 2),
        ("DB Lab", "SE-DBL", 3),
    ],
    "TE": [  # Third Year - 5 advanced subjects
        ("Machine Learning", "TE-ML", 4),
        ("Artificial Intelligence", "TE-AI", 4),
        ("Software Engineering", "TE-SE", 4),
        ("Cloud Computing", "TE-CC", 4),
        ("Cyber Security", "TE-CS", 4),
        ("ML Lab", "TE-MLL", 3),
        ("AI Lab", "TE-AIL", 2),
    ],
    "BE": [  # Fourth Year - 5 elective subjects
        ("Big Data Analytics", "BE-BDA", 4),
        ("Blockchain", "BE-BC", 4),
        ("IoT Systems", "BE-IOT", 4),
        ("NLP", "BE-NLP", 4),
        ("Data Science", "BE-DS", 4),
        ("Project Work", "BE-PROJ", 3),
        ("Seminar", "BE-SEM", 2),
    ]
}

# Create subjects and assign to appropriate classes
print("Step 3: Creating subjects and lessons...\n")

teacher_list = list(teacher_ids.values())
subject_count = 0
lesson_count = 0

for year_prefix, subjects_list in curricula.items():
    print(f"--- {year_prefix} Curriculum ---")
    
    # Create subjects for this year
    year_subjects = {}
    for subj_name, subj_code, periods_per_week in subjects_list:
        teacher_id = teacher_list[subject_count % len(teacher_list)]
        
        try:
            response = requests.post(f"{API_BASE}/subjects/", json={
                "name": subj_name,
                "code": subj_code,
                "is_lab": "Lab" in subj_name,
                "credits": 4,
                "required_room_type": "ComputerLab" if "Lab" in subj_name else "LectureHall",
                "duration_slots": 1,
                "teacher_id": teacher_id
            })
            if response.status_code == 200:
                subject_id = response.json()["id"]
                year_subjects[subj_code] = (subject_id, teacher_id, periods_per_week)
                subject_count += 1
                print(f"  ✓ Created: {subj_name} ({subj_code})")
        except Exception as e:
            print(f"  ✗ Error creating {subj_name}: {e}")
    
    # Assign these subjects to matching class groups
    matching_groups = [(gid, gname) for gid, gname in class_groups if gname.startswith(year_prefix)]
    
    for group_id, group_name in matching_groups:
        print(f"\n  Assigning to {group_name}...")
        for subj_code, (subject_id, teacher_id, periods_per_week) in year_subjects.items():
            try:
                response = requests.post(f"{API_BASE}/lessons/", json={
                    "teacher_ids": [teacher_id],
                    "class_group_ids": [group_id],
                    "subject_ids": [subject_id],
                    "lessons_per_week": periods_per_week,
                    "length_per_lesson": 1
                })
                if response.status_code == 200:
                    lesson_count += 1
            except Exception as e:
                print(f"    ✗ Error: {e}")
        
        # Calculate total periods
        total_periods = sum(ppw for _, (_, _, ppw) in year_subjects.items())
        print(f"    ✓ Total periods/week: {total_periods}")
    
    print()

print(f"✓ Created {subject_count} subjects")
print(f"✓ Created {lesson_count} lessons\n")

# Generate timetable
print("Step 4: Generating timetable...")
try:
    response = requests.post(f"{API_BASE}/solvers/generate", 
                            params={"method": "csp"},
                            data={"name": "Realistic Curriculum"})
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Generation started! Version ID: {result.get('id')}\n")
    else:
        print(f"✗ Failed: {response.text}\n")
except Exception as e:
    print(f"✗ Error: {e}\n")

conn.close()

print("="*70)
print("✅ SETUP COMPLETE!")
print("="*70)
print(f"\n⏳ Wait 15-20 seconds, then run:")
print(f"   python calculate_teacher_load.py")
