from ortools.sat.python import cp_model
from typing import List, Dict, Any, Set
from ..domain.entities.all_entities import Teacher, Subject, Room, ClassGroup, TimeSlot
from collections import defaultdict


class CspTimetableSolver:
    def __init__(self, teachers: List[Teacher], subjects: List[Subject],
                 rooms: List[Room], groups: List[ClassGroup], slots: List[TimeSlot],
                 required_assignments: List[Dict[str, Any]] = None):
        self.teachers = teachers
        self.subjects = subjects
        self.rooms = rooms
        self.groups = groups
        self.slots = slots
        self.required_assignments = required_assignments or []
        self.model = cp_model.CpModel()

        # Lookups
        self.slot_map = {s.id: s for s in slots}
        self.subject_map = {s.id: s for s in subjects}
        self.active_slots = [s for s in slots if not s.is_break]

        # Consecutive slot map: slot_id -> next_slot_id (same day, period n -> n+1)
        day_slots_by_day = defaultdict(list)
        for s in self.active_slots:
            day_slots_by_day[s.day].append(s)

        self.next_slot: Dict[int, int] = {}
        self.day_of_slot: Dict[int, str] = {}
        self.all_days: Set[str] = set()
        self.slots_by_day: Dict[str, List[int]] = defaultdict(list)

        for day, day_list in day_slots_by_day.items():
            self.all_days.add(day)
            sorted_list = sorted(day_list, key=lambda s: s.period)
            for s in sorted_list:
                self.day_of_slot[s.id] = day
                self.slots_by_day[day].append(s.id)
            for i in range(len(sorted_list) - 1):
                curr, nxt = sorted_list[i], sorted_list[i + 1]
                if nxt.period == curr.period + 1:
                    self.next_slot[curr.id] = nxt.id

        # Identify lab assignments (need 2 consecutive periods)
        self._lab_ids: Set[int] = set()
        for idx, a in enumerate(self.required_assignments):
            subj = self.subject_map.get(a['subject_id'])
            duration = a.get('duration', 1)
            subj_lab = subj and subj.is_lab and (subj.duration_slots or 1) >= 2
            if subj_lab or duration >= 2:
                self._lab_ids.add(idx)

        # Room type matching
        self.lab_rooms = [r for r in rooms if 'lab' in (r.type or '').lower()]
        self.lecture_rooms = [r for r in rooms if 'lab' not in (r.type or '').lower()]

    # ------------------------------------------------------------------
    def _valid_rooms(self, idx: int) -> List:
        a = self.required_assignments[idx]
        is_lab_assignment = a.get('duration', 1) >= 2
        
        if is_lab_assignment:
            return self.lab_rooms or self.rooms
        else:
            return self.lecture_rooms or self.rooms

    # ------------------------------------------------------------------
    def solve(self):
        if not self.required_assignments:
            return self._solve_cartesian()

        print(f"CSP: {len(self.required_assignments)} assignments | "
              f"{len(self.active_slots)} slots | {len(self.rooms)} rooms | "
              f"{len(self._lab_ids)} labs (2-period)")

        # ── Build variables ──────────────────────────────────────────────────
        # var[(idx, room_id, slot_id)] = BoolVar
        var: Dict = {}
        for idx in range(len(self.required_assignments)):
            is_lab = idx in self._lab_ids
            for r in self._valid_rooms(idx):
                for t in self.active_slots:
                    # Labs can only START where a consecutive next slot exists
                    if is_lab and t.id not in self.next_slot:
                        continue
                    var[(idx, r.id, t.id)] = self.model.NewBoolVar(
                        f'a{idx}_r{r.id}_t{t.id}')

        print(f"CSP: {len(var)} variables created")

        # ── Pre-build indexes for fast constraint generation ─────────────────
        # idx -> list of its vars
        idx_vars: Dict[int, list] = defaultdict(list)
        # (group_id, slot_id) -> list of vars whose assignment OCCUPIES that slot
        group_slot_vars: Dict[tuple, list] = defaultdict(list)
        # (room_id, slot_id) -> list of vars whose assignment OCCUPIES that slot
        room_slot_vars: Dict[tuple, list] = defaultdict(list)
        # (teacher_id, slot_id) -> list of vars whose assignment OCCUPIES that slot
        teacher_slot_vars: Dict[tuple, list] = defaultdict(list)
        # (group_id, subject_id, day) -> list of vars that START on that day
        group_subj_day_vars: Dict[tuple, list] = defaultdict(list)
        # (group_id, day) -> list of (var, weight) for daily load
        group_day_load: Dict[tuple, list] = defaultdict(list)
        # (group_id, subject_id, slot_id) -> list of vars that START this subject/group here
        group_subj_slot_vars: Dict[tuple, list] = defaultdict(list)

        for (idx, rid, sid), v in var.items():
            a = self.required_assignments[idx]
            group_id = a['group_id']
            teacher_id = a.get('teacher_id')
            subject_id = a['subject_id']
            day = self.day_of_slot[sid]
            is_lab = idx in self._lab_ids
            weight = 2 if is_lab else 1

            idx_vars[idx].append(v)
            group_subj_day_vars[(group_id, subject_id, day)].append(v)
            group_day_load[(group_id, day)].append((v, weight))

            # Occupied slots = start slot + next slot (for labs)
            occupied = [sid]
            if is_lab:
                nxt = self.next_slot.get(sid)
                if nxt:
                    occupied.append(nxt)

            for occ_slot in occupied:
                group_slot_vars[(group_id, occ_slot)].append(v)
                room_slot_vars[(rid, occ_slot)].append(v)
                if teacher_id:
                    teacher_slot_vars[(teacher_id, occ_slot)].append(v)
            
            # C7 Pre-indexing: group_subj_slot_vars
            # Track which variables START a specific subject for a group in a slot
            group_subj_slot_vars[(group_id, subject_id, sid)].append(v)

        # ── C1: Each assignment scheduled AT MOST ONCE (Relaxed for feasibility) ──
        for idx, v_list in idx_vars.items():
            if v_list:
                # Use <= 1 so solver can skip assignments it can't fit without conflicts
                self.model.Add(sum(v_list) <= 1)
        print(f"CSP: C1 – {len(idx_vars)} at-most-once constraints")

        # ── C2: Group no-overlap (including lab 2nd period) ───────────────────
        c2 = 0
        for v_list in group_slot_vars.values():
            if len(v_list) > 1:
                self.model.Add(sum(v_list) <= 1)
                c2 += 1
        print(f"CSP: C2 – {c2} group-timeslot constraints")

        # ── C3: Room no-overlap ───────────────────────────────────────────────
        c3 = 0
        for v_list in room_slot_vars.values():
            if len(v_list) > 1:
                self.model.Add(sum(v_list) <= 1)
                c3 += 1
        print(f"CSP: C3 – {c3} room-timeslot constraints")

        # ── C4: Teacher no-overlap ────────────────────────────────────────────
        c4 = 0
        for v_list in teacher_slot_vars.values():
            if len(v_list) > 1:
                self.model.Add(sum(v_list) <= 1)
                c4 += 1
        print(f"CSP: C4 – {c4} teacher-timeslot constraints")

        # ── C5: Same subject ≤ 1 per day per group (Theory/General) ───────────
        c5 = 0
        for (gid, subid, day), v_list in group_subj_day_vars.items():
            if len(v_list) > 1:
                self.model.Add(sum(v_list) <= 1)
                c5 += 1
        print(f"CSP: C5 – {c5} same-subject-per-day constraints")

        # ── C7: No consecutive same-subject lectures (same group) ───────────
        c7 = 0
        for (gid, subid, day) in group_subj_day_vars.keys():
            day_slots = self.slots_by_day.get(day, [])
            for i in range(len(day_slots) - 1):
                s1 = day_slots[i]
                s2 = day_slots[i+1]
                
                vars_s1 = group_subj_slot_vars.get((gid, subid, s1), [])
                vars_s2 = group_subj_slot_vars.get((gid, subid, s2), [])
                
                if vars_s1 and vars_s2:
                    # If we have assignments starting at s1 AND s2, they can't both be true
                    self.model.Add(sum(vars_s1) + sum(vars_s2) <= 1)
                    c7 += 1
        print(f"CSP: C7 – {c7} consecutive-subject constraints")

        # ── C6: Max 5 periods per group per day (labs = 2 periods) ───────────
        MAX_PERIODS = 5
        c6 = 0
        for (group_id, day), load_list in group_day_load.items():
            if load_list:
                terms = [v * w for v, w in load_list]
                self.model.Add(sum(terms) <= MAX_PERIODS)
                c6 += 1
        print(f"CSP: C6 – {c6} daily-load constraints (max {MAX_PERIODS})")

        # ── Objective: Maximize scheduled assignments ─────────────────────────
        self.model.Maximize(sum(var.values()))

        # ── Solve ─────────────────────────────────────────────────────────────
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 60.0
        solver.parameters.num_search_workers = 8  # Use more workers
        solver.parameters.log_search_progress = True
        print(f"CSP: Solving {len(var)} variables (timeout 60 s)…")
        status = solver.Solve(self.model)

        names = {cp_model.OPTIMAL: "OPTIMAL", cp_model.FEASIBLE: "FEASIBLE",
                 cp_model.INFEASIBLE: "INFEASIBLE", cp_model.UNKNOWN: "UNKNOWN"}
        print(f"CSP: Status = {names.get(status, status)}")

        if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            schedule = self._extract(solver, var)
            print(f"CSP: {len(schedule)} entries extracted")
            return schedule

        return None

    # ------------------------------------------------------------------
    def _extract(self, solver, var: Dict) -> List[Dict]:
        schedule = []
        seen: Set[tuple] = set()

        for (idx, rid, start_sid), v in var.items():
            if solver.Value(v) != 1:
                continue
            a = self.required_assignments[idx]

            def add(slot_id):
                key = (a['group_id'], a['subject_id'], slot_id)
                if key in seen:
                    return
                seen.add(key)
                slot = self.slot_map.get(slot_id)
                if slot:
                    schedule.append({
                        "class_group_id": a['group_id'],
                        "subject_id": a['subject_id'],
                        "room_id": rid,
                        "time_slot_id": slot_id,
                        "teacher_id": a.get('teacher_id'),
                        "batch_label": a.get('batch_label'),
                        "day": slot.day,
                        "period": slot.period,
                    })

            add(start_sid)
            if idx in self._lab_ids:
                nxt = self.next_slot.get(start_sid)
                if nxt:
                    add(nxt)

        return schedule

    # ------------------------------------------------------------------
    # Fallback (rarely used)
    # ------------------------------------------------------------------
    def _solve_cartesian(self):
        print("WARNING: No assignments – cartesian fallback")
        return None
