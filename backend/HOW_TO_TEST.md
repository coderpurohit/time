# How to Test the Auto-Substitution System

## Method 1: Interactive API Docs (Easiest) 🎯

1. **Open in your browser**: http://localhost:8000/docs

2. **Test Auto-Assignment**:
   - Scroll down to **"substitutions"** section
   - Find `POST /api/substitutions/auto-assign`
   - Click "**Try it out**"
   - Enter parameters:
     ```
     teacher_id: 1
     date: 2026-02-05
     auto_notify: false
     ```
   - Click "**Execute**"
   - See the result with substitute assignment and scoring!

3. **View Ranked Suggestions**:
   - Find `GET /api/substitutions/suggestions/{entry_id}/ranked`
   - Click "**Try it out**"
   - Enter: `entry_id: 1` and `top_n: 5`
   - Click "**Execute**"
   - See all substitutes ranked by score!

---

## Method 2: Using Python Script 🐍

Run the test script:
```bash
cd backend
python test_quick.py
```

This will automatically test:
- Server health
- Auto-assignment
- Ranked suggestions
- Bulk operations

---

## Method 3: Using Postman/Thunder Client 📮

### Test 1: Auto-Assignment
```http
POST http://localhost:8000/api/substitutions/auto-assign?teacher_id=1&date=2026-02-05&auto_notify=false
```

### Test 2: Ranked Suggestions
```http
GET http://localhost:8000/api/substitutions/suggestions/1/ranked?top_n=5
```

### Test 3: Bulk Assignment
```http
POST http://localhost:8000/api/substitutions/auto-assign-bulk
Content-Type: application/json

{
  "absences": [
    {"teacher_id": 1, "date": "2026-02-06"},
    {"teacher_id": 2, "date": "2026-02-06"}
  ],
  "auto_notify": false
}
```

---

## Method 4: Using curl (Command Line) 💻

```bash
# Test auto-assignment
curl -X POST "http://localhost:8000/api/substitutions/auto-assign?teacher_id=1&date=2026-02-05&auto_notify=false"

# Test ranked suggestions
curl "http://localhost:8000/api/substitutions/suggestions/1/ranked?top_n=5"

# Test bulk assignment
curl -X POST "http://localhost:8000/api/substitutions/auto-assign-bulk" \
  -H "Content-Type: application/json" \
  -d '{
    "absences": [
      {"teacher_id": 1, "date": "2026-02-06"},
      {"teacher_id": 2, "date": "2026-02-06"}
    ],
    "auto_notify": false
  }'
```

---

## What to Expect

### ✅ Successful Auto-Assignment Response:
```json
{
  "success": true,
  "teacher_name": "Dr. Rajesh Kumar",
  "affected_classes": 5,
  "substitute_assigned": "Prof. Priya Sharma",
  "confidence_score": 225.0,
  "score_breakdown": {
    "availability": 100,
    "subject_expertise": 80,
    "workload_balance": 45
  },
  "assignments": [...],
  "alternative_substitutes": [...]
}
```

### 🎯 Ranked Suggestions Response:
```json
{
  "entry_id": 1,
  "total_suggestions": 4,
  "ranked_substitutes": [
    {
      "teacher_id": 2,
      "teacher_name": "Prof. Priya Sharma",
      "score": 225.0,
      "available": true,
      "teaches_same_subject": true,
      "current_workload": 12
    }
  ]
}
```

---

## Test Scenarios to Try

### Scenario 1: Basic Auto-Assignment
- Teacher ID: `1`
- Date: `2026-02-05`
- Expected: Finds best substitute automatically

### Scenario 2: Same Day Multiple Absences
- Teacher IDs: `1`, `2`
- Date: `2026-02-05`
- Use bulk endpoint
- Expected: Assigns different substitutes efficiently

### Scenario 3: Teacher with No Available Substitute
- Teacher ID: (try different IDs)
- Expected: Returns cancellation notice

---

## Troubleshooting

**Error: "No timetable found"**
- Generate a timetable first:
  ```
  POST /api/solvers/generate
  {
    "algorithm": "csp",
    "class_groups": [1, 2, 3]
  }
  ```

**Error: "Cannot connect"**
- Make sure backend is running: `cd backend && start.bat`

**Error: "Teacher not found"**
- Check available teachers: `GET /api/teachers/`

---

## Quick Links

- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **All Teachers**: http://localhost:8000/api/teachers/
- **All Timetables**: http://localhost:8000/api/timetables/

---

**Recommended**: Start with Method 1 (Browser API Docs) - it's the easiest and most visual!
