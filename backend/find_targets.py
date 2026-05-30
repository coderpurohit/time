from app.infrastructure.database import SessionLocal
from app.infrastructure import models

def find_targets():
    db = SessionLocal()
    try:
        results = {}
        
        # Teachers
        teachers = db.query(models.Teacher).all()
        t_map = {t.name.lower(): t.id for t in teachers}
        
        target_teachers = [
            ("kottawar", "Dr. V. G. Kottawar"),
            ("sharma", "Dr. Manish Sharma"),
            ("gothane", "Dr. Suvarna S. Gothane")
        ]
        
        print("TEACHERS FOUND:")
        for key, name in target_teachers:
            found = [t for t in teachers if key in t.name.lower()]
            for t in found:
                print(f"  {t.name} -> ID: {t.id}")
                results[f"teacher_{key}"] = t.id

        # Subjects
        subjects = db.query(models.Subject).all()
        print("\nSUBJECTS SEARCH:")
        
        search_terms = {
            "ptc": ["professional", "technical", "communication"],
            "se": ["sustainable", "energy", "development"],
            "ep": ["engineering", "physics"]
        }
        
        for key, terms in search_terms.items():
            print(f"Search for {key} ({terms}):")
            matches = []
            for s in subjects:
                if all(term in s.name.lower() for term in terms):
                    matches.append(s)
                elif key == "se" and "sustainable" in s.name.lower(): # Relaxed search for SE
                    matches.append(s)
                elif key == "ep" and "physics" in s.name.lower(): # Relaxed search for EP
                    matches.append(s)
                    
            for s in matches:
                teacher_name = next((t.name for t in teachers if t.id == s.teacher_id), "None")
                print(f"  ID: {s.id}, Name: '{s.name}', Teacher: {teacher_name} (ID: {s.teacher_id}), is_lab: {s.is_lab}, duration: {s.duration_slots}")

        # Labs
        labs = [s for s in subjects if s.is_lab]
        print("\nLABS WITH INCORRECT DURATION (not 2):")
        for l in labs:
            if l.duration_slots != 2:
                print(f"  ID: {l.id}, Name: '{l.name}', duration: {l.duration_slots}")
        
    finally:
        db.close()

if __name__ == "__main__":
    find_targets()
