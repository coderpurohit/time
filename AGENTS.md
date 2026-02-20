# AGENTS.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview
Automated college timetable generation system using constraint satisfaction (CSP) and genetic algorithms. Includes intelligent teacher substitution with scoring-based assignment.

## Build & Run Commands

### Backend (FastAPI + SQLite)
```bash
# Quick start (Windows) - auto-creates venv, installs deps, seeds DB
cd backend && start.bat

# Manual setup
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Server runs at http://localhost:8000, API docs at /docs

### Frontend (React + Vite + Tailwind)
```bash
cd frontend
npm install
npm run dev      # Development server at localhost:5173
npm run build    # Production build
npm run lint     # ESLint
```

## Testing

Backend tests use `requests` library against a running server (not pytest fixtures):
```bash
# Start backend first, then:
cd backend
python tests/test_api_flow.py           # Basic CRUD + solver flow
python tests/test_auto_substitution.py  # Substitution system
python tests/test_operational.py        # Operational endpoints
```

Interactive API testing: http://localhost:8000/docs

## Architecture

### Backend Clean Architecture (`backend/app/`)
- **`api/routers/`** - FastAPI endpoints (timetables, teachers, subjects, rooms, solvers, substitutions, analytics, imports)
- **`domain/entities/`** - Business entities (Teacher, Subject, Room, ClassGroup, TimeSlot)
- **`infrastructure/`** - SQLAlchemy models and database session management
- **`services/`** - Business logic (auto_assignment.py for substitute scoring, timetable_service.py)
- **`solver/`** - Timetable generation algorithms:
  - `csp_solver.py` - OR-Tools CP-SAT constraint satisfaction
  - `genetic_solver.py` - Genetic algorithm alternative

### Key Data Flow
1. Admin creates Teachers, Subjects, Rooms, ClassGroups, TimeSlots via CRUD APIs
2. `POST /api/solvers/generate?method=csp|genetic` generates timetable
3. Solution stored in `timetable_versions` + `timetable_entries` tables
4. Substitution system scores candidates by availability (100pts), expertise (80pts), workload (50pts)

### Database
SQLite at `backend/timetable.db`. Models in `infrastructure/models.py`:
- Core: Teacher, Subject, Room, ClassGroup, TimeSlot
- Timetable: TimetableVersion, TimetableEntry
- Operational: Holiday, Substitution, ScheduleConfig

### Frontend (`frontend/src/`)
- React 18 with Vite
- Zustand for state management
- Tailwind CSS for styling
- Features: `src/features/modeling/` (TeacherForm), `src/features/scheduler/` (SchedulerGrid)

## Key API Patterns
- All APIs prefixed with `/api/`
- CORS configured for localhost:5173, 3000, 8080
- Solver endpoint: `POST /api/solvers/generate?method=csp` (body optional)
- Auto-substitution: `POST /api/substitutions/auto-assign?teacher_id=X&date=YYYY-MM-DD`

## CSP Solver Constraints
The constraint solver enforces:
- Each group-subject combination assigned exactly once
- No group overlap (one class per slot)
- No room overlap (one booking per slot)
- No teacher overlap (one assignment per slot)
- Lab sessions span multiple consecutive slots when `duration_slots > 1`
