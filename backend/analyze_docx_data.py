"""Analyze DOCX data to plan DB import - list all unique teachers, subjects, classes"""
import requests

r = requests.post(
    "http://localhost:8000/api/analytics/workload-from-docx/0",
    files={"file": ("load.docx", open("last_uploaded_debug.docx", "rb"), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
)
data = r.json()["data"]

teachers = set()
subjects = set()
classes = set()
lessons = []

for t in data:
    name = t["name"]
    teachers.add(name)
    for c in t.get("courses_detail", []):
        course = c["course_name"]
        subjects.add(course)
        # Parse class divisions: "SE- A,B,C" -> ["SE-A", "SE-B", "SE-C"]
        raw_div = c["class_division"]
        if raw_div:
            # Normalize: "SE- A,B,C" -> prefix="SE-", suffixes=["A","B","C"]
            raw_div = raw_div.replace(" ", "")  # "SE-A,B,C"
            if "-" in raw_div:
                parts = raw_div.split("-", 1)
                prefix = parts[0] + "-"
                suffixes = [s.strip() for s in parts[1].split(",") if s.strip()]
                for s in suffixes:
                    classes.add(prefix + s)
            else:
                classes.add(raw_div)
        lessons.append({"teacher": name, "course": course, "class_div": raw_div, 
                        "theory": c["theory_hours"], "practical": c["practical_hours"]})

print(f"\n=== TEACHERS ({len(teachers)}) ===")
for t in sorted(teachers):
    print(f"  {t}")

print(f"\n=== SUBJECTS ({len(subjects)}) ===")
for s in sorted(subjects):
    print(f"  {s}")

print(f"\n=== CLASSES ({len(classes)}) ===")
for c in sorted(classes):
    print(f"  {c}")

print(f"\n=== LESSONS ({len(lessons)}) ===")
print(f"  Total lesson entries: {len(lessons)}")
