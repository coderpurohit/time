@echo off
cd /d C:\Users\bhara\Documents\trae_projects\TimeTable-Generator\backend
C:\Users\bhara\Documents\trae_projects\TimeTable-Generator\venv\Scripts\python.exe -m uvicorn app.main:app --port 8000 --host 127.0.0.1
