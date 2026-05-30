
import io
import docx
import re
from app.infrastructure.database import SessionLocal
from app.infrastructure import models
from app.api.routers.analytics import upload_workload_docx
import asyncio
from fastapi import UploadFile

async def repair():
    db = SessionLocal()
    try:
        with open("last_uploaded_debug.docx", "rb") as f:
            content = f.read()
        
        # We can't easily call the route directly because of Depends, 
        # but we can call the logic or just re-run the same file.
        # Let's just create a dummy UploadFile and call it.
        file = UploadFile(filename="repair.docx", file=io.BytesIO(content))
        result = await upload_workload_docx(version_id=0, file=file, db=db)
        print("Repair Result:", result["message"])
        print(f"Teachers: {result.get('teachers_parsed')}")
    except Exception as e:
        print("Repair Failed:", str(e))
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(repair())
