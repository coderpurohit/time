#!/usr/bin/env python3

import re

def emergency_fix_now():
    """Emergency fix for the API endpoint issue"""
    
    print("🚨 EMERGENCY FIX: API ENDPOINTS")
    
    # Read the JavaScript file
    with open('academic_resource_management.js', 'r', encoding='utf-8') as f:
        js_content = f.read()
    
    # Fix all API endpoints to use trailing slashes
    fixes = [
        (r'`\$\{API_BASE\}/teachers`', '`${API_BASE}/teachers/`'),
        (r'`\$\{API_BASE\}/subjects`', '`${API_BASE}/subjects/`'),
        (r'`\$\{API_BASE\}/class-groups`', '`${API_BASE}/class-groups/`'),
        (r'`\$\{API_BASE\}/rooms\?type=Lab`', '`${API_BASE}/rooms/?type=Lab`'),
        (r'fetch\(`\$\{API_BASE\}/teachers/\$\{facultyId\}`', 'fetch(`${API_BASE}/teachers/${facultyId}/`'),
        (r'fetch\(`\$\{API_BASE\}/subjects/\$\{subjectId\}`', 'fetch(`${API_BASE}/subjects/${subjectId}/`'),
    ]
    
    for pattern, replacement in fixes:
        js_content = re.sub(pattern, replacement, js_content)
    
    # Write back the fixed JavaScript
    with open('academic_resource_management.js', 'w', encoding='utf-8') as f:
        f.write(js_content)
    
    print("✅ Fixed JavaScript API endpoints")
    
    # Generate timetable for load factor
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
    
    from backend.app.infrastructure.database import SessionLocal
    from backend.app.infrastructure import models
    from backend.app.services.timetable_service import TimetableService
    
    db = SessionLocal()
    try:
        # Check if timetable exists
        latest_version = db.query(models.TimetableVersion).order_by(
            models.TimetableVersion.id.desc()
        ).first()
        
        if not latest_version or len(latest_version.entries) == 0:
            print("🔧 Generating timetable for load factor...")
            service = TimetableService()
            result = service.generate_simple_timetable(db)
            print(f"✅ Generated {result.get('total_entries', 0)} timetable entries")
        else:
            print(f"✅ Timetable exists with {len(latest_version.entries)} entries")
            
    except Exception as e:
        print(f"⚠️ Timetable generation error: {e}")
    finally:
        db.close()
    
    print("\n🎉 EMERGENCY FIX COMPLETE!")
    print("🔄 Refresh the page: http://localhost:8000/dynamic_academic_management.html")
    
    return True

if __name__ == "__main__":
    emergency_fix_now()