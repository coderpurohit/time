# FastAPI Entry Point
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from .infrastructure import models
from .infrastructure.database import engine, SessionLocal
from .api.routers import timetables, teachers, subjects, rooms, solvers, operational, analytics, substitutions, imports

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
    "http://localhost:8080",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:5173",
    "null",  # Allow local file access
    "*"  # Allow all for development
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup event - auto-seed if database is empty
# DISABLED TEMPORARILY FOR DEBUGGING
# @app.on_event("startup")
# async def startup_event():
#     """Auto-initialize database with sample data if empty"""
#     db = SessionLocal()
#     try:
#         # Check if database has any data
#         teacher_count = db.query(models.Teacher).count()
#         
#         if teacher_count == 0:
#             print("📊 Database is empty. Auto-seeding with sample data...")
#             # ... rest of startup code ...
#         else:
#             print(f"✅ Database already initialized ({teacher_count} teachers)")
#     
#     except Exception as e:
#         print(f"⚠️  Auto-seeding failed: {e}")
#         db.rollback()
#     finally:
#         db.close()

app.include_router(timetables.router, prefix="/api/timetables", tags=["timetables"])
app.include_router(teachers.router, prefix="/api/teachers", tags=["teachers"])
app.include_router(subjects.router, prefix="/api/subjects", tags=["subjects"])
app.include_router(rooms.router, prefix="/api/rooms", tags=["rooms"])
app.include_router(solvers.router, prefix="/api/solvers", tags=["solvers"])
app.include_router(operational.router, prefix="/api/operational", tags=["operational"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(substitutions.router)  # Uses prefix from router definition
app.include_router(imports.router, prefix="/api/import", tags=["import"])
from .api.routers import lessons
app.include_router(lessons.router, prefix="/api/lessons", tags=["lessons"])

# Import here to avoid circular dependencies if any
from .api.routers import classgroups
app.include_router(classgroups.router, prefix="/api/class-groups", tags=["class-groups"])

@app.get("/health")
def health_check():
    """Health check endpoint for monitoring"""
    db = SessionLocal()
    try:
        # Check database connectivity
        teacher_count = db.query(models.Teacher).count()
        timetable_count = db.query(models.TimetableVersion).count()

        from datetime import datetime
        return {
            "status": "healthy",
            "database": "connected",
            "teachers": teacher_count,
            "timetables": timetable_count,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
    finally:
        db.close()
@app.get("/timetable_page.html")
async def get_timetable_page():
    """Serve timetable_page.html"""
    import pathlib
    root = pathlib.Path(__file__).parent.parent.parent
    filepath = root / "timetable_page.html"
    if filepath.exists():
        return FileResponse(str(filepath), media_type="text/html")
    else:
        raise HTTPException(status_code=404, detail=f"File not found: {filepath}")


@app.get("/")
async def root_index():
    """Serve the default timetable page at root for convenience"""
    import pathlib
    root = pathlib.Path(__file__).parent.parent.parent
    filepath = root / "timetable_page.html"
    if filepath.exists():
        return FileResponse(str(filepath), media_type="text/html")
    # fallback: try frontend/index.html
    filepath2 = root / "frontend" / "index.html"
    if filepath2.exists():
        return FileResponse(str(filepath2), media_type="text/html")
    raise HTTPException(status_code=404, detail="No default page found in project root")

# Mount static files (frontend HTML, CSS, JS) - MUST BE LAST
# Serve the repository root so pages like timetable_page.html and
# associated JS/CSS are available at the root paths the HTML expects.
try:
    backend_dir = os.path.dirname(os.path.dirname(__file__))  # backend/app -> backend/
    static_dir = os.path.dirname(backend_dir)  # TimeTable-Generator/ (project root)
    if os.path.isdir(static_dir):
        app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
    else:
        print(f"Warning: Static directory not found at {static_dir}")
except Exception as e:
    print(f"Warning: Could not mount static files: {e}")
