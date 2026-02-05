
import sys
import os

# Add backend to path so we can import app modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.domain.entities.all_entities import Teacher, Subject, Room, ClassGroup, TimeSlot
from app.solver.csp_solver import CspTimetableSolver
from app.solver.genetic_solver import GeneticTimetableSolver

def test_solvers():
    print(">>> Setting up Dummy AI-DS Data...")
    
    # 1. Teachers
    teachers = [
        Teacher(id=1, name="Dr. AI", email="ai@ds.com", max_hours_per_week=10),
        Teacher(id=2, name="Prof. ML", email="ml@ds.com", max_hours_per_week=10),
        Teacher(id=3, name="Mr. Python", email="py@ds.com", max_hours_per_week=10)
    ]

    # 2. Rooms
    rooms = [
        Room(id=1, name="LH-101", capacity=60, type="LectureHall"),
        Room(id=2, name="Lab-1", capacity=30, type="Lab", resources=["PCs", "GPU"])
    ]

    # 3. Subjects
    subjects = [
        Subject(id=1, name="Data Structures", code="DS101", is_lab=False, credits=3, required_room_type="LectureHall", teacher_id=3),
        Subject(id=2, name="AI Theory", code="AI201", is_lab=False, credits=3, required_room_type="LectureHall", teacher_id=1),
        Subject(id=3, name="ML Lab", code="ML201L", is_lab=True, credits=1, required_room_type="Lab", duration_slots=1, teacher_id=2)
    ]

    # 4. Groups
    groups = [
        ClassGroup(id=1, name="SE-AI-DS", student_count=50)
    ]

    # 5. Slots (Morning session only for test)
    slots = [
        TimeSlot(id=1, day="Mon", period=1, start_time="09:00", end_time="10:00"),
        TimeSlot(id=2, day="Mon", period=2, start_time="10:00", end_time="11:00"),
        TimeSlot(id=3, day="Mon", period=3, start_time="11:00", end_time="12:00"),
    ]

    print("\n>>> Testing CSP Solver (Hard Constraints)...")
    csp = CspTimetableSolver(teachers, subjects, rooms, groups, slots)
    result_csp = csp.solve()
    
    if result_csp:
        print("✅ CSP Solution Found!")
        for entry in result_csp:
            s_name = next(s.name for s in subjects if s.id == entry['subject_id'])
            r_name = next(r.name for r in rooms if r.id == entry['room_id'])
            t_slug = next(f"{t.day} P{t.period}" for t in slots if t.id == entry['time_slot_id'])
            print(f"  - {t_slug}: {s_name} in {r_name}")
    else:
        print("❌ CSP Failed to find solution.")

    print("\n>>> Testing Genetic Solver (Optimization)...")
    ga = GeneticTimetableSolver(teachers, subjects, rooms, groups, slots, pop_size=10, generations=5)
    result_ga = ga.generate()
    
    if result_ga:
        print("✅ GA Solution Generated!")
        # GA returns a list of dicts directly
        print(f"  - First 2 entries: {result_ga[:2]}")
    else:
        print("❌ GA Failed.")

if __name__ == "__main__":
    test_solvers()
