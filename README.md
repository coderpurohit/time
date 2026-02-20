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

### 👥 Resource Management
- **Teachers**: CRUD operations with workload tracking and availability management
- **Classes**: Manage class groups with student count and coverage tracking
- **Subjects**: Theory and lab subjects with duration and room requirements
- **Rooms**: Room allocation with capacity and utilization tracking

### 📊 Analytics & Reports
- **Teacher Workload**: Visual charts showing load distribution
- **Room Utilization**: Pie charts and usage statistics
- **Coverage Reports**: Class-wise and subject-wise coverage analysis
- **Key Insights**: Busiest teachers, most used rooms, popular subjects

### 🔄 Advanced Features
- **Intelligent Substitution**: Scoring-based teacher replacement (availability, expertise, workload)
- **Bulk Import**: CSV import for teachers, subjects, classes, and rooms
- **Conflict Detection**: Automatic detection of scheduling conflicts
- **Load Balancing**: Even distribution of workload across teachers

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- pip (Python package manager)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/timetable-generator.git
cd timetable-generator
```

2. **Start the backend** (Windows)
```bash
cd backend
start.bat
```

The backend will:
- Create a virtual environment
- Install dependencies
- Initialize the database
- Start the server on http://localhost:8000

3. **Access the application**
- Main App: http://localhost:8000/timetable_page.html
- Calendar: http://localhost:8000/calendar_page.html
- Reports: http://localhost:8000/reports_page.html
- API Docs: http://localhost:8000/docs

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
