# 🎓 College Timetable Generator

An automated college timetable generation system using constraint satisfaction (CSP) and genetic algorithms with intelligent teacher substitution.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ Features

### 📅 Timetable Management
- **Automated Generation**: CSP and genetic algorithm-based timetable generation
- **Smart Scheduling**: Constraint-based optimization for conflict-free schedules
- **Multi-view Display**: Calendar view, grid view, and detailed reports
- **Export Options**: PDF, CSV, and print-friendly formats
- **Real-time Updates**: Instant timetable updates when resources change

### 👥 Resource Management
- **Teachers**: CRUD operations with workload tracking and availability management
- **Classes**: Manage class groups with student count and coverage tracking
- **Subjects**: Theory and lab subjects with duration and room requirements
- **Rooms**: Room allocation with capacity and utilization tracking
- **Time Slots**: Flexible configuration for teaching hours and breaks

### 📊 Analytics & Reports
- **Teacher Workload**: Visual charts showing load distribution across all teachers
- **Room Utilization**: Pie charts and usage statistics for optimal space planning
- **Coverage Reports**: Class-wise and subject-wise coverage analysis
- **Key Insights**: Busiest teachers, most used rooms, popular subjects at a glance
- **Load Factor Analysis**: Real-time monitoring of teacher and class loads

### 🔄 Advanced Features
- **Intelligent Substitution**: Scoring-based teacher replacement (availability, expertise, workload)
- **Bulk Import**: CSV import for teachers, subjects, classes, and rooms
- **Conflict Detection**: Automatic detection of scheduling conflicts
- **Load Balancing**: Even distribution of workload across teachers
- **Multi-period Labs**: Support for lab sessions spanning multiple consecutive periods
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices

## 🚀 Quick Start

