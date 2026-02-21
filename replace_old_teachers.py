import requests
import json

API_BASE = "http://localhost:8000/api"

print("=" * 60)
print("TEACHER REPLACEMENT SCRIPT")
print("=" * 60)

# Step 1: Get all teachers
print("\n1. Fetching all teachers...")
response = requests.get(f"{API_BASE}/teachers/")
all_teachers = response.json()
print(f"   Total teachers: {len(all_teachers)}")

# Display all teachers with their IDs
print("\n   Current teachers:")
for teacher in all_teachers:
    print(f"   - ID {teacher['id']}: {teacher['name']} ({teacher['email']})")

# Step 2: Identify old vs new teachers
print("\n2. Identifying old teachers to remove...")
print("   Enter the IDs of OLD teachers to DELETE (comma-separated):")
print("   Example: 1,2,3,4,5")
old_teacher_ids = input("   IDs to delete: ").strip()

if not old_teacher_ids:
    print("   No teachers selected for deletion. Exiting.")
    exit()

old_ids = [int(id.strip()) for id in old_teacher_ids.split(',')]
print(f"   Will delete {len(old_ids)} teachers: {old_ids}")

# Step 3: Get all subjects/lessons
print("\n3. Fetching subjects and lessons...")
subjects_response = requests.get(f"{API_BASE}/subjects/")
subjects = subjects_response.json()
print(f"   Total subjects: {len(subjects)}")

lessons_response = requests.get(f"{API_BASE}/lessons/")
lessons = lessons_response.json()
print(f"   Total lessons: {len(lessons)}")

# Step 4: Get new teachers (those not in old_ids)
new_teachers = [t for t in all_teachers if t['id'] not in old_ids]
print(f"\n4. New teachers available for assignment: {len(new_teachers)}")
for teacher in new_teachers:
    print(f"   - ID {teacher['id']}: {teacher['name']}")

if len(new_teachers) == 0:
    print("   ERROR: No new teachers available! Add teachers first.")
    exit()

# Step 5: Reassign subjects from old teachers to new teachers
print("\n5. Reassigning subjects to new teachers...")
subjects_to_update = [s for s in subjects if s.get('teacher_id') in old_ids]
print(f"   Found {len(subjects_to_update)} subjects assigned to old teachers")

if subjects_to_update:
    print("\n   Reassignment plan:")
    for i, subject in enumerate(subjects_to_update):
        new_teacher = new_teachers[i % len(new_teachers)]  # Round-robin assignment
        print(f"   - {subject['name']} (ID {subject['id']}): Teacher ID {subject.get('teacher_id')} → {new_teacher['id']} ({new_teacher['name']})")
        
        # Update subject
        subject['teacher_id'] = new_teacher['id']
        update_response = requests.put(
            f"{API_BASE}/subjects/{subject['id']}",
            json=subject
        )
        if update_response.status_code == 200:
            print(f"     ✓ Updated")
        else:
            print(f"     ✗ Failed: {update_response.text}")

# Step 6: Reassign lessons from old teachers to new teachers
print("\n6. Reassigning lessons to new teachers...")
lessons_to_update = [l for l in lessons if l.get('teacher_id') in old_ids]
print(f"   Found {len(lessons_to_update)} lessons assigned to old teachers")

if lessons_to_update:
    for i, lesson in enumerate(lessons_to_update):
        new_teacher = new_teachers[i % len(new_teachers)]
        print(f"   - Lesson ID {lesson['id']}: Teacher ID {lesson.get('teacher_id')} → {new_teacher['id']} ({new_teacher['name']})")
        
        # Update lesson
        lesson['teacher_id'] = new_teacher['id']
        update_response = requests.put(
            f"{API_BASE}/lessons/{lesson['id']}",
            json=lesson
        )
        if update_response.status_code == 200:
            print(f"     ✓ Updated")
        else:
            print(f"     ✗ Failed: {update_response.text}")

# Step 7: Delete old teachers
print("\n7. Deleting old teachers...")
confirm = input(f"   Are you sure you want to delete {len(old_ids)} teachers? (yes/no): ").strip().lower()

if confirm == 'yes':
    for teacher_id in old_ids:
        teacher = next((t for t in all_teachers if t['id'] == teacher_id), None)
        if teacher:
            print(f"   Deleting: {teacher['name']} (ID {teacher_id})")
            delete_response = requests.delete(f"{API_BASE}/teachers/{teacher_id}")
            if delete_response.status_code == 200:
                print(f"     ✓ Deleted")
            else:
                print(f"     ✗ Failed: {delete_response.text}")
else:
    print("   Deletion cancelled.")

# Step 8: Verify final state
print("\n8. Final verification...")
final_teachers = requests.get(f"{API_BASE}/teachers/").json()
print(f"   Remaining teachers: {len(final_teachers)}")
for teacher in final_teachers:
    print(f"   - ID {teacher['id']}: {teacher['name']}")

print("\n" + "=" * 60)
print("DONE! Now regenerate your timetable from the web interface.")
print("=" * 60)
