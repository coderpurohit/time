# 🎯 Admin Onboarding Checklist

## ✅ Pre-Setup Verification

### System Requirements
- [ ] Python 3.10+ installed
- [ ] Virtual environment active  
- [ ] Backend dependencies installed (`pip install -r requirements.txt`)
- [ ] Port 8000 available (not in use)
- [ ] SQLite available (usually built-in)

### Knowledge Prerequisites
- [ ] Familiar with command line/terminal
- [ ] Know basic schedule structure (periods, start/end times)
- [ ] Understand institution's teaching hours

---

## 🚀 Initial Setup (One-Time)

### Step 1: Navigate and Start Backend
```bash
cd backend
python run_uvicorn.py
```
- [ ] Server starts without errors
- [ ] Message shows: "Uvicorn running on http://127.0.0.1:8000"

### Step 2: In Another Terminal - Seed Demo Data
```bash
cd backend
python seed_demo_data.py
```
- [ ] Script completes successfully
- [ ] Shows: "✅ Demo data seeded successfully!"

### Step 3: Verify System Health
```bash
curl http://localhost:8000/health
```
- [ ] Response shows status: "healthy"
- [ ] Database: "connected"
- [ ] Teachers: >= 10
- [ ] Timetables: >= 1

---

## 📋 First Configuration (Initial Setup)

### Option A: Use Preset (Recommended for First Time)
```bash
cd backend
python admin_schedule_config.py preset=7period
```
- [ ] Confirms configuration to apply
- [ ] Shows periods: 7 × 60 min
- [ ] Responds: "✅ Configuration applied successfully!"
- [ ] Message: "✅ Timetable auto-regenerated"

### Option B: Interactive Setup (Custom Configuration)
```bash
cd backend
python admin_schedule_config.py
```
- [ ] Select option 1: "Interactive setup"
- [ ] Answer all prompts (or press Enter for defaults)
- [ ] Review configuration
- [ ] Confirm application
- [ ] See success message

---

## 🧪 Verify Everything Works

### Run Complete Test Suite
```bash
cd backend
python test_schedule_regeneration.py
```

Expected results:
- [ ] "Step 1: ✅ Server is healthy"
- [ ] "Step 2: ✅ Current config found"
- [ ] "Step 3: Time slots populated"
- [ ] "Step 4: ✅ Configuration applied"
- [ ] "Step 5: ✅ Time slots Regenerated!"
- [ ] "Step 5: ✅ Timetable entries regenerated"
- [ ] "Step 5: ✅ Timetable completeness - Group data shows all subjects"
- [ ] "✅ ALL TESTS PASSED!"

---

## 📖 Documentation Review

