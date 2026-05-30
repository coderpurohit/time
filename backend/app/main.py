# FastAPI Entry Point
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from sqlalchemy import text
from .infrastructure import models
from .infrastructure.database import engine, SessionLocal
from .api.routers import timetables, teachers, subjects, rooms, solvers, operational, analytics, substitutions, imports, schedule_config

# Auto-create tables on startup
models.Base.metadata.create_all(bind=engine)


def ensure_runtime_schema():
    """Apply lightweight additive schema fixes for existing SQLite DBs."""
    try:
        with engine.begin() as conn:
            cols = conn.execute(text("PRAGMA table_info(timetable_entries)")).fetchall()
            col_names = {row[1] for row in cols}
            if "batch_label" not in col_names:
                conn.execute(text("ALTER TABLE timetable_entries ADD COLUMN batch_label VARCHAR"))
                print("Schema update: added timetable_entries.batch_label")
    except Exception as e:
        print(f"WARNING: Runtime schema update failed: {e}")


ensure_runtime_schema()

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
#             print("Database is empty. Auto-seeding with sample data...")
#             # ... rest of startup code ...
#         else:
#             print(f"Database already initialized ({teacher_count} teachers)")
#     
#     except Exception as e:
#         print(f"WARNING: Auto-seeding failed: {e}")
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
app.include_router(schedule_config.router)  # Uses prefix from router definition
from .api.routers import imports_fixed, imports_enhanced
app.include_router(imports_fixed.router, prefix="/api/import", tags=["import"])
app.include_router(imports_enhanced.router, prefix="/api/import", tags=["import-enhanced"])
from .api.routers import lessons
app.include_router(lessons.router, prefix="/api/lessons", tags=["lessons"])

# Import here to avoid circular dependencies if any
from .api.routers import classgroups, debug_router
app.include_router(classgroups.router, prefix="/api/class-groups", tags=["class-groups"])
app.include_router(debug_router.router, prefix="/api/debug", tags=["debug"])

# Serve static files (CSS, JS, etc.) from root directory
import os
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
app.mount("/static", StaticFiles(directory=root_dir), name="static")

@app.get("/dashboard_styles.css")
async def get_dashboard_styles():
    """Serve dashboard styles"""
    import os
    file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "dashboard_styles.css")
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="text/css")
    raise HTTPException(status_code=404, detail="dashboard_styles.css not found")

@app.get("/timetable_page_styles.css")
async def get_timetable_styles():
    """Serve timetable page styles"""
    import os
    file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "timetable_page_styles.css")
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="text/css")
    raise HTTPException(status_code=404, detail="timetable_page_styles.css not found")

@app.get("/dashboard_script.js")
async def get_dashboard_script():
    """Serve dashboard script"""
    import os
    file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "dashboard_script.js")
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="application/javascript")
    raise HTTPException(status_code=404, detail="dashboard_script.js not found")

@app.get("/timetable_page_script.js")
async def get_timetable_script():
    """Serve timetable page script"""
    import os
    file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "timetable_page_script.js")
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="application/javascript")
    raise HTTPException(status_code=404, detail="timetable_page_script.js not found")

@app.get("/subjects_management.js")
async def get_subjects_management():
    """Serve subjects management script"""
    import os
    file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "subjects_management.js")
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="application/javascript")
    raise HTTPException(status_code=404, detail="subjects_management.js not found")

@app.get("/classes_management.js")
async def get_classes_management():
    """Serve classes management script"""
    import os
    file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "classes_management.js")
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="application/javascript")
    raise HTTPException(status_code=404, detail="classes_management.js not found")

@app.get("/rooms_management.js")
async def get_rooms_management():
    """Serve rooms management script"""
    import os
    file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "rooms_management.js")
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="application/javascript")
    raise HTTPException(status_code=404, detail="rooms_management.js not found")

@app.get("/teacher_bulk_import.js")
async def get_teacher_bulk_import():
    """Serve teacher bulk import script"""
    import os
    file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "teacher_bulk_import.js")
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="application/javascript")
    raise HTTPException(status_code=404, detail="teacher_bulk_import.js not found")

@app.get("/frontend/lessons_styles.css")
async def get_frontend_lessons_styles():
    """Serve frontend lessons styles"""
    import os
    file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend", "lessons_styles.css")
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="text/css")
    raise HTTPException(status_code=404, detail="lessons_styles.css not found")

@app.get("/frontend/lessons_script.js")
async def get_frontend_lessons_script():
    """Serve frontend lessons script"""
    import os
    file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend", "lessons_script.js")
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="application/javascript")
    raise HTTPException(status_code=404, detail="lessons_script.js not found")
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
@app.get("/master_timetable.html")
async def get_master_timetable():
    """Serve the master timetable page"""
    import os
    file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "master_timetable.html")
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="text/html")
    else:
        raise HTTPException(status_code=404, detail="master_timetable.html not found")

@app.get("/timetable_config.html")
async def get_timetable_config():
    """Serve the timetable configuration page"""
    import os
    file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "timetable_config.html")
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="text/html")
    else:
        raise HTTPException(status_code=404, detail="timetable_config.html not found")

@app.get("/teacher_config.html")
async def get_teacher_config():
    """Serve the teacher configuration page"""
    import os
    file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "teacher_config.html")
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="text/html")
    else:
        raise HTTPException(status_code=404, detail="teacher_config.html not found")

@app.get("/timetable_page.html")
async def get_timetable_page():
    """Serve the timetable page HTML file"""
    import os
    file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "timetable_page.html")
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="text/html")
    else:
        raise HTTPException(status_code=404, detail="timetable_page.html not found")

@app.get("/calendar_page.html")
async def get_calendar_page():
    """Serve the calendar page HTML file."""
    import os
    file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "calendar_page.html")
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="text/html")
    else:
        raise HTTPException(status_code=404, detail="calendar_page.html not found")

@app.get("/dashboard.html")
async def get_dashboard_page():
    """
    Backward-compatible dashboard route.
    If a standalone dashboard page exists, serve it.
    Otherwise fall back to timetable page so sidebar links keep working.
    """
    import os
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    dashboard_path = os.path.join(root_dir, "dashboard.html")
    index_path = os.path.join(root_dir, "index.html")
    fallback_path = os.path.join(root_dir, "timetable_page.html")

    if os.path.exists(dashboard_path):
        return FileResponse(dashboard_path, media_type="text/html")
    if os.path.exists(index_path):
        return FileResponse(index_path, media_type="text/html")
    if os.path.exists(fallback_path):
        return FileResponse(fallback_path, media_type="text/html")
    raise HTTPException(status_code=404, detail="dashboard.html, index.html, and fallback timetable_page.html not found")

@app.get("/dashboard")
async def get_dashboard_page_alias():
    """Alias route so links using /dashboard also work."""
    return await get_dashboard_page()

@app.get("/index.html")
async def get_index_page():
    """Serve dashboard index page used by sidebar Dashboard link."""
    import os
    file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "index.html")
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="text/html")
    # Keep compatibility if index is missing
    return await get_dashboard_page()

@app.get("/")
async def root_index():
    """Serve the timetable page HTML file"""
    import os
    file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "timetable_page.html")
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="text/html")
    else:
        raise HTTPException(status_code=404, detail="timetable_page.html not found")
