import requests

API_BASE = "http://localhost:8000/api"

print("=" * 60)
print("KEEP ONLY NEW 15 TEACHERS - AUTOMATED")
print("=" * 60)

# Get all teachers
print("\n1. Fetching all teachers...")
response = requests.get(f"{API_BASE}/teachers/")
all_teachers = response.json()
print(f"   Total teachers: {len(all_teachers)}")

# Sort by ID (assuming newer teachers have higher IDs)
all_teachers.sort(key=lambda t: t['id'])

# Keep last 15, delete the rest
if len(all_teachers) <= 15:
    print(f"\n   You have {len(all_teachers)} teachers. No deletion needed.")
    exit()

teachers_to_keep = all_teachers[-15:]  # Last 15
teachers_to_delete = all_teachers[:-15]  # All except last 15

print(f"\n2. Will KEEP these {len(teachers_to_keep)} teachers:")
for t in teachers_to_keep:
    print(f"   ✓ ID {t['id']}: {t['name']}")

print(f"\n3. Will DELETE these {len(teachers_to_delete)} teachers:")
for t in teachers_to_delete:
    print(f"   ✗ ID {t['id']}: {t['name']}")

# Get subjects and lessons
print("\n4. Fetching subjects and lessons...")
subjects = requests.get(f"{API_BASE}/subjects/").json()
lessons = requests.get(f"{API_BASE}/lessons/").json()

old_teacher_ids = [t['id'] for t in teachers_to_delete]

# Reassign subjects
print("\n5. Reassigning subjects...")
subjects_to_update = [s for s in subjects if s.get('teacher_id') in old_teacher_ids]
for i, subject in enumerate(subjects_to_update):
    new_teacher = teachers_to_keep[i % len(teachers_to_keep)]
    print(f"   {subject['name']}: {subject.get('teacher_id')} → {new_teacher['id']} ({new_teacher['name']})")
    subject['teacher_id'] = new_teacher['id']
    requests.put(f"{API_BASE}/subjects/{subject['id']}", json=subject)

# Reassign lessons
print("\n6. Reassigning lessons...")
lessons_to_update = [l for l in lessons if l.get('teacher_id') in old_teacher_ids]
for i, lesson in enumerate(lessons_to_update):
    new_teacher = teachers_to_keep[i % len(teachers_to_keep)]
    print(f"   Lesson {lesson['id']}: {lesson.get('teacher_id')} → {new_teacher['id']} ({new_teacher['name']})")
    lesson['teacher_id'] = new_teacher['id']
    requests.put(f"{API_BASE}/lessons/{lesson['id']}", json=lesson)

# Delete old teachers
print("\n7. Deleting old teachers...")
confirm = input(f"\n   Delete {len(teachers_to_delete)} old teachers? (yes/no): ").strip().lower()

if confirm == 'yes':
    for teacher in teachers_to_delete:
        print(f"   Deleting: {teacher['name']} (ID {teacher['id']})")
        response = requests.delete(f"{API_BASE}/teachers/{teacher['id']}")
        if response.status_code == 200:
            print(f"     ✓ Deleted")
        else:
            print(f"     ✗ Failed")
    
    print("\n✅ DONE! You now have only your 15 new teachers.")
    print("   Go to the timetable page and click 'Generate New Schedule'")
else:
    print("\n   Cancelled. No teachers were deleted.")

print("=" * 60)
