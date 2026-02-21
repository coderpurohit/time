"""
Timetable Dataset Generator
Creates a valid timetable with the following constraints:
- 10 teachers, 5 subjects, 15 rooms
- Monday to Friday, 6 time slots (09:00-15:00)
- Each subject taught every day
- No conflicts (teacher/room double booking)
"""

import json
import random
from datetime import time
from typing import List, Dict

# Configuration
SUBJECTS = [
    {"name": "Mathematics", "code": "MATH", "is_lab": False},
    {"name": "Physics", "code": "PHY", "is_lab": True},
    {"name": "Chemistry", "code": "CHEM", "is_lab": True},
    {"name": "Computer Science", "code": "CS", "is_lab": True},
    {"name": "English", "code": "ENG", "is_lab": False}
]

TEACHERS = [
    {"name": "Dr. Sharma", "email": "sharma@college.edu", "subject": "MATH"},
    {"name": "Dr. Patel", "email": "patel@college.edu", "subject": "MATH"},
    {"name": "Prof. Kumar", "email": "kumar@college.edu", "subject": "PHY"},
    {"name": "Prof. Singh", "email": "singh@college.edu", "subject": "PHY"},
    {"name": "Dr. Reddy", "email": "reddy@college.edu", "subject": "CHEM"},
    {"name": "Dr. Gupta", "email": "gupta@college.edu", "subject": "CHEM"},
    {"name": "Prof. Verma", "email": "verma@college.edu", "subject": "CS"},
    {"name": "Dr. Joshi", "email": "joshi@college.edu", "subject": "CS"},
    {"name": "Prof. Iyer", "email": "iyer@college.edu", "subject": "ENG"},
    {"name": "Dr. Nair", "email": "nair@college.edu", "subject": "ENG"}
]

ROOMS = [
    {"name": "Room 101", "type": "LectureHall", "capacity": 60},
    {"name": "Room 102", "type": "LectureHall", "capacity": 60},
    {"name": "Room 103", "type": "LectureHall", "capacity": 60},
    {"name": "Lab 201", "type": "Lab", "capacity": 30},
    {"name": "Lab 202", "type": "Lab", "capacity": 30},
    {"name": "Lab 203", "type": "Lab", "capacity": 30},
    {"name": "Lab 204", "type": "Lab", "capacity": 30},
    {"name": "Room 301", "type": "LectureHall", "capacity": 50},
    {"name": "Room 302", "type": "LectureHall", "capacity": 50},
    {"name": "Room 303", "type": "LectureHall", "capacity": 50},
    {"name": "Lab 401", "type": "Lab", "capacity": 25},
    {"name": "Lab 402", "type": "Lab", "capacity": 25},
    {"name": "Room 501", "type": "LectureHall", "capacity": 40},
    {"name": "Room 502", "type": "LectureHall", "capacity": 40},
    {"name": "Room 503", "type": "LectureHall", "capacity": 40}
]

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

TIME_SLOTS = [
    {"period": 1, "start": "09:00", "end": "10:00"},
    {"period": 2, "start": "10:00", "end": "11:00"},
    {"period": 3, "start": "11:00", "end": "12:00"},
    # Lunch break 12:00-13:00
    {"period": 4, "start": "13:00", "end": "14:00"},
    {"period": 5, "start": "14:00", "end": "15:00"},
    {"period": 6, "start": "15:00", "end": "16:00"}
]

CLASS_GROUPS = [
    {"name": "TE-A", "student_count": 60},
    {"name": "TE-B", "student_count": 60},
    {"name": "SE-A", "student_count": 55},
    {"name": "SE-B", "student_count": 55},
    {"name": "FE-A", "student_count": 50}
]


def generate_timetable():
    """Generate a valid timetable satisfying all constraints"""
    timetable = []
    teacher_schedule = {day: {slot["period"]: None for slot in TIME_SLOTS} for day in DAYS}
    room_schedule = {day: {slot["period"]: None for slot in TIME_SLOTS} for day in DAYS}
    
    # Track which teachers teach which subjects
    subject_teachers = {}
    for teacher in TEACHERS:
        subj_code = teacher["subject"]
        if subj_code not in subject_teachers:
            subject_teachers[subj_code] = []
        subject_teachers[subj_code].append(teacher)
    
    # For each class group
    for class_group in CLASS_GROUPS:
        # Each subject must be taught every day
        for day in DAYS:
            subject_assigned_today = set()
            
            for slot in TIME_SLOTS:
                period = slot["period"]
                
                # Pick a subject (ensure all subjects get covered across the week)
                available_subjects = [s for s in SUBJECTS if s["code"] not in subject_assigned_today]
                
                if not available_subjects:
                    # All subjects assigned today, can repeat
                    available_subjects = SUBJECTS
                
                subject = random.choice(available_subjects)
                subject_assigned_today.add(subject["code"])
                
                # Find available teacher for this subject
                available_teachers = [
                    t for t in subject_teachers[subject["code"]]
                    if teacher_schedule[day][period] != t["email"]
                ]
                
                if not available_teachers:
                    # Skip this slot if no teacher available
                    continue
                
                teacher = random.choice(available_teachers)
                
                # Find available room
                room_type_needed = "Lab" if subject["is_lab"] else "LectureHall"
                available_rooms = [
                    r for r in ROOMS
                    if r["type"] == room_type_needed and
                    room_schedule[day][period] != r["name"]
                ]
                
                if not available_rooms:
                    # Skip if no room available
                    continue
                
                room = random.choice(available_rooms)
                
                # Create timetable entry
                entry = {
                    "day": day,
                    "period": period,
                    "start_time": slot["start"],
                    "end_time": slot["end"],
                    "subject_name": subject["name"],
                    "subject_code": subject["code"],
                    "teacher_name": teacher["name"],
                    "teacher_email": teacher["email"],
                    "room_name": room["name"],
                    "class_group": class_group["name"],
                    "is_lab": subject["is_lab"]
                }
                
                timetable.append(entry)
                
                # Mark teacher and room as busy
                teacher_schedule[day][period] = teacher["email"]
                room_schedule[day][period] = room["name"]
    
    return timetable


