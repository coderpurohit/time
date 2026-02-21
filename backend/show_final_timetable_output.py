"""
Show the complete final timetable output with all details and schedule times.
This reveals exactly what the admin and students will see.
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def format_timetable_as_table():
    """Fetch timetable and display in readable format"""
    
    # Get latest timetable
    resp = requests.get(f"{BASE_URL}/api/timetables/latest", timeout=10)
    if resp.status_code != 200:
        print(f"❌ Failed to fetch timetable: {resp.status_code}")
        return
    
    tt = resp.json()
    entries = tt.get('entries', [])
    
    print("\n" + "="*120)
    print("FINAL TIMETABLE OUTPUT - What Admin and Students See")
    print("="*120)
    
    print(f"\nTimetable ID: {tt.get('id')}")
    print(f"Status: {tt.get('status')}")
    print(f"Total Entries: {len(entries)}")
    print(f"Generated: {tt.get('created_at')}")
    
    # Group by day and time
    by_day_time = {}
    for entry in entries:
        day = entry['time_slot']['day']
        start = entry['time_slot']['start_time']
        key = (day, start)
        
        if key not in by_day_time:
            by_day_time[key] = []
        by_day_time[key].append(entry)
    
    # Print by day
    days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    for day in days_order:
        print(f"\n{'='*120}")
        print(f"  {day.upper()}")
        print(f"{'='*120}")
        print(f"{'Time':<12} {'Class':<18} {'Subject':<35} {'Teacher':<20} {'Room':<12}")
        print(f"{'-'*120}")
        
        day_entries = sorted(
            [e for e in entries if e['time_slot']['day'] == day],
            key=lambda x: x['time_slot']['start_time']
        )
        
        for entry in day_entries:
            ts = entry['time_slot']
            if ts['is_break']:
                print(f"{ts['start_time']:<12} {'[LUNCH BREAK]':<18} {ts['end_time']:<35} {'-':<20} {'-':<12}")
            else:
                time_slot = f"{ts['start_time']}-{ts['end_time']}"
                class_name = entry['class_group']['name'][:17]
                subject = entry['subject']['name'][:34]
                teacher = entry['teacher']['name'][:19]
                room = entry['room']['name'][:11]
                
                print(f"{time_slot:<12} {class_name:<18} {subject:<35} {teacher:<20} {room:<12}")
    
    # Summary statistics
    print(f"\n{'='*120}")
    print("SCHEDULE SUMMARY")
    print(f"{'='*120}")
    
    # Get config
    resp_cfg = requests.get(f"{BASE_URL}/api/operational/schedule-config", timeout=10)
    cfg = resp_cfg.json()
    
    print(f"\nApplied Configuration:")
    print(f"  Teaching Hours: {cfg.get('day_start_time')} - {cfg.get('day_end_time', 'Auto-calculated')}")
    print(f"  Periods Per Day: {cfg.get('number_of_periods')}")
    print(f"  Period Duration: {cfg.get('period_duration_minutes')} minutes")
    print(f"  Lunch Break: {cfg.get('lunch_break_start')} - {cfg.get('lunch_break_end')}")
    print(f"  Working Days: {', '.join(cfg.get('schedule_days', []))}")
    
    # Class stats
    classes = {}
    for entry in entries:
        class_id = entry['class_group']['id']
        class_name = entry['class_group']['name']
        if class_id not in classes:
            classes[class_id] = {"name": class_name, "slots": 0}
        classes[class_id]["slots"] += 1
    
    print(f"\nClass Loading:")
    for class_id, info in sorted(classes.items(), key=lambda x: x[1]['name']):
        print(f"  {info['name']:<20} : {info['slots']} slots assigned")
    
    # Teacher stats
    teachers = {}
    for entry in entries:
        teacher_id = entry['teacher']['id']
        teacher_name = entry['teacher']['name']
        if teacher_id not in teachers:
            teachers[teacher_id] = {"name": teacher_name, "slots": 0}
        teachers[teacher_id]["slots"] += 1
    
    print(f"\nTeacher Loading:")
    for teacher_id, info in sorted(teachers.items(), key=lambda x: x[1]['name'])[:10]:
        print(f"  {info['name']:<20} : {info['slots']} slots assigned")
    
    # Room stats
    rooms = {}
    for entry in entries:
        room_id = entry['room']['id']
        room_name = entry['room']['name']
        if room_id not in rooms:
            rooms[room_id] = {"name": room_name, "slots": 0}
        rooms[room_id]["slots"] += 1
    
    print(f"\nRoom Utilization:")
    for room_id, info in sorted(rooms.items(), key=lambda x: x[1]['slots'], reverse=True)[:10]:
        print(f"  {info['name']:<20} : {info['slots']} slots used")
    
    print(f"\n{'='*120}\n")

def show_raw_json():
    """Show raw JSON of first few entries"""
    resp = requests.get(f"{BASE_URL}/api/timetables/latest", timeout=10)
    if resp.status_code != 200:
        print(f"❌ Failed: {resp.status_code}")
        return
    
    tt = resp.json()
    entries = tt.get('entries', [])
    
    print("\n" + "="*120)
    print("FIRST 3 ENTRIES (RAW JSON)")
    print("="*120 + "\n")
    
    for i, entry in enumerate(entries[:3]):
        print(f"Entry {i+1}:")
        print(json.dumps(entry, indent=2))
        print()

if __name__ == '__main__':
    print("\n🔍 FETCHING FINAL TIMETABLE OUTPUT...\n")
    format_timetable_as_table()
    show_raw_json()
