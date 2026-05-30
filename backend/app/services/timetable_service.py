
from sqlalchemy.orm import Session
from ..infrastructure.database import SessionLocal
from ..infrastructure import models
from ..solver.csp_solver import CspTimetableSolver
from ..solver.genetic_solver import GeneticTimetableSolver
from ..solver.constraints.base import HardConstraints
from ..domain.entities.all_entities import Teacher, Subject, Room, ClassGroup, TimeSlot
from fastapi import HTTPException
from collections import Counter, defaultdict
import re

class TimetableService:
    @staticmethod
    def _room_is_lab(room) -> bool:
        room_type = (getattr(room, "type", "") or "").strip().lower()
        return "lab" in room_type

    @staticmethod
    def _preferred_room_sets_for_group(group_name: str):
        name = (group_name or "").upper()
        
        # TE (Third Year) - Rooms 32-35
        if name.startswith("TE-"):
            return {
                "lecture": {"32", "33", "34", "35", "TUTORIAL ROOM", "BOARD ROOM"},
                "lab": {"SL1", "SL2", "SL3", "SL4", "AI LAB", "PROJECT LAB"},
            }
        
        # SE (Second Year) - Rooms 21-25
        if name.startswith("SE-"):
            return {
                "lecture": {"21", "22", "23", "24", "25", "TUTORIAL ROOM", "BOARD ROOM"},
                "lab": {"SL1", "SL2", "SL3", "SL4", "AI LAB", "PROJECT LAB"},
            }
        
        # BE (Final Year) - Rooms 11-12
        if name == "BE-A":
            # BE-A uses Room 12
            return {
                "lecture": {"12", "TUTORIAL ROOM", "BOARD ROOM"},
                "lab": {"SL1", "SL2", "SL3", "SL4", "AI LAB", "PROJECT LAB"},
            }
        if name == "BE-B":
            # BE-B uses Room 11
            return {
                "lecture": {"11", "TUTORIAL ROOM", "BOARD ROOM"},
                "lab": {"SL1", "SL2", "SL3", "SL4", "AI LAB", "PROJECT LAB"},
            }
        if name == "BE-C":
            # BE-C can use either room 11 or 12
            return {
                "lecture": {"11", "12", "TUTORIAL ROOM", "BOARD ROOM"},
                "lab": {"SL1", "SL2", "SL3", "SL4", "AI LAB", "PROJECT LAB"},
            }
        
        # FE (First Year) - can use any available room
        return {
            "lecture": {"11", "12", "21", "22", "23", "24", "25", "32", "33", "34", "35", "TUTORIAL ROOM", "BOARD ROOM"},
            "lab": {"SL1", "SL2", "SL3", "SL4", "AI LAB", "PROJECT LAB"},
        }

    @staticmethod
    def _subject_should_be_lab(subject) -> bool:
        name = (getattr(subject, "name", "") or "").lower()
        room_type = (getattr(subject, "required_room_type", "") or "").lower()
        return bool(
            getattr(subject, "is_lab", False)
            or "lab" in name
            or "laboratory" in name
            or room_type == "lab"
        )

    @staticmethod
    def normalize_subject_rules(db: Session) -> int:
        changed = 0
        for subject in db.query(models.Subject).all():
            should_be_lab = TimetableService._subject_should_be_lab(subject)
            desired_duration = 2 if should_be_lab else 1
            desired_room_type = "Lab" if should_be_lab else "LectureHall"

            if subject.is_lab != should_be_lab:
                subject.is_lab = should_be_lab
                changed += 1
            if subject.duration_slots != desired_duration:
                subject.duration_slots = desired_duration
                changed += 1
            if (subject.required_room_type or "") != desired_room_type:
                subject.required_room_type = desired_room_type
                changed += 1

        if changed:
            db.commit()
            print(f"GENERATOR: Normalized subject scheduling rules. Updated fields={changed}")
        return changed

    @staticmethod
    def _normalize_text(value) -> str:
        return re.sub(r"\s+", " ", str(value or "").strip().lower()).strip()

    @staticmethod
    def _normalize_teacher_lookup_name(value) -> str:
        text = str(value or "").strip().lower()
        text = text.replace("\n", " ")
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"\b(dr|mr|mrs|ms|miss|prof)\.?\s+", "", text)
        text = re.sub(
            r"\s*[-,]\s*(hod|professor|associate professor|assistant professor|lecturer|coordinator|advisor).*$",
            "",
            text,
        )
        return text.strip()

    @staticmethod
    def _make_placeholder_email(name: str) -> str:
        base = re.sub(r"[^a-z0-9]+", ".", (name or "").strip().lower()).strip(".")
        if not base:
            base = "auto.teacher"
        return f"{base}@placeholder.local"

    @staticmethod
    def _resolve_teacher_id(db: Session, teacher_name, teacher_id, subject, teacher_map, exact_teacher_map):
        if teacher_id:
            return teacher_id

        raw_name = str(teacher_name or "").strip()
        if raw_name:
            exact_match = exact_teacher_map.get(TimetableService._normalize_text(raw_name))
            if exact_match:
                return exact_match

            normalized_match = teacher_map.get(TimetableService._normalize_teacher_lookup_name(raw_name))
            if normalized_match:
                return normalized_match

        subject_teacher_id = getattr(subject, "teacher_id", None)
        if subject_teacher_id:
            return subject_teacher_id

        if raw_name:
            existing = db.query(models.Teacher).filter(
                models.Teacher.email == TimetableService._make_placeholder_email(raw_name)
            ).first()
            if existing:
                exact_teacher_map[TimetableService._normalize_text(existing.name)] = existing.id
                teacher_map[TimetableService._normalize_teacher_lookup_name(existing.name)] = existing.id
                return existing.id

            placeholder = models.Teacher(
                name=raw_name,
                email=TimetableService._make_placeholder_email(raw_name),
                max_hours_per_week=20,
                available_slots=[],
            )
            db.add(placeholder)
            db.flush()
            exact_teacher_map[TimetableService._normalize_text(raw_name)] = placeholder.id
            teacher_map[TimetableService._normalize_teacher_lookup_name(raw_name)] = placeholder.id
            print(f"GENERATOR: Created placeholder teacher '{raw_name}' for workload import.")
            return placeholder.id

        return None

    @staticmethod
    def _division_suffix(group_name: str) -> str:
        name = (group_name or "").strip().upper()
        if "-" in name:
            return name.split("-")[-1]
        return name[-1:] if name else ""

    @staticmethod
    def _parse_first_int(raw_value) -> int:
        match = re.search(r"\d+", str(raw_value or ""))
        return int(match.group()) if match else 0

    @staticmethod
    def _parse_batch_count_for_division(practical_hours, division_suffix: str) -> int:
        text = str(practical_hours or "")
        if not text:
            return 0

        suffix = (division_suffix or "").strip().upper()
        paren_match = re.search(r"\(([^)]*)\)", text)
        mult_matches = re.findall(r"(\d+)\s*\*\s*(\d+)", text)
        default_batches = max((int(right) for _, right in mult_matches), default=0)

        if suffix and paren_match:
            found_division_markup = False
            for part in paren_match.group(1).split(","):
                bit = part.strip().upper()
                if not bit:
                    continue

                match = re.match(r"([A-Z]+)\s*-\s*(\d+)$", bit)
                if match:
                    found_division_markup = True
                    if match.group(1) == suffix:
                        return int(match.group(2))
                    continue

                match = re.match(r"(\d+)\s*-\s*([A-Z]+)$", bit)
                if match:
                    found_division_markup = True
                    if match.group(2) == suffix:
                        return int(match.group(1))
                    continue

                match = re.match(r"([A-Z]+)$", bit)
                if match:
                    found_division_markup = True
                    if match.group(1) == suffix:
                        return default_batches or 1
                    continue

            if found_division_markup:
                return 0

        if mult_matches:
            return default_batches

        return TimetableService._parse_first_int(text)

    @staticmethod
    def _build_batch_labels(group_name: str, count: int):
        suffix = TimetableService._division_suffix(group_name)
        if count <= 0 or not suffix:
            return []
        return [f"{suffix}{idx}" for idx in range(1, count + 1)]

    @staticmethod
    def _balance_year_session_counts(required_assignments, groups, assignment_id_start: int):
        group_name_map = {g.id: g.name for g in groups}
        counts_by_group = defaultdict(int)
        theory_templates = defaultdict(list)

        for assignment in required_assignments:
            group_id = assignment["group_id"]
            group_name = (group_name_map.get(group_id, "") or "").upper()
            if not group_name.startswith(("BE-", "SE-", "TE-")):
                continue
            counts_by_group[group_id] += 1
            if not assignment.get("batch_label") and int(assignment.get("duration", 1) or 1) == 1:
                theory_templates[group_id].append(assignment)

        groups_by_year = defaultdict(list)
        for group_id, group_name in group_name_map.items():
            upper = (group_name or "").upper()
            if upper.startswith(("BE-", "SE-", "TE-")):
                groups_by_year[upper.split("-")[0]].append(group_id)

        next_assignment_id = assignment_id_start
        for _, group_ids in groups_by_year.items():
            existing = [counts_by_group[g] for g in group_ids if g in counts_by_group]
            if not existing:
                continue
            target = max(existing)
            for group_id in group_ids:
                deficit = target - counts_by_group.get(group_id, 0)
                if deficit <= 0:
                    continue
                templates = theory_templates.get(group_id, [])
                if not templates:
                    continue

                subject_usage = Counter(a["subject_id"] for a in templates)
                templates = sorted(
                    templates,
                    key=lambda a: (subject_usage[a["subject_id"]], a["subject_id"], a.get("occurrence", 0))
                )

                for idx in range(deficit):
                    base = templates[idx % len(templates)]
                    cloned = {
                        **base,
                        "assignment_id": next_assignment_id,
                        "occurrence": (base.get("occurrence", 0) or 0) + 100 + idx,
                    }
                    required_assignments.append(cloned)
                    counts_by_group[group_id] += 1
                    next_assignment_id += 1

        return required_assignments, next_assignment_id

    @staticmethod
    def _build_greedy_schedule(subjects, rooms, groups, slots, required_assignments):
        active_slots = [s for s in slots if not s.is_break]
        if not active_slots or not required_assignments:
            return []

        subject_map = {s.id: s for s in subjects}
        group_map = {g.id: g for g in groups}
        lab_rooms = [r for r in rooms if TimetableService._room_is_lab(r)]
        lecture_rooms = [r for r in rooms if not TimetableService._room_is_lab(r)] or rooms
        teacher_assignment_count = defaultdict(int)
        for assignment in required_assignments:
            if assignment.get("teacher_id"):
                teacher_assignment_count[assignment["teacher_id"]] += 1

        def group_priority(group_id):
            group_name = (getattr(group_map.get(group_id), "name", "") or "").upper()
            if group_name.startswith("TE-"):
                return 0
            if group_name.startswith("BE-"):
                return 1
            if group_name.startswith("SE-"):
                return 2
            if group_name.startswith("FE-"):
                return 3
            return 4

        slots_by_day = defaultdict(list)
        for slot in active_slots:
            slots_by_day[slot.day].append(slot)
        for day in slots_by_day:
            slots_by_day[day].sort(key=lambda s: s.period)

        next_slot = {}
        for day, day_slots in slots_by_day.items():
            for i in range(len(day_slots) - 1):
                if day_slots[i + 1].period == day_slots[i].period + 1:
                    next_slot[day_slots[i].id] = day_slots[i + 1].id

        division_busy = set()
        batch_busy = set()
        room_busy = set()
        teacher_busy = set()
        group_day_subjects = defaultdict(set)
        group_day_load = defaultdict(int)
        schedule = []
        group_batch_labels = defaultdict(set)

        for assignment in required_assignments:
            batch_label = assignment.get("batch_label")
            if batch_label:
                group_batch_labels[assignment["group_id"]].add(batch_label)

        def occupied_by_other_batch(group_id, occupied_slots, batch_label):
            batches = group_batch_labels.get(group_id, set())
            if not batches:
                return False
            return any(
                any(
                    (group_id, other_batch, sid) in batch_busy
                    for other_batch in batches
                    if not batch_label or other_batch != batch_label
                )
                for sid in occupied_slots
            )

        def parallel_batch_usage(group_id, occupied_slots, batch_label):
            batches = group_batch_labels.get(group_id, set())
            if not batches or not batch_label:
                return 0
            used = 0
            for sid in occupied_slots:
                if any((group_id, other_batch, sid) in batch_busy for other_batch in batches if other_batch != batch_label):
                    used += 1
            return used

        def group_conflict(group_id, occupied_slots, batch_label):
            if batch_label:
                if any((group_id, sid) in division_busy for sid in occupied_slots):
                    return True
                if any((group_id, batch_label, sid) in batch_busy for sid in occupied_slots):
                    return True
                return False

            if any((group_id, sid) in division_busy for sid in occupied_slots):
                return True
            return occupied_by_other_batch(group_id, occupied_slots, batch_label)

        def valid_rooms_for(assignment):
            is_lab = assignment.get("duration", 1) >= 2
            return lab_rooms if is_lab and lab_rooms else lecture_rooms

        def room_preference_score(assignment, room):
            group = group_map.get(assignment.get("group_id"))
            room_name = (getattr(room, "name", "") or "").upper()
            preferred = TimetableService._preferred_room_sets_for_group(getattr(group, "name", ""))
            if assignment.get("duration", 1) >= 2:
                return 0 if room_name in preferred["lab"] else 5
            return 0 if room_name in preferred["lecture"] else 5

        def sort_key(assignment):
            subject = subject_map.get(assignment["subject_id"])
            is_lab = assignment.get("duration", 1) >= 2 or (subject and subject.is_lab)
            return (
                0 if is_lab else 1,
                -assignment.get("duration", 1),
                group_priority(assignment.get("group_id")),
                -teacher_assignment_count.get(assignment.get("teacher_id"), 0),
                0 if assignment.get("batch_label") else 1,
                -assignment.get("group_id", 0),
                assignment.get("subject_id", 0),
            )

        unscheduled = 0
        for assignment in sorted(required_assignments, key=sort_key):
            group_id = assignment["group_id"]
            teacher_id = assignment.get("teacher_id")
            subject_id = assignment["subject_id"]
            duration = max(1, int(assignment.get("duration", 1) or 1))
            batch_label = assignment.get("batch_label")
            candidate_rooms = valid_rooms_for(assignment)

            best_choice = None
            best_score = None

            for day, day_slots in slots_by_day.items():
                for slot in day_slots:
                    occupied_slots = [slot.id]
                    if duration >= 2:
                        nxt = next_slot.get(slot.id)
                        if not nxt:
                            continue
                        occupied_slots.append(nxt)

                    if group_conflict(group_id, occupied_slots, batch_label):
                        continue
                    if teacher_id and any((teacher_id, sid) in teacher_busy for sid in occupied_slots):
                        continue

                    for room in candidate_rooms:
                        if any((room.id, sid) in room_busy for sid in occupied_slots):
                            continue

                        score = (
                            0 if batch_label and parallel_batch_usage(group_id, occupied_slots, batch_label) == len(occupied_slots) else 1,
                            -parallel_batch_usage(group_id, occupied_slots, batch_label),
                            1 if (not batch_label and subject_id in group_day_subjects[(group_id, day)]) else 0,
                            group_day_load[(group_id, day)],
                            slot.period,
                            room_preference_score(assignment, room),
                            0 if room.type == "LectureHall" else 1,
                            room.id,
                        )
                        if best_score is None or score < best_score:
                            best_score = score
                            best_choice = (room, occupied_slots, day)

            if not best_choice:
                unscheduled += 1
                continue

            room, occupied_slots, day = best_choice
            for sid in occupied_slots:
                schedule.append({
                    "class_group_id": group_id,
                    "subject_id": subject_id,
                    "room_id": room.id,
                    "time_slot_id": sid,
                    "teacher_id": teacher_id,
                    "batch_label": batch_label,
                })
                if batch_label:
                    batch_busy.add((group_id, batch_label, sid))
                else:
                    division_busy.add((group_id, sid))
                room_busy.add((room.id, sid))
                if teacher_id:
                    teacher_busy.add((teacher_id, sid))

            if not batch_label:
                group_day_subjects[(group_id, day)].add(subject_id)
            group_day_load[(group_id, day)] += len(occupied_slots)

        print(f"GENERATOR: Greedy fallback scheduled {len(schedule)} timetable entries; unscheduled assignments={unscheduled}")
        return schedule

    @staticmethod
    def generate_and_save(db: Session, method: str = "csp", version_name: str = "New Timetable"):
        TimetableService.normalize_subject_rules(db)
        # 1. Fetch data
        db_teachers = db.query(models.Teacher).all()
        db_subjects = db.query(models.Subject).all()
        db_rooms = db.query(models.Room).all()
        db_groups = db.query(models.ClassGroup).all()
        db_slots = db.query(models.TimeSlot).all()
        db_lessons = db.query(models.Lesson).all()

        print(f"GENERATOR: Found {len(db_lessons)} lessons, {len(db_slots)} slots, method: {method}")
        
        # Convert DB models to Domain Entities expected by Solvers
        teachers = [Teacher(id=t.id, name=t.name, email=t.email) for t in db_teachers]
        subjects = [Subject(id=s.id, name=s.name, code=s.code, is_lab=s.is_lab, credits=s.credits, 
                    required_room_type=s.required_room_type, duration_slots=s.duration_slots, teacher_id=s.teacher_id) for s in db_subjects]
        rooms = [Room(id=r.id, name=r.name, capacity=r.capacity, type=r.type) for r in db_rooms]
        groups = [ClassGroup(id=g.id, name=g.name, student_count=g.student_count) for g in db_groups]
        slots = [TimeSlot(id=s.id, day=s.day, period=s.period, start_time=s.start_time, end_time=s.end_time, is_break=s.is_break) for s in db_slots]

        # ─── WORKLOAD SOURCE ───
        required_assignments = []
        assignment_id = 0
        
        # Priority 1: Use DOCX Override (v3/v4 way)
        override = db.query(models.WorkloadReportOverride).filter(
            models.WorkloadReportOverride.version_id == None
        ).first()

        if override and override.report_data:
            print(f"GENERATOR: Using WorkloadReportOverride (DOCX) data for generation.")
            # Maps for efficient DB lookup
            # Normalization helper
            def norm(s): return re.sub(r'\s+', ' ', str(s).lower()).strip() if s else ""

            subject_obj_map = {norm(s.name): s for s in db_subjects}
            subject_map = {key: subj.id for key, subj in subject_obj_map.items()}
            group_map = {norm(g.name).replace("-", ""): g.id for g in db_groups}
            teacher_map = {TimetableService._normalize_teacher_lookup_name(t.name): t.id for t in db_teachers}
            exact_teacher_map = {norm(t.name): t.id for t in db_teachers}
            
            def normalize_and_expand_classes(name):
                if not name: return []
                name = name.strip()
                if ',' not in name:
                    return [name.replace(" ", "").upper()]
                
                parts = [p.strip() for p in name.split(',')]
                prefix = ""
                # Try to find a dash prefix in the first part, e.g., "SE-A" -> "SE-"
                if '-' in parts[0]:
                    prefix = parts[0].split('-')[0] + "-"
                
                results = []
                for p in parts:
                    if '-' in p:
                        results.append(p.replace(" ", "").upper())
                        # Update current prefix if this part has one
                        prefix = p.split('-')[0] + "-"
                    elif prefix:
                        results.append(f"{prefix}{p}".replace(" ", "").upper())
                    else:
                        results.append(p.replace(" ", "").upper())
                return results

            for t_load in override.report_data:
                t_name = t_load.get("name", "Unknown")
                teacher_id = t_load.get("id")

                for course in t_load.get("courses_detail", []):
                    subj_name = course.get("course_name", "").strip()
                    subj_id = subject_map.get(norm(subj_name))
                    subject_obj = subject_obj_map.get(norm(subj_name))
                    
                    if not subj_id:
                        print(f"GENERATOR: Skipping subject '{subj_name}' for {t_name} (Not found in DB)")
                        continue

                    resolved_teacher_id = TimetableService._resolve_teacher_id(
                        db=db,
                        teacher_name=t_name,
                        teacher_id=teacher_id,
                        subject=subject_obj,
                        teacher_map=teacher_map,
                        exact_teacher_map=exact_teacher_map,
                    )
                    if not resolved_teacher_id:
                        print(f"GENERATOR: Skipping subject '{subj_name}' for '{t_name}' (Teacher unresolved)")
                        continue
                    
                    # Expansion for divisions
                    cls_raw = course.get("class_division")
                    cls_list = normalize_and_expand_classes(cls_raw)
                    
                    # Theory stays 1-hour. Practicals are expanded batchwise as 2-hour sessions.
                    t_h = 0
                    try:
                        th_val = course.get("theory_hours", "0")
                        if th_val:
                            match = re.search(r'\d+', str(th_val))
                            if match: t_h = int(match.group())
                    except: pass

                    practical_raw = str(course.get("practical_hours", "") or "")
                    project_raw = str(course.get("project_hours", "") or "")

                    total_load = t_h
                    if total_load <= 0:
                        total_load = course.get("total_load", 0)
                        if isinstance(total_load, str):
                            try:
                                total_load = int(re.search(r'\d+', total_load).group())
                            except:
                                total_load = 0

                    if total_load <= 0:
                        total_load = TimetableService._parse_first_int(practical_raw)

                    theory_sessions = t_h
                    if theory_sessions <= 0 and not practical_raw and not project_raw:
                        theory_sessions = total_load

                    for clean_cls in cls_list:
                        group_id = group_map.get(norm(clean_cls).replace("-", ""))
                        if not group_id:
                            print(f"GENERATOR: Skipping class '{clean_cls}' for {subj_name} (Not found in DB)")
                            continue

                        division_suffix = TimetableService._division_suffix(clean_cls)
                        practical_batch_count = TimetableService._parse_batch_count_for_division(practical_raw, division_suffix)
                        batch_labels = TimetableService._build_batch_labels(clean_cls, practical_batch_count)

                        for occ in range(theory_sessions):
                            required_assignments.append({
                                'assignment_id': assignment_id,
                                'group_id': group_id,
                                'subject_id': subj_id,
                                'teacher_id': resolved_teacher_id,
                                'duration': 1,
                                'occurrence': occ + 1,
                                'batch_label': None,
                            })
                            assignment_id += 1

                        for occ, batch_label in enumerate(batch_labels, start=1):
                            required_assignments.append({
                                'assignment_id': assignment_id,
                                'group_id': group_id,
                                'subject_id': subj_id,
                                'teacher_id': resolved_teacher_id,
                                'duration': 2,
                                'occurrence': occ,
                                'batch_label': batch_label,
                            })
                            assignment_id += 1
            print(f"GENERATOR: Final Assignment Count from DOCX = {len(required_assignments)}")

        else:
            # Priority 2: Fallback to Legacy Lessons table
            print(f"GENERATOR: WorkloadReportOverride not found. Falling back to Lessons table.")
            for lesson in db_lessons:
                teacher_id = lesson.teachers[0].id if lesson.teachers else None
                subject_id = lesson.subjects[0].id if lesson.subjects else None
                group_id = lesson.class_groups[0].id if lesson.class_groups else None
                
                if teacher_id and subject_id and group_id:
                    subject = lesson.subjects[0]
                    duration = lesson.length_per_lesson
                    if subject.is_lab or (subject.required_room_type and "Lab" in subject.required_room_type):
                        if duration < 2: duration = 2

                    for occurrence in range(lesson.lessons_per_week):
                        required_assignments.append({
                            'assignment_id': assignment_id,
                            'group_id': group_id,
                            'subject_id': subject_id,
                            'teacher_id': teacher_id,
                            'duration': duration,
                            'occurrence': occurrence + 1,
                            'batch_label': None,
                        })
                        assignment_id += 1

        required_assignments, assignment_id = TimetableService._balance_year_session_counts(
            required_assignments, groups, assignment_id
        )

        print(f"GENERATOR: Constructed {len(required_assignments)} assignments totalling approximately {sum(a['duration'] for a in required_assignments)} periods.")

        # Create version record
        version = models.TimetableVersion(name=version_name, algorithm=method)
        db.add(version)
        db.commit()
        db.refresh(version)

        # Run Solver
        try:
            if method == "genetic":
                solver = GeneticTimetableSolver(teachers, subjects, rooms, groups, slots, required_assignments)
                schedule = solver.solve()
            else:
                if len(required_assignments) > 140:
                    print(f"GENERATOR: Skipping CSP for large workload ({len(required_assignments)} assignments); using greedy fallback.")
                    schedule = None
                else:
                    solver = CspTimetableSolver(teachers, subjects, rooms, groups, slots, required_assignments)
                    schedule = solver.solve()
        except Exception as e:
            print(f"GENERATOR: Primary solver '{method}' failed with error: {e}")
            schedule = None

        if not schedule:
            print("GENERATOR: Falling back to greedy scheduler.")
            schedule = TimetableService._build_greedy_schedule(subjects, rooms, groups, slots, required_assignments)

        # Save results
        if schedule:
            entries_created = 0
            for item in schedule:
                entry = models.TimetableEntry(
                    version_id=version.id,
                    time_slot_id=item["time_slot_id"],
                    subject_id=item["subject_id"],
                    room_id=item["room_id"],
                    class_group_id=item["class_group_id"],
                    teacher_id=item["teacher_id"],
                    batch_label=item.get("batch_label"),
                )
                db.add(entry)
                entries_created += 1
            
            version.status = "active"
            version.is_valid = True
            db.commit()
            db.refresh(version)
            print(f"GENERATOR: Success! Saved {entries_created} entries to DB.")
        else:
            version.status = "failed"
            version.is_valid = False
            db.commit()
            db.refresh(version)
            print("GENERATOR: Solver failed to find a valid schedule.")
            
        return version

    @staticmethod
    def get_latest(db: Session):
        latest_with_entries = (
            db.query(models.TimetableVersion)
            .join(models.TimetableEntry, models.TimetableEntry.version_id == models.TimetableVersion.id)
            .group_by(models.TimetableVersion.id)
            .order_by(models.TimetableVersion.id.desc())
            .first()
        )
        if latest_with_entries:
            return latest_with_entries
        return db.query(models.TimetableVersion).order_by(models.TimetableVersion.id.desc()).first()

    @staticmethod
    def get_analytics(db: Session, version_id: int):
        version = db.query(models.TimetableVersion).filter(models.TimetableVersion.id == version_id).first()
        if not version: return None
        
        entries = version.entries
        total_slots = db.query(models.TimeSlot).filter(models.TimeSlot.is_break == False).count()
        
        # 1. Teacher Utilization
        teacher_stats = []
        teachers = db.query(models.Teacher).all()
        for t in teachers:
            assigned = sum(1 for e in entries if e.teacher_id == t.id)
            teacher_stats.append({
                "id": t.id,
                "name": t.name,
                "assigned_slots": assigned,
                "total_slots": t.max_hours_per_week, # Or use a different metric
                "utilization_percentage": (assigned / t.max_hours_per_week * 100) if t.max_hours_per_week else 0
            })
            
        # 2. Room Utilization
        room_stats = []
        rooms = db.query(models.Room).all()
        for r in rooms:
            assigned = sum(1 for e in entries if e.room_id == r.id)
            room_stats.append({
                "id": r.id,
                "name": r.name,
                "assigned_slots": assigned,
                "total_slots": total_slots,
                "utilization_percentage": (assigned / total_slots * 100) if total_slots else 0
            })
            
        # 3. Conflict Detection (Redundant for auto-generated, but good for manual edits)
        conflicts = HardConstraints.check_teacher_overlap([e.__dict__ for e in entries])
        conflicts += HardConstraints.check_room_overlap([e.__dict__ for e in entries])

        return {
            "teacher_utilization": teacher_stats,
            "room_utilization": room_stats,
            "conflicts": conflicts,
            "subject_load": {s.id: 1.0 for s in db.query(models.Subject).all()} # Placeholder
        }

    @staticmethod
    def generate_in_background(version_id: int, method: str):
        db = SessionLocal()
        try:
            version = db.query(models.TimetableVersion).filter(models.TimetableVersion.id == version_id).first()
            if not version: return
            
            # Fetch data (reusing logic from generate_and_save)
            db_teachers = db.query(models.Teacher).all()
            db_subjects = db.query(models.Subject).all()
            db_rooms = db.query(models.Room).all()
            db_groups = db.query(models.ClassGroup).all()
            db_slots = db.query(models.TimeSlot).all()
            db_lessons = db.query(models.Lesson).all()  # ADDED: Query lessons

            teachers = [Teacher(id=t.id, name=t.name, email=t.email) for t in db_teachers]
            subjects = [Subject(id=s.id, name=s.name, code=s.code, is_lab=s.is_lab, credits=s.credits, 
                        required_room_type=s.required_room_type, duration_slots=s.duration_slots, teacher_id=s.teacher_id) for s in db_subjects]
            rooms = [Room(id=r.id, name=r.name, capacity=r.capacity, type=r.type) for r in db_rooms]
            groups = [ClassGroup(id=g.id, name=g.name, student_count=g.student_count) for g in db_groups]
            slots = [TimeSlot(id=s.id, day=s.day, period=s.period, start_time=s.start_time, end_time=s.end_time, is_break=s.is_break) for s in db_slots]

            # ADDED: Convert lessons to required assignments (same logic as generate_and_save)
            required_assignments = []
            assignment_id = 0
            
            print(f"DEBUG (background): Found {len(db_lessons)} lessons in database")
            
            # Teacher-Subject Exclusion Rules
            FORBIDDEN_RULES = {
                "Kottawar": ["Professional and Technical Communication", "Professional & Technical Communication", "PTC"],
                "Sharma": ["Sustainable Development", "Sustainable Energy", "Energy"],
                "Gothane": ["Engineering Physics", "Engg Physics"]
            }

            for lesson in db_lessons:
                teacher_id = lesson.teachers[0].id if lesson.teachers else None
                subject_id = lesson.subjects[0].id if lesson.subjects else None
                group_id = lesson.class_groups[0].id if lesson.class_groups else None
                
                if teacher_id and subject_id and group_id:
                    teacher = lesson.teachers[0]
                    subject = lesson.subjects[0]

                    # Check for forbidden assignments
                    is_forbidden = False
                    for t_key, subjects_list in FORBIDDEN_RULES.items():
                        if t_key.lower() in teacher.name.lower():
                            if any(fs.lower() in subject.name.lower() or fs.lower() in (subject.code or "").lower() for fs in subjects_list):
                                print(f"DEBUG (background): Skipping forbidden assignment: {teacher.name} -> {subject.name}")
                                is_forbidden = True
                                break
                    if is_forbidden:
                        continue

                    # Force Lab duration
                    duration = lesson.length_per_lesson
                    if subject.is_lab or (subject.required_room_type and "Lab" in subject.required_room_type):
                        if duration < 2:
                            print(f"DEBUG (background): Forcing duration=2 for lab: {subject.name}")
                            duration = 2

                    for occurrence in range(lesson.lessons_per_week):
                        required_assignments.append({
                            'assignment_id': assignment_id,
                            'group_id': group_id,
                            'subject_id': subject_id,
                            'teacher_id': teacher_id,
                            'duration': duration,
                            'occurrence': occurrence + 1
                        })
                        assignment_id += 1

            print(f"DEBUG (background): Generated {len(required_assignments)} required assignments from {len(db_lessons)} lessons")

            # Pass required_assignments to solver
            if method == "genetic":
                solver = GeneticTimetableSolver(teachers, subjects, rooms, groups, slots, required_assignments)
                schedule = solver.solve()
            else:
                solver = CspTimetableSolver(teachers, subjects, rooms, groups, slots, required_assignments)
                schedule = solver.solve()

            if schedule:
                for item in schedule:
                    entry = models.TimetableEntry(
                        version_id=version.id,
                        time_slot_id=item["time_slot_id"],
                        subject_id=item["subject_id"],
                        room_id=item["room_id"],
                        class_group_id=item["class_group_id"],
                        teacher_id=item["teacher_id"]
                    )
                    db.add(entry)
                version.status = "active"
                version.is_valid = True
            else:
                version.status = "failed"
                version.is_valid = False
            
            db.commit()
        except Exception as e:
            print(f"Bkg Error: {e}")
            import traceback
            traceback.print_exc()
            if version:
                version.status = "error"
                db.commit()
        finally:
            db.close()
