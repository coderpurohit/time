import requests

API = 'http://localhost:8000/api'

# Get data
subjects = requests.get(f'{API}/subjects').json()
classes = requests.get(f'{API}/class-groups').json()
teachers = requests.get(f'{API}/teachers').json()

print(f'Subjects: {len(subjects)}, Classes: {len(classes)}, Teachers: {len(teachers)}')

if subjects and classes and teachers:
    count = 0
    for subject in subjects[:5]:
        for cls in classes[:3]:
            lesson_data = {
                'subject_ids': [subject['id']],
                'class_group_ids': [cls['id']],
                'teacher_ids': [teachers[0]['id']],
                'lessons_per_week': 2,
                'length_per_lesson': 1
            }
            resp = requests.post(f'{API}/lessons', json=lesson_data)
            if resp.status_code == 200:
                count += 1
            else:
                print(f'Error: {resp.status_code} - {resp.text}')
    print(f'Created {count} lessons')
