
from typing import List, Dict
from ...domain.entities.all_entities import Teacher, Subject, Room, ClassGroup, TimeSlot

class HardConstraints:
    @staticmethod
    def check_teacher_overlap(schedule: List[Dict]) -> List[str]:
        conflicts = []
        # (teacher_id, slot_id) -> list of entries
        usage = {}
        for entry in schedule:
            key = (entry['teacher_id'], entry['time_slot_id'])
            if key not in usage: usage[key] = []
            usage[key].append(entry)
        
        for key, entries in usage.items():
            if len(entries) > 1:
                conflicts.append(f"Teacher {key[0]} has {len(entries)} classes at slot {key[1]}")
        return conflicts

    @staticmethod
    def check_room_overlap(schedule: List[Dict]) -> List[str]:
        conflicts = []
        usage = {}
        for entry in schedule:
            key = (entry['room_id'], entry['time_slot_id'])
            if key not in usage: usage[key] = []
            usage[key].append(entry)
        
        for key, entries in usage.items():
            if len(entries) > 1:
                conflicts.append(f"Room {key[0]} is double-booked at slot {key[1]}")
        return conflicts

    @staticmethod
    def check_room_capacity(schedule: List[Dict], groups: List[ClassGroup], rooms: List[Room]) -> List[str]:
        conflicts = []
        group_map = {g.id: g.student_count for g in groups}
        room_map = {r.id: r.capacity for r in rooms}
        
        for entry in schedule:
            if group_map[entry['class_group_id']] > room_map[entry['room_id']]:
                conflicts.append(f"Room {entry['room_id']} capacity too small for Group {entry['class_group_id']}")
        return conflicts

class SoftConstraints:
    @staticmethod
    def calculate_gaps(schedule: List[Dict], teachers: List[Teacher], slots: List[TimeSlot]) -> float:
        """
        Calculate penalty for gaps in teacher schedules.
        A gap is when a teacher has free periods between classes on the same day.
        """
        penalty = 0.0
        
        # Group schedule by teacher and day
        teacher_schedules = {}
        for entry in schedule:
            tid = entry['teacher_id']
            if not tid:
                continue
            if tid not in teacher_schedules:
                teacher_schedules[tid] = {}
            
            # Find the slot to get day information
            slot = next((s for s in slots if s.id == entry['time_slot_id']), None)
            if not slot or slot.is_break:
                continue
            
            day = slot.day
            if day not in teacher_schedules[tid]:
                teacher_schedules[tid][day] = []
            teacher_schedules[tid][day].append(slot.period)
        
        # Calculate gaps for each teacher on each day
        for tid, days in teacher_schedules.items():
            for day, periods in days.items():
                if len(periods) <= 1:
                    continue  # No gaps possible with 0 or 1 class
                
                # Sort periods
                sorted_periods = sorted(periods)
                
                # Count gaps (missing periods between first and last class)
                first_period = sorted_periods[0]
                last_period = sorted_periods[-1]
                total_span = last_period - first_period + 1
                actual_classes = len(sorted_periods)
                gaps = total_span - actual_classes
                
                # Penalize each gap
                penalty += gaps * 10.0
        
        return penalty

    @staticmethod
    def balance_workload(schedule: List[Dict], teachers: List[Teacher]) -> float:
        """
        Calculate penalty based on unbalanced workload distribution.
        Uses standard deviation - higher deviation means worse balance.
        """
        # Count classes per teacher
        teacher_loads = {t.id: 0 for t in teachers}
        for entry in schedule:
            tid = entry.get('teacher_id')
            if tid and tid in teacher_loads:
                teacher_loads[tid] += 1
        
        # Calculate standard deviation
        loads = list(teacher_loads.values())
        if not loads:
            return 0.0
        
        mean = sum(loads) / len(loads)
        variance = sum((x - mean) ** 2 for x in loads) / len(loads)
        std_dev = variance ** 0.5
        
        # Penalize based on standard deviation
        return std_dev * 5.0
    
    @staticmethod
    def consecutive_classes_penalty(schedule: List[Dict], slots: List[TimeSlot]) -> float:
        """
        Penalize teachers having too many consecutive classes without breaks.
        More than 3 consecutive classes is tiring.
        """
        penalty = 0.0
        
        # Group by teacher and day
        teacher_day_schedules = {}
        for entry in schedule:
            tid = entry.get('teacher_id')
            if not tid:
                continue
            
            slot = next((s for s in slots if s.id == entry['time_slot_id']), None)
            if not slot or slot.is_break:
                continue
            
            key = (tid, slot.day)
            if key not in teacher_day_schedules:
                teacher_day_schedules[key] = []
            teacher_day_schedules[key].append(slot.period)
        
        # Check for long consecutive sequences
        for (tid, day), periods in teacher_day_schedules.items():
            sorted_periods = sorted(periods)
            
            # Find consecutive sequences
            consecutive_count = 1
            max_consecutive = 1
            
            for i in range(1, len(sorted_periods)):
                if sorted_periods[i] == sorted_periods[i-1] + 1:
                    consecutive_count += 1
                    max_consecutive = max(max_consecutive, consecutive_count)
                else:
                    consecutive_count = 1
            
            # Penalize if more than 3 consecutive classes
            if max_consecutive > 3:
                penalty += (max_consecutive - 3) * 8.0
        
        return penalty
    
    @staticmethod
    def total_soft_score(schedule: List[Dict], teachers: List[Teacher], slots: List[TimeSlot]) -> float:
        """
        Calculate total soft constraint penalty.
        Lower score is better.
        """
        gap_penalty = SoftConstraints.calculate_gaps(schedule, teachers, slots)
        balance_penalty = SoftConstraints.balance_workload(schedule, teachers)
        consecutive_penalty = SoftConstraints.consecutive_classes_penalty(schedule, slots)
        
        return gap_penalty + balance_penalty + consecutive_penalty

