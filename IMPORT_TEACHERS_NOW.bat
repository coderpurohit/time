@echo off
echo ============================================
echo  IMPORT TEACHERS - DIRECT METHOD
echo ============================================
echo.
echo This will import teachers and clear existing ones
echo.
pause

python import_teachers_csv.py teachers.csv --clear

echo.
echo ============================================
echo  DONE! Check the output above
echo ============================================
pause