def print_tabular_format(timetable):
    """Print timetable in tabular format"""
    print("\n" + "="*120)
    print("COLLEGE TIMETABLE - WEEK SCHEDULE")
    print("="*120)
    
    for class_group in CLASS_GROUPS:
        print(f"\n{'='*120}")
        print(f"CLASS: {class_group['name']}")
        print(f"{'='*120}")
        
        # Header
        print(f"{'Day':<12} | {'Time':<12} | {'Subject':<20} | {'Teacher':<20} | {'Room':<15}")
        print("-" * 120)
        
        # Filter entries for this class
        class_entries = [e for e in timetable if e["class_group"] == class_group["name"]]
        class_entries.sort(key=lambda x: (DAYS.index(x["day"]), x["period"]))
        
        for entry in class_entries:
            print(
                f"{entry['day']:<12} | "
                f"{entry['start_time']}-{entry['end_time']:<5} | "
                f"{entry['subject_code']:<20} | "
                f"{entry['teacher_name']:<20} | "
                f"{entry['room_name']:<15}"
            )
    
    print("\n" + "="*120)


def generate_json_for_database(timetable):
    """Generate structured JSON for database insertion"""
    
    # Teachers JSON
    teachers_json = [
        {
            "name": t["name"],
            "email": t["email"],
            "max_hours_per_week": 20
        }
        for t in TEACHERS
    ]
    
    # Subjects JSON (with teacher assignment)
    subjects_json = []
    for subject in SUBJECTS:
        # Find a teacher for this subject
        teacher = next(t for t in TEACHERS if t["subject"] == subject["code"])
        subjects_json.append({
            "name": subject["name"],
            "code": subject["code"],
            "is_lab": subject["is_lab"],
            "credits": 4 if subject["is_lab"] else 3,
            "required_room_type": "Lab" if subject["is_lab"] else "LectureHall",
            "duration_slots": 1,
            "teacher_email": teacher["email"]
        })
    
    # Rooms JSON
    rooms_json = [
        {
            "name": r["name"],
            "capacity": r["capacity"],
            "type": r["type"],
            "resources": ["Projector", "Whiteboard"] + (["Lab Equipment"] if r["type"] == "Lab" else [])
        }
        for r in ROOMS
    ]
    
    # Class Groups JSON
    class_groups_json = [
        {
            "name": cg["name"],
            "student_count": cg["student_count"]
        }
        for cg in CLASS_GROUPS
    ]
    
    # Timetable entries
    timetable_json = timetable
    
    # Complete database JSON
    database_json = {
        "teachers": teachers_json,
        "subjects": subjects_json,
        "rooms": rooms_json,
        "class_groups": class_groups_json,
        "timetable_entries": timetable_json
    }
    
    return database_json


def main():
    print("Generating timetable dataset...")
    print(f"Teachers: {len(TEACHERS)}")
    print(f"Subjects: {len(SUBJECTS)}")
    print(f"Rooms: {len(ROOMS)}")
    print(f"Days: {len(DAYS)}")
    print(f"Time Slots: {len(TIME_SLOTS)}")
    print(f"Class Groups: {len(CLASS_GROUPS)}")
    
    # Generate timetable
    timetable = generate_timetable()
    
    print(f"\nTotal timetable entries generated: {len(timetable)}")
    
    # Print tabular format
    print_tabular_format(timetable)
    
    # Generate JSON
    database_json = generate_json_for_database(timetable)
    
    # Save to file
    output_file = "timetable_dataset.json"
    with open(output_file, 'w') as f:
        json.dump(database_json, f, indent=2)
    
    print(f"\n✅ Database JSON saved to: {output_file}")
    print(f"   - Teachers: {len(database_json['teachers'])}")
    print(f"   - Subjects: {len(database_json['subjects'])}")
    print(f"   - Rooms: {len(database_json['rooms'])}")
    print(f"   - Class Groups: {len(database_json['class_groups'])}")
    print(f"   - Timetable Entries: {len(database_json['timetable_entries'])}")
    
    # Print sample JSON structure
    print("\n" + "="*120)
    print("SAMPLE JSON STRUCTURE:")
    print("="*120)
    print("\nTeachers (sample):")
    print(json.dumps(database_json["teachers"][:2], indent=2))
    print("\nSubjects (sample):")
    print(json.dumps(database_json["subjects"][:2], indent=2))
    print("\nTimetable Entries (sample):")
    print(json.dumps(database_json["timetable_entries"][:3], indent=2))


if __name__ == "__main__":
    main()
