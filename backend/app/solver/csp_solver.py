from ortools.sat.python import cp_model
from typing import List, Dict, Any
from ..domain.entities.all_entities import Teacher, Subject, Room, ClassGroup, TimeSlot

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
        self.vars = {} # (assignment_idx, room, slot) -> BoolVar

    def solve(self):
        # If no required assignments provided, fall back to old behavior
        if not self.required_assignments:
            print("WARNING: No required assignments provided, using cartesian product (may fail)")
            return self._solve_cartesian()
        
        # 1. Create Variables - one for each required assignment × room × slot
        print(f"DEBUG: Creating variables for {len(self.required_assignments)} required assignments...")
        
        for idx, assignment in enumerate(self.required_assignments):
            for r in self.rooms:
                for t in self.slots:
                    if t.is_break:
                        continue
                    
                    # Create variable for this assignment at this room and slot
                    self.vars[(idx, r.id, t.id)] = self.model.NewBoolVar(
                        f'x_a{idx}_r{r.id}_t{t.id}'
                    )

        print(f"DEBUG: Created {len(self.vars)} variables")

        # 2. Constraints
        print(f"DEBUG: Applying constraints...")
        
        # C1: Each assignment must be scheduled exactly once
        for idx in range(len(self.required_assignments)):
            assignment_vars = []
            for r in self.rooms:
                for t in self.slots:
                    if not t.is_break and (idx, r.id, t.id) in self.vars:
                        assignment_vars.append(self.vars[(idx, r.id, t.id)])
            if assignment_vars:
                self.model.Add(sum(assignment_vars) == 1)
        print(f"DEBUG: Added {len(self.required_assignments)} assignment constraints")

        # C2: Group No Overlaps - a group can't have multiple classes at same time
        overlap_count = 0
        for t in self.slots:
            if t.is_break:
                continue
            for group_id in set(a['group_id'] for a in self.required_assignments):
                group_vars = []
                for idx, assignment in enumerate(self.required_assignments):
                    if assignment['group_id'] == group_id:
                        for r in self.rooms:
                            if (idx, r.id, t.id) in self.vars:
                                group_vars.append(self.vars[(idx, r.id, t.id)])
                if group_vars:
                    self.model.Add(sum(group_vars) <= 1)
                    overlap_count += 1
        print(f"DEBUG: Added {overlap_count} group overlap constraints")

        # C3: Room No Overlaps - a room can't have multiple classes at same time
        room_overlap_count = 0
        for r in self.rooms:
            for t in self.slots:
                if t.is_break:
                    continue
                room_vars = []
                for idx in range(len(self.required_assignments)):
                    if (idx, r.id, t.id) in self.vars:
                        room_vars.append(self.vars[(idx, r.id, t.id)])
                if room_vars:
                    self.model.Add(sum(room_vars) <= 1)
                    room_overlap_count += 1
        print(f"DEBUG: Added {room_overlap_count} room overlap constraints")

        # C4: Teacher No Overlaps - a teacher can't teach multiple classes at same time
        teacher_overlap_count = 0
        for t in self.slots:
            if t.is_break:
                continue
            for teacher_id in set(a['teacher_id'] for a in self.required_assignments if a['teacher_id']):
                teacher_vars = []
                for idx, assignment in enumerate(self.required_assignments):
                    if assignment.get('teacher_id') == teacher_id:
                        for r in self.rooms:
                            if (idx, r.id, t.id) in self.vars:
                                teacher_vars.append(self.vars[(idx, r.id, t.id)])
                if teacher_vars:
                    self.model.Add(sum(teacher_vars) <= 1)
                    teacher_overlap_count += 1
        print(f"DEBUG: Added {teacher_overlap_count} teacher overlap constraints")

        # C5: HARD CONSTRAINT - Each teacher must teach exactly 3 classes per day
        # TEMPORARILY DISABLED - Testing if this constraint is causing the 63-entry issue
        # daily_load_count = 0
        # days = set(t.day for t in self.slots if not t.is_break)
        # for teacher_id in set(a['teacher_id'] for a in self.required_assignments if a['teacher_id']):
        #     for day in days:
        #         # Get all slots for this day
        #         day_slots = [t for t in self.slots if t.day == day and not t.is_break]
        #         
        #         # Get all variables for this teacher on this day
        #         teacher_day_vars = []
        #         for idx, assignment in enumerate(self.required_assignments):
        #             if assignment.get('teacher_id') == teacher_id:
        #                 for slot in day_slots:
        #                     for r in self.rooms:
        #                         if (idx, r.id, slot.id) in self.vars:
        #                             teacher_day_vars.append(self.vars[(idx, r.id, slot.id)])
        #         
        #         if teacher_day_vars:
        #             # Each teacher must teach exactly 3 classes per day
        #             self.model.Add(sum(teacher_day_vars) == 3)
        #             daily_load_count += 1
        # print(f"DEBUG: Added {daily_load_count} daily teacher load constraints (3 classes/day)")
        print(f"DEBUG: Daily teacher load constraint DISABLED for testing - will re-enable after fixing 225 entries issue")

        # 3. Solve
        print("DEBUG: Solving...")
        solver = cp_model.CpSolver()
        solver.parameters.log_search_progress = True
        solver.parameters.max_time_in_seconds = 60.0  # 60 second timeout
        status = solver.Solve(self.model)

        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            return self._extract_solution_from_assignments(solver)
        else:
            print(f"DEBUG: No solution found. Status: {status}")
            return None
    
    def _extract_solution_from_assignments(self, solver):
        """Extract solution from assignment-based variables"""
        schedule = []
        slot_info = {t.id: t for t in self.slots}
        
        for key, var in self.vars.items():
            if solver.Value(var) == 1:
                idx, rid, tid = key
                assignment = self.required_assignments[idx]
                slot = slot_info.get(tid)
                
                schedule.append({
                    "class_group_id": assignment['group_id'],
                    "subject_id": assignment['subject_id'],
                    "room_id": rid,
                    "time_slot_id": tid,
                    "teacher_id": assignment['teacher_id'],
                    "day": slot.day,
                    "period": slot.period
                })
        
        return schedule
    
    def _solve_cartesian(self):
        """Old cartesian product method - fallback only"""
        # 1. Create Variables - create for ALL combinations
        print("DEBUG: Creating variables...")
        for g in self.groups:
            for s in self.subjects:
                for r in self.rooms:
                    for t in self.slots:
                        if t.is_break: 
                            continue
                        
                        # Create variables for ALL non-break slots
                        self.vars[(g.id, s.id, r.id, t.id)] = self.model.NewBoolVar(
                            f'x_g{g.id}_s{s.id}_r{r.id}_t{t.id}'
                        )

        print(f"DEBUG: Created {len(self.vars)} variables")
        print(f"DEBUG: Groups: {len(self.groups)}, Subjects: {len(self.subjects)}, Rooms: {len(self.rooms)}, Non-break slots: {len([t for t in self.slots if not t.is_break])}")

        # 2. Constraints
        print(f"DEBUG: Applying constraints...")
        
        # Helper: Get all variables for a group at a specific slot
        def get_group_slot_vars(group_id, slot_id):
            vars_list = []
            for s in self.subjects:
                for r in self.rooms:
                    if (group_id, s.id, r.id, slot_id) in self.vars:
                        vars_list.append(self.vars[(group_id, s.id, r.id, slot_id)])
            return vars_list

        # C1: REQUIREMENT - Each group must have each subject exactly once
        req_count = 0
        for g in self.groups:
            for s in self.subjects:
                # All time slots for this group + subject combination
                subject_vars = []
                for r in self.rooms:
                    for t in self.slots:
                        if not t.is_break and (g.id, s.id, r.id, t.id) in self.vars:
                            subject_vars.append(self.vars[(g.id, s.id, r.id, t.id)])
                if subject_vars:
                    # Group must have subject exactly once (across all slots)
                    self.model.Add(sum(subject_vars) == 1)
                    req_count += 1
        print(f"DEBUG: Added {req_count} requirement constraints (each group-subject once)")

        # C2: Group No Overlaps (at slot level)
        overlap_count = 0
        for g in self.groups:
            for t in self.slots:
                if t.is_break: continue
                g_vars = get_group_slot_vars(g.id, t.id)
                if g_vars:
                    self.model.Add(sum(g_vars) <= 1)
                    overlap_count += 1
        print(f"DEBUG: Added {overlap_count} group overlap constraints")

        # C3: Room No Overlaps
        room_overlap_count = 0
        for r in self.rooms:
            for t in self.slots:
                if t.is_break: continue
                r_vars = []
                for g in self.groups:
                    for s in self.subjects:
                        if (g.id, s.id, r.id, t.id) in self.vars:
                            r_vars.append(self.vars[(g.id, s.id, r.id, t.id)])
                if r_vars:
                    self.model.Add(sum(r_vars) <= 1)
                    room_overlap_count += 1
        print(f"DEBUG: Added {room_overlap_count} room overlap constraints")

        # C4: Teacher No Overlaps
        teacher_map = {s.id: s.teacher_id for s in self.subjects if s.teacher_id}
        teacher_overlap_count = 0
        for tid in set(teacher_map.values()):
            for t in self.slots:
                if t.is_break: continue
                t_vars = []
                for s in self.subjects:
                    if s.teacher_id == tid:
                        for g in self.groups:
                            for r in self.rooms:
                                if (g.id, s.id, r.id, t.id) in self.vars:
                                    t_vars.append(self.vars[(g.id, s.id, r.id, t.id)])
                if t_vars:
                    self.model.Add(sum(t_vars) <= 1)
                    teacher_overlap_count += 1
        print(f"DEBUG: Added {teacher_overlap_count} teacher overlap constraints")

        # 3. Solve
        print("DEBUG: Solving...")
        solver = cp_model.CpSolver()
        solver.parameters.log_search_progress = True  # Enable logging
        status = solver.Solve(self.model)

        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            return self._extract_solution(solver)
        else:
            print("DEBUG: No solution found.")
            return None

    def _extract_solution(self, solver):
        schedule = []
        subject_to_teacher = {s.id: s.teacher_id for s in self.subjects}
        subject_info = {s.id: s for s in self.subjects}
        slot_info = {t.id: t for t in self.slots}
        
        for key, var in self.vars.items():
            if solver.Value(var) == 1:
                gid, sid, rid, tid = key
                subject = subject_info.get(sid)
                slot = slot_info.get(tid)
                
                # Add the main entry
                schedule.append({
                    "class_group_id": gid,
                    "subject_id": sid,
                    "room_id": rid,
                    "time_slot_id": tid,
                    "teacher_id": subject_to_teacher.get(sid),
                    "day": slot.day,
                    "period": slot.period
                })
                
                # If Lab, add the implicit following slot (Period 6)
                if subject.is_lab and subject.duration_slots > 1 and slot.period == 5:
                    # Find period 6 slot
                    p6_slot = next((t for t in self.slots if t.day == slot.day and t.period == 6), None)
                    if p6_slot:
                        schedule.append({
                            "class_group_id": gid,
                            "subject_id": sid,
                            "room_id": rid,
                            "time_slot_id": p6_slot.id,
                            "teacher_id": subject_to_teacher.get(sid),
                            "day": slot.day,
                            "period": 6
                        })
        
        return schedule
