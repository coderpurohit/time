# Integrated Timetable Generator Frontend - User Guide

## 🎯 Quick Start

### 1. Start the Backend Server
```bash
cd c:\Users\bhara\Documents\trae_projects\TimeTable-Generator\backend
.\start.bat
```
Wait for: "Application startup complete"

### 2. Open the Frontend
Open in your browser:
```
c:\Users\bhara\Documents\trae_projects\TimeTable-Generator\frontend\app.html
```

## 📱 Features Overview

### 📅 View Timetable Tab
- Select class group from dropdown
- View weekly schedule grid
- See teacher, room, and subject details
- Lab sessions marked with badges

### 🔧 Manage Resources Tab
**Add and view:**
- **Teachers**: Name, email, max hours (default: 18)
- **Subjects**: Name, code, credits, theory/lab type
- **Rooms**: Name, capacity, type (Lecture Hall/Lab)
- **Class Groups**: Name, student count

### ⚡ Generate Timetable Tab
- Choose algorithm (CSP or Genetic)
- Name your timetable
- Generate and view status
- See recent timetables

## 🔄 Basic Workflow

1. **Setup Resources** (Manage Resources tab)
   - Add 3-5 teachers
   - Add 5+ subjects  
   - Add 3-5 rooms
   - Add 1+ class groups

2. **Generate** (Generate Timetable tab)
   - Select CSP algorithm
   - Enter name: "Test Schedule"
   - Click Generate
   - Wait 5-30 seconds

3. **View** (View Timetable tab)
   - Select class group
   - See your generated schedule

## 🐛 Troubleshooting

**"Backend not running" error:**
- Start backend with `.\start.bat`
- Verify at `http://localhost:8000/docs`

**"No timetable entries":**
- Generate a timetable first
- Ensure resources are added

**Empty dropdown:**
- Add class groups in Manage Resources
- Click Refresh button

## 📚 What's Different from Static HTML?

**app.html** (NEW):
- ✅ Live backend integration
- ✅ Add/edit resources
- ✅ Generate timetables on demand
- ✅ Dynamic updates

**timetable_clean.html** (OLD):
- ❌ Static data only
- ❌ View-only
- ❌ No generation

Enjoy! 🎓