### Essential Reading (Required - 10 minutes)
- [ ] Skim [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
- [ ] Know the 3 main commands:
  - [ ] `python run_uvicorn.py` - Start server
  - [ ] `python admin_schedule_config.py` - Configure schedule
  - [ ] `python test_schedule_regeneration.py` - Test system

### Recommended Reading (Soon - 20 minutes)
- [ ] Full [SCHEDULE_CONFIG_GUIDE.md](SCHEDULE_CONFIG_GUIDE.md)
- [ ] Review "Common Scenarios" section
- [ ] Review "Troubleshooting" section

### Reference Documents (As Needed)
- [ ] [CSP_SOLVER_FIX.md](CSP_SOLVER_FIX.md) - Technical details
- [ ] [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - System overview

---

## 💾 Daily Operations

### Morning: Start System
```bash
cd backend
python run_uvicorn.py
```
- [ ] Keep this terminal open
- [ ] Note the URL: http://127.0.0.1:8000

### Check Timetable Status
```bash
curl http://localhost:8000/api/timetables/latest
# Or visit: http://localhost:8000/docs
```
- [ ] Verify current timetable exists
- [ ] Check status is "active" or "valid"

### Make Schedule Changes (When Needed)
```bash
python admin_schedule_config.py
```
- [ ] Choose option
- [ ] Apply changes
- [ ] Verify success message indicates timetable regenerated

### Evening: Optional Backup
- [ ] Consider backing up `app.db` if important data exists
- [ ] Keep notes of current configuration

---

## 🎮 Common Tasks Checklist

### Task: Change to 7-Period Schedule
```bash
python admin_schedule_config.py preset=7period
```
- [ ] Run command
- [ ] Verify success
- [ ] Check timetable regenerated

### Task: Change to Custom Schedule  
```bash
python admin_schedule_config.py
# Select: 1. Interactive setup
```
- [ ] Answer all prompts
- [ ] Review before applying
- [ ] Confirm application
- [ ] Verify regeneration

### Task: View Current Configuration
```bash
python admin_schedule_config.py
# Select: 4. Show current config
```
- [ ] See current schedule
- [ ] Note last update time

### Task: Run System Test
```bash
python test_schedule_regeneration.py
```
- [ ] All tests pass
- [ ] No error messages
- [ ] Configuration stable

---

## 🆘 Troubleshooting Decisions

### Are you seeing an error?

#### Error: "Cannot connect to server"
- [ ] Is `python run_uvicorn.py` running?
- [ ] Try: Restart server

#### Error: "No timetable found"
- [ ] Did you run `python seed_demo_data.py`?
- [ ] Try: Run seed_demo_data.py again

#### Error: "Database connection failed"
- [ ] Try: `python reset_db.py` then `python seed_demo_data.py`

#### Error: "Configuration failed to apply"
- [ ] Check times are in HH:MM format
- [ ] Check periods × duration fit in working day
- [ ] Try: Run test_schedule_regeneration.py to diagnose

#### Not sure?
- [ ] See [SCHEDULE_CONFIG_GUIDE.md](SCHEDULE_CONFIG_GUIDE.md) Troubleshooting section
- [ ] Run: `python test_schedule_regeneration.py`
- [ ] Check logs in terminal where server runs

---

## 🎓 Training Checkpoints

### Checkpoint 1: Basic Operation (15 minutes)
- [ ] Can start server
- [ ] Can run admin tool
- [ ] Can apply preset configuration
- [ ] System generates timetable automatically

**Status: Ready for basic schedule changes**

### Checkpoint 2: Intermediate (30 minutes)
- [ ] Understand all configuration parameters
- [ ] Can do interactive setup
- [ ] Can verify timetable completeness
- [ ] Know what to do when changes don't take effect

**Status: Ready for custom configurations**

### Checkpoint 3: Advanced (Optional - 1 hour)
- [ ] Understand CSP solver basics
- [ ] Can diagnose system issues
- [ ] Can reset and re-seed database if needed
- [ ] Can use API endpoints directly

**Status: Ready for advanced troubleshooting**

---

## 📊 Quick Access

### Important Commands
```
Server:      cd backend && python run_uvicorn.py
Config:      cd backend && python admin_schedule_config.py
Tests:       cd backend && python test_schedule_regeneration.py
Reset DB:    cd backend && python reset_db.py
Seed Demo:   cd backend && python seed_demo_data.py
```

### Important URLs
- API Interactive: `http://localhost:8000/docs`
- API Reference: `http://localhost:8000/redoc`
- Health Check: `http://localhost:8000/health`

### Important Files
- `schedule_config.json` - Current schedule (if saved)
- `app.db` - SQLite database
- `admin_schedule_config.py` - Admin tool
- `QUICK_REFERENCE.md` - Quick guide

---

## ✨ Success Indicators

### How to Know System is Working Well
- [ ] Server starts without errors
- [ ] Admin tool runs and responds to inputs
- [ ] Configuration changes are applied successfully
- [ ] Timetable auto-regenerates after config changes
- [ ] Test suite shows: "✅ ALL TESTS PASSED!"
- [ ] No error messages in terminal or output

### How to Know Configuration is Complete
- [ ] Current schedule matches institutional requirements
- [ ] All teaching hours covered
- [ ] Lunch breaks configured
- [ ] Working days set correctly
- [ ] Timetable shows all classes for all groups

---

## 📝 Sign-Off

### I have completed the setup:
- Date: _______________
- Time: _______________
- System Status: _______________
- Notes: _______________________________________________

### Admin Name (Print): _______________

### Admin Signature: _______________

---

## 🎉 Ready to Use!

Once this checklist is complete, you:
- ✅ Can manage schedule configuration
- ✅ Can apply changes without manual intervention
- ✅ Know how to verify system health
- ✅ Know how to troubleshoot common issues
- ✅ Can run the system independently

**Congratulations! You're ready to manage the timetable system!** 🚀

---

## 📞 Quick Support

### For Questions About...

**Schedule Configuration**
→ See: [QUICK_REFERENCE.md](QUICK_REFERENCE.md)

**Common Scenarios**
→ See: [SCHEDULE_CONFIG_GUIDE.md](SCHEDULE_CONFIG_GUIDE.md)

**Technical Details**
→ See: [CSP_SOLVER_FIX.md](CSP_SOLVER_FIX.md)

**System Overview**
→ See: [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)

**Errors/Issues**
→ See: [SCHEDULE_CONFIG_GUIDE.md](SCHEDULE_CONFIG_GUIDE.md#troubleshooting)

---

**Setup Complete! 🎉**
