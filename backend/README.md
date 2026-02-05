# TimeTable Generator Backend

**100% Automated** FastAPI backend with intelligent teacher substitution system.

## 🚀 Quick Start (One Command!)

Just double-click `start.bat` or run:
```bash
start.bat
```

That's it! The script automatically:
- ✅ Creates virtual environment (if needed)
- ✅ Installs dependencies (if needed)
- ✅ Initializes database with sample data (if needed)
- ✅ Starts the backend server
- ✅ Opens at http://localhost:8000

## 📋 Available Scripts

### `start.bat`
**Interactive mode** - Server runs in current window
- Perfect for development
- See real-time logs
- Press Ctrl+C to stop

### `start-bg.bat`  
**Background mode** - Server runs in background
- Starts server silently
- Logs to `backend.log`
- Use `stop.bat` to stop

### `stop.bat`
**Stop server** - Gracefully terminates backend
- Finds and stops running backend
- Safe shutdown

## 🎯 Features

### Core Functionality
- **Automated Timetable Generation** using CSP and Genetic Algorithms
- **Constraint Management** (hard/soft constraints)
- **Resource Optimization** (teachers, rooms, time slots)
- **Analytics & Reporting**

### 🤖 NEW: Automated Teacher Substitution
**Zero manual work required!**

#### One-Click Auto-Assignment
```bash
POST /api/substitutions/auto-assign?teacher_id=1&date=2026-02-05
```
Automatically:
- Finds all affected classes
- Scores all available teachers (availability + expertise + workload)
- Assigns best substitute
- Returns detailed report

#### Bulk Operations
```bash
POST /api/substitutions/auto-assign-bulk
{
  "absences": [
    {"teacher_id": 1, "date": "2026-02-05"},
    {"teacher_id": 3, "date": "2026-02-05"}
  ]
}
```
Process multiple absences instantly!

#### Intelligent Scoring
Substitutes are ranked by:
- **Availability** (100 points) - Free during required time slots
- **Subject Expertise** (80 points) - Teaches same/related subject  
- **Workload Balance** (50 points) - Less busy teachers preferred

#### Ranked Suggestions
```bash
GET /api/substitutions/suggestions/{entry_id}/ranked?top_n=5
```
Get AI-ranked substitute recommendations with detailed scores.

## 📚 API Endpoints

### Core APIs
- `GET /` - API info and status
- `GET /health` - Health check
- `GET /docs` - Interactive API documentation

### Teachers
- `GET /api/teachers/` - List all teachers
- `POST /api/teachers/` - Add teacher
- `GET /api/teachers/{id}` - Get teacher details

### Subjects, Rooms, Classes
- `/api/subjects/` - Subject management
- `/api/rooms/` - Room management  
- `/api/class-groups/` - Class group management

### Timetables
- `POST /api/solvers/generate` - Generate timetable
- `GET /api/timetables/` - View timetables
- `POST /api/solvers/optimize` - Optimize existing timetable

### Substitutions (Automated)
- `POST /api/substitutions/auto-assign` - Auto-assign substitute
- `POST /api/substitutions/auto-assign-bulk` - Bulk auto-assignment
- `GET /api/substitutions/suggestions/{id}/ranked` - Get ranked suggestions
- `POST /api/substitutions/mark-absent` - Mark teacher absent
- `POST /api/substitutions/assign` - Manual assignment
- `GET /api/substitutions/by-date/{date}` - View substitutions

### Analytics
- `GET /api/analytics/teacher-utilization` - Teacher workload analysis
- `GET /api/analytics/room-utilization` - Room usage stats

## 🔧 Manual Setup (If Needed)

If you want to set up manually:

```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate it
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Initialize database (optional - auto-runs on startup)
python setup_database.py

# 5. Start server
uvicorn app.main:app --reload
```

## 📊 Database

- **Type**: SQLite (development) / PostgreSQL (production-ready)
- **Auto-initialization**: Database is created and seeded automatically on first run
- **Location**: `timetable.db`

### Sample Data Included
- 5 Teachers
- 4 Rooms (2 lecture halls, 2 labs)
- 3 Class Groups
- 8 Subjects (including labs)
- 40 Time Slots (Mon-Fri, 8 periods/day)

## 🧪 Testing

Run automated tests:
```bash
python tests/test_auto_substitution.py
```

Test individual endpoints via:
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🏗️ Architecture

```
backend/
├── app/
│   ├── api/routers/        # API endpoints
│   │   ├── substitutions.py  # Auto-assignment endpoints
│   │   ├── timetables.py
│   │   └── ...
│   ├── services/           # Business logic
│   │   ├── auto_assignment.py  # Intelligent scoring
│   │   ├── notifications.py    # Email notifications
│   │   └── timetable_service.py
│   ├── solver/             # Algorithms
│   │   ├── csp_solver.py
│   │   └── genetic_solver.py
│   ├── infrastructure/     # Database
│   │   ├── models.py
│   │   └── database.py
│   └── main.py            # FastAPI app with auto-init
├── start.bat              # 🚀 ONE-CLICK START
├── start-bg.bat           # Background mode
├── stop.bat               # Stop server
└── requirements.txt
```

## 💡 Usage Examples

### Generate Timetable
```python
import requests

response = requests.post("http://localhost:8000/api/solvers/generate", json={
    "algorithm": "csp",
    "class_groups": [1, 2, 3],
    "constraints": {...}
})
```

### Auto-Assign Substitute
```python
response = requests.post(
    "http://localhost:8000/api/substitutions/auto-assign",
    params={
        "teacher_id": 1,
        "date": "2026-02-05",
        "auto_notify": False
    }
)

result = response.json()
print(f"Substitute: {result['substitute_assigned']}")
print(f"Classes: {result['affected_classes']}")
print(f"Score: {result['confidence_score']}")
```

## 🔥 What's New in v2.0

- ✅ **100% Automated Startup** - No manual setup required
- ✅ **Auto-Database Initialization** - Runs on first start
- ✅ **Intelligent Substitution** - AI-powered substitute matching
- ✅ **Bulk Operations** - Handle multiple absences at once
- ✅ **Health Monitoring** - `/health` endpoint for status checks
- ✅ **Background Mode** - Run server silently

## 📝 Configuration

Environment variables (optional):
```
DATABASE_URL=sqlite:///./timetable.db
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_EMAIL=your-email@gmail.com
SMTP_PASSWORD=your-password
```

## 🤝 Support

- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Logs**: Check `backend.log` (in background mode)

---

**Made with ❤️ for automated college scheduling**
