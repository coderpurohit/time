# FastAPI Entry Point
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .infrastructure import models
from .infrastructure.database import engine, SessionLocal
from .api.routers import timetables, teachers, subjects, rooms, solvers, operational, analytics, substitutions

# Auto-create tables on startup
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="TimeTable Generator API",
    description="Automated timetable generation with intelligent teacher substitution",
    version="2.0.0"
)

origins = [
    "http://localhost:5173",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup event - auto-seed if database is empty
@app.on_event("startup")
async def startup_event():
    """Auto-initialize database with sample data if empty"""
    db = SessionLocal()
    try:
        # Check if database has any data
        teacher_count = db.query(models.Teacher).count()
        
        if teacher_count == 0:
            print("📊 Database is empty. Auto-seeding with sample data...")
            
            # Import and run seeding logic
            from sqlalchemy import create_engine
            from sqlalchemy.orm import sessionmaker
            from .infrastructure.database import SQLALCHEMY_DATABASE_URL
            
            # Time Slots
            slots = []
            for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
                for i in range(1, 9):
                    slots.append(models.TimeSlot(
                        day=day,
                        period=i,
                        start_time=f"{8+i}:00",
                        end_time=f"{9+i}:00",
                        is_break=(i == 4)
                    ))
            db.add_all(slots)
            
            # Teachers
            teachers = [
                models.Teacher(name="Dr. Rajesh Kumar", email="rajesh.kumar@college.edu", max_hours_per_week=18),
                models.Teacher(name="Prof. Priya Sharma", email="priya.sharma@college.edu", max_hours_per_week=16),
                models.Teacher(name="Dr. Amit Patel", email="amit.patel@college.edu", max_hours_per_week=15),
                models.Teacher(name="Dr. Sneha Desai", email="sneha.desai@college.edu", max_hours_per_week=14),
                models.Teacher(name="Prof. Vikram Singh", email="vikram.singh@college.edu", max_hours_per_week=16),
            ]
            db.add_all(teachers)
            
            # Rooms
            rooms = [
                models.Room(name="Room 101", capacity=60, type="LectureHall", resources=["Projector", "Whiteboard"]),
                models.Room(name="Room 102", capacity=60, type="LectureHall", resources=["Projector", "Whiteboard"]),
                models.Room(name="Lab 401", capacity=40, type="ComputerLab", resources=["Computers", "Projector"]),
                models.Room(name="Lab 402", capacity=40, type="ComputerLab", resources=["Computers", "Projector"]),
            ]
            db.add_all(rooms)
            
            # Class Groups
            groups = [
                models.ClassGroup(name="SE-AI-DS-A", student_count=60),
                models.ClassGroup(name="SE-AI-DS-B", student_count=55),
                models.ClassGroup(name="TE-AI-DS-A", student_count=50),
            ]
            db.add_all(groups)
            
            # Subjects
            subjects = [
                models.Subject(name="Data Structures", code="CS301", is_lab=False, credits=4, 
                              required_room_type="LectureHall", duration_slots=1, teacher_id=1),
                models.Subject(name="Database Management", code="CS302", is_lab=False, credits=3,
                              required_room_type="LectureHall", duration_slots=1, teacher_id=2),
                models.Subject(name="Database Lab", code="CS302L", is_lab=True, credits=2,
                              required_room_type="ComputerLab", duration_slots=2, teacher_id=2),
                models.Subject(name="Machine Learning", code="CS401", is_lab=False, credits=4,
                              required_room_type="LectureHall", duration_slots=1, teacher_id=3),
                models.Subject(name="Web Development", code="CS303", is_lab=False, credits=3,
                              required_room_type="LectureHall", duration_slots=1, teacher_id=4),
            ]
            db.add_all(subjects)
            
            db.commit()
            print("✅ Database auto-seeded successfully!")
        else:
            print(f"✅ Database already initialized ({teacher_count} teachers)")
    
    except Exception as e:
        print(f"⚠️  Auto-seeding failed: {e}")
        db.rollback()
    finally:
        db.close()

app.include_router(timetables.router, prefix="/api/timetables", tags=["timetables"])
app.include_router(teachers.router, prefix="/api/teachers", tags=["teachers"])
app.include_router(subjects.router, prefix="/api/subjects", tags=["subjects"])
app.include_router(rooms.router, prefix="/api/rooms", tags=["rooms"])
app.include_router(solvers.router, prefix="/api/solvers", tags=["solvers"])
app.include_router(operational.router, prefix="/api/operational", tags=["operational"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(substitutions.router)  # Uses prefix from router definition

@app.get("/")
def read_root():
    return {
        "message": "Welcome to TimeTable Generator API",
        "version": "2.0.0",
        "features": ["Auto-Assignment", "Intelligent Scoring", "Bulk Operations"],
        "docs": "/docs",
        "status": "operational"
    }

@app.get("/health")
def health_check():
    """Health check endpoint for monitoring"""
    db = SessionLocal()
    try:
        # Check database connectivity
        teacher_count = db.query(models.Teacher).count()
        timetable_count = db.query(models.TimetableVersion).count()
        
        return {
            "status": "healthy",
            "database": "connected",
            "teachers": teacher_count,
            "timetables": timetable_count,
            "timestamp": models.func.now()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
    finally:
        db.close()