### Prerequisites
- **Python 3.11+** (Download from [python.org](https://www.python.org/downloads/))
- **Git** (Download from [git-scm.com](https://git-scm.com/downloads))
- **pip** (Comes with Python)

### Installation & Setup

#### Step 1: Clone the Repository
```bash
git clone https://github.com/coderpurohit/time.git
cd time
```

#### Step 2: Start the Backend

**For Windows:**
```bash
cd backend
start.bat
```

**For Mac/Linux:**
```bash
cd backend
./start.sh
```
Note: The script is already executable. If you get a permission error, run: `chmod +x start.sh`

**Or manually:**
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend will:
- ✅ Create a virtual environment
- ✅ Install all dependencies
- ✅ Initialize the SQLite database
- ✅ Start the server on http://localhost:8000

#### Step 3: Access the Application

Open your browser and navigate to:

**Main Application:**
- 🎓 **Timetable Management**: http://localhost:8000/timetable_page.html
- 📅 **Calendar View**: http://localhost:8000/calendar_page.html
- 📊 **Reports & Analytics**: http://localhost:8000/reports_page.html
- 🏠 **Dashboard**: http://localhost:8000/dashboard.html

**API Documentation:**
- 📖 **Swagger UI**: http://localhost:8000/docs
- 📖 **ReDoc**: http://localhost:8000/redoc

### ⚡ Quick Start Commands

```bash
# Clone and start in one go
git clone https://github.com/coderpurohit/time.git && cd time/backend && start.bat
```

### 🛑 Stopping the Server

**Windows:**
- Press `Ctrl + C` in the terminal
- Or run: `cd backend && stop.bat`

**Mac/Linux:**
- Press `Ctrl + C` in the terminal

## 📖 Usage

### 1. Setup Resources
Navigate through the wizard tabs:
1. **Subjects/Courses**: Add subjects with type (theory/lab), duration, and room requirements
2. **Teachers**: Add teachers with max hours per week
3. **Classes**: Add class groups with student count
4. **Rooms**: Add rooms with capacity and type
5. **Lessons**: Define lesson requirements (optional)

### 2. Generate Timetable
- Click "Generate New Schedule" button
- Choose CSP or Genetic algorithm
- System automatically creates conflict-free schedule

### 3. View & Export
- **Review Tab**: See full timetable grid
- **Calendar**: Monthly view with daily schedules
- **Reports**: Analytics and workload distribution
- **Export**: Download as PDF or CSV

## 🏗️ Architecture

### Backend (FastAPI + SQLite)
```
backend/
├── app/
│   ├── api/routers/      # API endpoints
│   ├── domain/entities/  # Business entities
│   ├── infrastructure/   # Database models
│   ├── services/         # Business logic
│   └── solver/           # CSP & Genetic algorithms
├── timetable.db          # SQLite database
└── requirements.txt      # Python dependencies
```

### Frontend (Vanilla JS + HTML/CSS)
```
root/
├── timetable_page.html   # Main timetable interface
├── calendar_page.html    # Calendar view
├── reports_page.html     # Analytics dashboard
├── dashboard.html        # Landing page
└── *.js                  # JavaScript modules
```

## 🔧 Configuration

### Time Slots
Configure in Review tab:
- Teaching hours per day
- Days of the week
- Lunch break timing
- Period duration

### Constraints
The CSP solver enforces:
- No teacher overlap (one class per slot)
- No room overlap (one booking per slot)
- No class overlap (one period per slot)
- Lab sessions span consecutive slots

## 📊 Database Schema

### Core Tables
- `teachers` - Teacher information and availability
- `subjects` - Subject details and requirements
- `rooms` - Room capacity and resources
- `class_groups` - Class information
- `time_slots` - Available time slots

### Timetable Tables
- `timetable_versions` - Generated timetables
- `timetable_entries` - Individual schedule entries
- `lessons` - Lesson requirements (optional)

### Operational Tables
- `holidays` - Holiday calendar
- `substitutions` - Teacher substitutions
- `schedule_config` - Configuration settings

## 🧪 Testing

```bash
cd backend

# Start server first
start.bat

# Run tests
python tests/test_api_flow.py
python tests/test_auto_substitution.py
python tests/test_operational.py
```

## 🔧 Troubleshooting

### Server Won't Start

**Issue**: Port 8000 already in use
```bash
# Windows: Find and kill process using port 8000
netstat -ano | findstr :8000
taskkill /PID <process_id> /F

# Mac/Linux: Find and kill process using port 8000
lsof -ti:8000 | xargs kill -9
```

**Issue**: Python not found
- Ensure Python 3.11+ is installed: `python --version` or `python3 --version`
- Add Python to your system PATH
- Download from [python.org](https://www.python.org/downloads/)

**Issue**: Module not found errors
```bash
cd backend
# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Reinstall dependencies
pip install -r requirements.txt
```

### Frontend Issues

**Issue**: Changes not showing up
- Hard refresh your browser: `Ctrl + Shift + R` (Windows/Linux) or `Cmd + Shift + R` (Mac)
- Clear browser cache
- Check browser console for errors (F12)

**Issue**: API connection errors
- Verify backend is running at http://localhost:8000
- Check CORS settings in `backend/app/main.py`
- Ensure no firewall blocking port 8000

### Database Issues

**Issue**: Database locked or corrupted
```bash
cd backend
# Backup existing database
copy timetable.db timetable.db.backup  # Windows
cp timetable.db timetable.db.backup    # Mac/Linux

# Reset database
python setup_database.py
```

**Issue**: No data showing up
- Check if database exists: `backend/timetable.db`
- Verify data via API docs: http://localhost:8000/docs
- Try regenerating timetable from the UI

### Common Errors

**"INFEASIBLE" when generating timetable**
- Too many lessons for available time slots
- Conflicting constraints (teacher/room availability)
- Reduce lesson count or increase available time slots

**"Unknown Subject" in timetable**
- Subject was deleted but still referenced in lessons
- Regenerate timetable after adding/removing subjects

**Teachers not balanced**
- Ensure all teachers have reasonable max hours per week
- Check lesson assignments in Lessons tab
- Regenerate timetable to redistribute load

## 📝 API Documentation

Interactive API documentation available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Key Endpoints
- `GET /api/teachers/` - List all teachers
- `POST /api/solvers/generate` - Generate timetable
- `GET /api/timetables/latest` - Get latest timetable
- `POST /api/substitutions/auto-assign` - Auto-assign substitute

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OR-Tools for constraint programming
- FastAPI for the backend framework
- Chart.js for data visualization

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

**Made with ❤️ for educational institutions**
