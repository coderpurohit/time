import requests

API_BASE = "http://localhost:8000/api"

print("=" * 60)
print("AUTO REPLACE OLD TEACHERS WITH NEW 15")
print("=" * 60)

# Get all teachers
print("\n1. Fetching all teachers...")
response = requests.get(f"{API_BASE}/teachers/")
all_teachers = response.json()
print(f"   Total teachers: {len(all_teachers)}")

# Sort by ID
all_teachers.sort(key=lambda t: t['id'])

# Keep last 15
if len(all_teachers) <= 15:
    print(f"\n   You have {len(all_teachers)} teachers. No deletion needed.")
    exit()

teachers_to_keep = all_teachers[-15:]
teachers_to_delete = all_teachers[:-15]

print(f"\n2. Keeping {len(teachers_to_keep)} newest teachers:")
for t in teachers_to_keep:
    print(f"   ✓ {t['name']}")

print(f"\n3. Deleting {len(teachers_to_delete)} old teachers:")
for t in teachers_to_delete:
    print(f"   ✗ {t['name']}")

# Get subjects and lessons
print("\n4. Reassigning subjects and lessons...")
subjects = requests.get(f"{API_BASE}/subjects/").json()
lessons = requests.get(f"{API_BASE}/lessons/").json()

old_ids = [t['id'] for t in teachers_to_delete]

# Reassign subjects
for i, subject in enumerate([s for s in subjects if s.get('teacher_id') in old_ids]):
    new_teacher = teachers_to_keep[i % len(teachers_to_keep)]
    subject['teacher_id'] = new_teacher['id']
    requests.put(f"{API_BASE}/subjects/{subject['id']}", json=subject)
    print(f"   Subject '{subject['name']}' → {new_teacher['name']}")

# Reassign lessons
for i, lesson in enumerate([l for l in lessons if l.get('teacher_id') in old_ids]):
    new_teacher = teachers_to_keep[i % len(teachers_to_keep)]
    lesson['teacher_id'] = new_teacher['id']
    requests.put(f"{API_BASE}/lessons/{lesson['id']}", json=lesson)

# Delete old teachers
print("\n5. Deleting old teachers...")
for teacher in teachers_to_delete:
    requests.delete(f"{API_BASE}/teachers/{teacher['id']}")
    print(f"   ✓ Deleted {teacher['name']}")

print("\n" + "=" * 60)
print("✅ DONE! You now have only your 15 new teachers.")
print("   Refresh the timetable page and generate a new schedule!")
print("=" * 60)
