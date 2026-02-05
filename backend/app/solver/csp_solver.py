from ortools.sat.python import cp_model
from typing import List, Dict, Any
from ..domain.entities.all_entities import Teacher, Subject, Room, ClassGroup, TimeSlot

class CspTimetableSolver:
    def __init__(self, teachers: List[Teacher], subjects: List[Subject], 
                 rooms: List[Room], groups: List[ClassGroup], slots: List[TimeSlot]):
        self.teachers = teachers
        self.subjects = subjects
        self.rooms = rooms
        self.groups = groups
        self.slots = slots
        self.model = cp_model.CpModel()
        self.vars = {} # (group, subject, room, slot) -> BoolVar

    def solve(self):
        # 1. Create Variables
        # x[group_id, subject_id, room_id, slot_id] = 1 if scheduled
        for g in self.groups:
            for s in self.subjects:
                # Optimized: Only consider rooms that match the subject requirement
                valid_rooms = [r for r in self.rooms if r.type == s.required_room_type and r.capacity >= g.student_count]
                for r in valid_rooms:
                    for t in self.slots:
                        if t.is_break: continue
                        self.vars[(g.id, s.id, r.id, t.id)] = self.model.NewBoolVar(
                            f'x_g{g.id}_s{s.id}_r{r.id}_t{t.id}'
                        )

        # 2. Hard Constraints

        # C1: Each subject for a group must be taught exactly once (Simplified)
        for g in self.groups:
            for s in self.subjects:
                # Filter variables for this specific (g, s)
                assignments = []
                for r in self.rooms:
                    for t in self.slots:
                        if (g.id, s.id, r.id, t.id) in self.vars:
                            assignments.append(self.vars[(g.id, s.id, r.id, t.id)])
                
                if assignments:
                    self.model.Add(sum(assignments) == 1)
        
        # C2: No Overlaps - A Group can't be in 2 places at once
        for g in self.groups:
            for t in self.slots:
                # Sum of all assignments for this group at this time <= 1
                group_assignments = []
                for s in self.subjects:
                    for r in self.rooms:
                        if (g.id, s.id, r.id, t.id) in self.vars:
                            group_assignments.append(self.vars[(g.id, s.id, r.id, t.id)])
                if group_assignments:
                    self.model.Add(sum(group_assignments) <= 1)

        # C3: No Overlaps - A Room can't hold 2 classes at once
        for r in self.rooms:
            for t in self.slots:
                room_assignments = []
                for g in self.groups:
                    for s in self.subjects:
                        if (g.id, s.id, r.id, t.id) in self.vars:
                            room_assignments.append(self.vars[(g.id, s.id, r.id, t.id)])
                if room_assignments:
                    self.model.Add(sum(room_assignments) <= 1)

        # C4: No Overlaps - A Teacher can't teach 2 classes at once
        # We need a map of Subject -> Teacher
        subject_teacher_map = {s.id: s.teacher_id for s in self.subjects if s.teacher_id}
        
        # For each teacher, for each slot, sum of their subjects <= 1
        teachers_ids = set(subject_teacher_map.values())
        for tid in teachers_ids:
            for t in self.slots:
                teacher_assignments = []
                for s in self.subjects:
                    if s.teacher_id == tid: # This subject is taught by this teacher
                        for g in self.groups:
                            for r in self.rooms:
                                if (g.id, s.id, r.id, t.id) in self.vars:
                                    teacher_assignments.append(self.vars[(g.id, s.id, r.id, t.id)])
                if teacher_assignments:
                    self.model.Add(sum(teacher_assignments) <= 1)

        # C5: Lab Continuity (if subject.is_lab, slots must be consecutive)
        # Multi-slot labs must be scheduled in consecutive time slots on the same day
        for s in self.subjects:
            if s.is_lab and s.duration_slots > 1:
                for g in self.groups:
                    # Group slots by day for consecutive checking
                    slots_by_day = {}
                    for t in self.slots:
                        if not t.is_break:
                            if t.day not in slots_by_day:
                                slots_by_day[t.day] = []
                            slots_by_day[t.day].append(t)
                    
                    # Sort slots within each day by period
                    for day in slots_by_day:
                        slots_by_day[day] = sorted(slots_by_day[day], key=lambda x: x.period)
                    
                    # For each day, create helper variables for consecutive blocks
                    block_vars = []
                    for day, day_slots in slots_by_day.items():
                        # Check if we have enough consecutive slots for this lab
                        for i in range(len(day_slots) - s.duration_slots + 1):
                            # Check if slots are truly consecutive (no period gaps)
                            consecutive = True
                            for j in range(s.duration_slots - 1):
                                if day_slots[i + j + 1].period != day_slots[i + j].period + 1:
                                    consecutive = False
                                    break
                            
                            if consecutive:
                                # Create a block start variable
                                block_start_var = self.model.NewBoolVar(
                                    f'block_g{g.id}_s{s.id}_day{day}_p{day_slots[i].period}'
                                )
                                block_vars.append(block_start_var)
                                
                                # If block starts here, all consecutive slots must be assigned
                                for j in range(s.duration_slots):
                                    slot = day_slots[i + j]
                                    for r in self.rooms:
                                        if (g.id, s.id, r.id, slot.id) in self.vars:
                                            # If block starts, this slot must be scheduled
                                            self.model.Add(
                                                self.vars[(g.id, s.id, r.id, slot.id)] >= block_start_var
                                            )
                    
                    # Exactly one block must be selected for this lab
                    if block_vars:
                        self.model.Add(sum(block_vars) == 1)
                    
                    # Constraint: For multi-slot labs, either all consecutive slots are assigned or none
                    for day, day_slots in slots_by_day.items():
                        for i in range(len(day_slots) - s.duration_slots + 1):
                            consecutive = True
                            for j in range(s.duration_slots - 1):
                                if day_slots[i + j + 1].period != day_slots[i + j].period + 1:
                                    consecutive = False
                                    break
                            
                            if consecutive:
                                for r in self.rooms:
                                    # Collect variables for this consecutive block
                                    block_slot_vars = []
                                    for j in range(s.duration_slots):
                                        slot = day_slots[i + j]
                                        if (g.id, s.id, r.id, slot.id) in self.vars:
                                            block_slot_vars.append(self.vars[(g.id, s.id, r.id, slot.id)])
                                    
                                    # If any slot in the block is assigned, all must be assigned
                                    if len(block_slot_vars) == s.duration_slots:
                                        for k in range(len(block_slot_vars) - 1):
                                            self.model.Add(block_slot_vars[k] == block_slot_vars[k + 1])

        # 3. Solve
        solver = cp_model.CpSolver()
        status = solver.Solve(self.model)

        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            return self._extract_solution(solver)
        return None

    def _extract_solution(self, solver):
        schedule = []
        subject_to_teacher = {s.id: s.teacher_id for s in self.subjects}
        for key, var in self.vars.items():
            if solver.Value(var) == 1:
                gid, sid, rid, tid = key
                schedule.append({
                    "class_group_id": gid,
                    "subject_id": sid,
                    "room_id": rid,
                    "time_slot_id": tid,
                    "teacher_id": subject_to_teacher.get(sid)
                })
        return schedule
