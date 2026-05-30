
import json
import os

def audit():
    path = "load_factor_detailed.json"
    if not os.path.exists(path):
        print("File not found.")
        return

    # Try different encodings due to Windows redirection issues
    data = None
    for enc in ["utf-16", "utf-8", "latin-1"]:
        try:
            with open(path, "r", encoding=enc) as f:
                content = f.read()
                data = json.loads(content)
                print(f"Loaded with {enc}")
                break
        except Exception as e:
            continue

    if not data:
        print("Failed to load JSON.")
        return

    summary = data.get("summary", {})
    print(f"Summary: {summary}")

    teachers = data.get("teachers", [])
    print(f"\nAudit: {len(teachers)} Teachers")
    
    # Sort teachers by load to see high/low outliers
    sorted_teachers = sorted(teachers, key=lambda x: x.get("total_periods", 0), reverse=True)
    for t in sorted_teachers[:10]:
        print(f"  - {t['name']}: {t['total_periods']} periods")
        for c in t.get("courses_detail", []):
            print(f"    * {c['course_name']} ({c['class_division']}): T={c.get('theory_hours')} P={c.get('practical_hours')} Total={c.get('total_load')}")

    classes = data.get("classes", [])
    print(f"\nAudit: {len(classes)} Classes")
    for c in classes:
        print(f"  - {c['name']}: {c['total_periods']} periods")

if __name__ == "__main__":
    audit()
