# Fix Timetable Generation - Complete Guide

## Problem
When you click "Generate New Schedule" button, it shows "Timetable is empty" error.

## Root Cause
The backend server was started BEFORE the lessons were created in the database. The backend loads data at startup, so it doesn't see the new lessons.

## Solution Options

### Option 1: Restart Backend (RECOMMENDED)
This is the proper fix that makes everything work correctly.

**Steps:**
1. Find the terminal window where backend is running
   - Look for text: `Uvicorn running on http://127.0.0.1:8000`
   
2. Stop the backend server:
   - Press `Ctrl+C` in that terminal
   
3. Restart the backend:
   ```cmd
   cd backend
   start.bat
   ```
   
4. Wait 5-10 seconds for server to start

5. Test if it works:
   ```cmd
   python fix_generation_issue.py
   ```

6. If successful, open your browser:
   - Go to: http://localhost:8000/timetable_review_fixed.html
   - Click "Generate New Schedule"
   - It should work now!

### Option 2: Use Workaround Script (QUICK FIX)
If you can't find the backend terminal or don't want to restart, use this:

```cmd
python generate_timetable_directly.py
```

This creates a timetable directly in the database without using the backend solver.

**After running the script:**
1. Open: http://localhost:8000/timetable_review_fixed.html
2. Click "Load Timetable" (NOT "Generate New Schedule")
3. You'll see the timetable

**Note:** The "Generate New Schedule" button will still fail until you restart backend.

## How to Verify Everything Works

Run this diagnostic script:
```cmd
python fix_generation_issue.py
```

It will:
- Check database for lessons
- Check if backend is running
- Check if backend can see the lessons
- Test timetable generation
- Tell you exactly what's wrong and how to fix it

## Teaching Configuration Settings

The timetable page has a "Teaching Configuration" section where you can set:
- Teaching hours per day
- Working days (Mon-Sat)
- Lunch break times
- Periods per day
- Period duration
- Start hour

**To apply these settings:**
1. Open: http://localhost:8000/timetable_review_fixed.html
2. Adjust the settings in "Teaching Configuration" section
3. Click "Apply All Settings"
4. The system will:
   - Save your configuration
   - Regenerate time slots based on your settings
   - Automatically regenerate the timetable
   - Show success message

**Important:** After applying settings, the timetable will be automatically regenerated. Just click "Load Timetable" to see the new schedule.

## Current Database State

Your database has:
- 40 teachers
- 8 subjects
- 13 classes (you wanted 9 - need to clean this up)
- 11 rooms
- 36 time slots
- 54 lessons (properly configured)

## Why "Generate New Schedule" Fails

The CSP solver in `backend/app/solver/csp_solver.py` needs to:
1. Read lessons from database
2. Convert them to required assignments
3. Create variables for each assignment × room × slot
4. Apply constraints (no overlaps, etc.)
5. Solve and return schedule

**The problem:** Backend loaded data at startup BEFORE lessons existed, so it sees 0 lessons.

**The fix:** Restart backend so it reloads data and sees the 54 lessons.

## Files Modified

1. `backend/app/api/routers/operational.py`
   - Added `/api/operational/time-slots/generate` endpoint
   - Fixed `/api/operational/schedule-config` to auto-regenerate timetable

2. `timetable_review_fixed.html`
   - Fixed `applySettings()` function to properly save configuration
   - Added auto-reload after successful generation

3. Created diagnostic scripts:
   - `fix_generation_issue.py` - Diagnoses and guides you through fixing
   - `restart_backend_and_test.py` - Helps with backend restart
   - `generate_timetable_directly.py` - Workaround that bypasses backend

## Next Steps

1. **Immediate:** Run `python fix_generation_issue.py` to see current status

2. **If backend needs restart:** Follow Option 1 above

3. **If you want quick fix:** Use Option 2 (workaround script)

4. **After fixing:** Test the "Apply All Settings" button to verify configuration works

5. **Clean up classes:** You have 13 classes but wanted 9. Run a cleanup script to remove extras.

## Common Issues

### "Cannot connect to backend"
- Backend is not running
- Solution: `cd backend && start.bat`

### "Backend sees 0 lessons"
- Backend needs restart
- Solution: Ctrl+C in backend terminal, then `start.bat`

### "Timetable has 0 entries"
- Solver couldn't find solution
- Possible causes:
  - Not enough time slots
  - Too many lessons
  - Conflicting constraints
- Solution: Use workaround script or adjust lessons/slots

### "Generation takes too long"
- CSP solver has 60 second timeout
- If it times out, use workaround script

## Support

If you're still having issues:
1. Run: `python fix_generation_issue.py`
2. Copy the output
3. Share it so we can diagnose further
