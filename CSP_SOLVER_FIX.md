# CSP Solver Fix Summary

## Problem
The CSP (Constraint Satisfaction Problem) timetable solver was failing to generate timetables. The solver would return OPTIMAL status but with no variables actually assigned (all 0 values), resulting in empty timetables.

## Root Cause
The solver had **only overlap-prevention constraints** (at_most_one constraints):
- Group cannot have 2+ classes at same time slot
- Room cannot have 2+ classes at same time slot  
- Teacher cannot teach 2+ classes at same time slot

**But NO positive assignment constraints** - meaning there was no requirement to actually assign anything.

The OR-Tools presolve phase would:
1. See that variables had no forcing constraints
2. Remove all variables as "unused" 
3. Leave a vacuous model with 0 variables
4. Declare OPTIMAL with empty solution

## Solution
Added **C1: Requirement Constraint** - Each group must have each subject assigned exactly once:

```python
# C1: REQUIREMENT - Each group must have each subject exactly once
for g in self.groups:
    for s in self.subjects:
        subject_vars = []
        for r in self.rooms:
            for t in self.slots:
                if not t.is_break and (g.id, s.id, r.id, t.id) in self.vars:
                    subject_vars.append(self.vars[(g.id, s.id, r.id, t.id)])
        if subject_vars:
            self.model.Add(sum(subject_vars) == 1)  # Forces assignment
```

This ensures:
- Variables are no longer "unused"
- OR-Tools must find valid assignments
- Overlap constraints keep solutions valid

## Result
✅ **Timetable Generation Now Works**
- 28 entries generated
- All 4 class groups assigned all 7 subjects
- Valid time slots and rooms
- No overlaps (rooms, teachers, groups respected)

## File Modified
- `backend/app/solver/csp_solver.py` - Added requirement constraint to C1

## Testing
```bash
# Request generation
curl -X POST http://localhost:8000/api/solvers/generate \
  -H "Content-Type: application/json" \
  -d '{"algorithm":"csp","class_groups":[1,2,3]}'

# Check result
curl http://localhost:8000/api/timetables/latest
```

Result: Status "active", 28 valid entries, all groups have all subjects assigned.
