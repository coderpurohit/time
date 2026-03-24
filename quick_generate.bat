@echo off
echo ============================================
echo QUICK TIMETABLE GENERATOR
echo ============================================
echo.
echo Generating new timetable...
python generate_timetable_directly.py
echo.
echo ============================================
echo DONE!
echo ============================================
echo.
echo Now open your browser and:
echo 1. Go to: http://localhost:8000/timetable_review_fixed.html
echo 2. Click "Load Timetable"
echo.
pause
