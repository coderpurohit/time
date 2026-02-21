#!/usr/bin/env python
"""
ADMIN SCHEDULE CONFIGURATION TOOL
=================================

This script helps administrators easily update the schedule configuration.
When you update the schedule, it automatically:
1. Updates the configuration
2. Regenerates time slots based on new configuration
3. Deletes old timetables
4. Generates a new timetable automatically

USAGE:
    python admin_schedule_config.py

EXAMPLES:
    # Interactive mode
    python admin_schedule_config.py
    
    # Apply a preset
    python admin_schedule_config.py preset=7period
    python admin_schedule_config.py preset=6period
    
    # Direct configuration
    python admin_schedule_config.py day_start="09:00" number_of_periods=7 period_duration=60
"""

import requests
import json
import sys
from datetime import datetime

BASE_URL = "http://localhost:8000"

# Presets for common schedules
PRESETS = {
    "7period": {
        "day_start_time": "09:00",
        "number_of_periods": 7,
        "period_duration_minutes": 60,
        "working_minutes_per_day": 420,  # 7 hours
        "lunch_break_start": "12:00",
        "lunch_break_end": "13:00",
        "schedule_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
    },
    "6period": {
        "day_start_time": "09:00",
        "number_of_periods": 6,
        "period_duration_minutes": 60,
        "working_minutes_per_day": 360,  # 6 hours
        "lunch_break_start": "12:00",
        "lunch_break_end": "13:00",
        "schedule_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
    },
    "5period": {
        "day_start_time": "09:00",
        "number_of_periods": 5,
        "period_duration_minutes": 60,
        "working_minutes_per_day": 300,  # 5 hours
        "lunch_break_start": "12:00",
        "lunch_break_end": "13:00",
        "schedule_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
    },
}

def print_header(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")

def get_current_config():
    """Fetch current configuration from server"""
    try:
        response = requests.get(f"{BASE_URL}/api/operational/schedule-config", timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"⚠️  Could not fetch current config (Status {response.status_code})")
            return None
    except Exception as e:
        print(f"❌ Error connecting to server: {e}")
        print("   Make sure the backend is running with: python backend/run_uvicorn.py")
        return None

def display_config(config):
    """Display configuration in readable format"""
    if not config:
        print("No configuration found")
        return
    
    print("Current Configuration:")
    print(f"  • Start time: {config.get('day_start_time', 'N/A')}")
    print(f"  • End time: {config.get('day_end_time', 'N/A')}")
    print(f"  • Number of periods: {config.get('number_of_periods', 'N/A')}")
    print(f"  • Period duration: {config.get('period_duration_minutes', 'N/A')} minutes")
    print(f"  • Working minutes/day: {config.get('working_minutes_per_day', 'N/A')}")
    print(f"  • Lunch break: {config.get('lunch_break_start', 'N/A')} - {config.get('lunch_break_end', 'N/A')}")
    print(f"  • Schedule days: {', '.join(config.get('schedule_days', []))}")
    print(f"  • Updated at: {config.get('updated_at', 'N/A')}")

def interactive_mode():
    """Interactive configuration setup"""
    print_header("INTERACTIVE SCHEDULE CONFIGURATION")
    
    config = {}
    
    # Day start time
    print("1️⃣  TEACHING HOURS")
    config["day_start_time"] = input("   Enter day start time (HH:MM) [default: 09:00]: ").strip() or "09:00"
    config["day_end_time"] = input("   Enter day end time (HH:MM) [default: 17:00]: ").strip() or "17:00"
    
    # Periods
    print("\n2️⃣  PERIOD CONFIGURATION")
    try:
        config["number_of_periods"] = int(input("   Number of periods per day [default: 7]: ") or "7")
        config["period_duration_minutes"] = int(input("   Period duration (minutes) [default: 60]: ") or "60")
    except ValueError:
        print("   ❌ Invalid number. Using defaults.")
        config["number_of_periods"] = 7
        config["period_duration_minutes"] = 60
    
    # Working minutes
    print("\n3️⃣  WORKING TIME")
    try:
        config["working_minutes_per_day"] = int(input("   Working minutes per day [default: auto-calculated]: ") or "0") or None
    except ValueError:
        config["working_minutes_per_day"] = None
    
    # Breaks
    print("\n4️⃣  LUNCH BREAK")
    config["lunch_break_start"] = input("   Lunch break start (HH:MM) [default: 12:00]: ").strip() or "12:00"
    config["lunch_break_end"] = input("   Lunch break end (HH:MM) [default: 13:00]: ").strip() or "13:00"
    
    # Schedule days
    print("\n5️⃣  WORKING DAYS")
    default_days = "Monday, Tuesday, Wednesday, Thursday, Friday"
    days_input = input(f"   Schedule days (comma-separated) [default: {default_days}]: ").strip()
    if days_input:
        config["schedule_days"] = [d.strip() for d in days_input.split(",")]
    else:
        config["schedule_days"] = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    
    return config

def apply_config(config):
    """Apply configuration to the backend"""
    print_header("APPLYING CONFIGURATION")
    
    try:
        print("📤 Sending configuration to server...")
        response = requests.post(
            f"{BASE_URL}/api/operational/schedule-config",
            json=config,
            timeout=120  # Long timeout for timetable generation
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Configuration applied successfully!\n")
            
            print("📋 Configuration Details:")
            print(f"   • ID: {result.get('id')}")
            print(f"   • Start time: {result.get('day_start_time')}")
            print(f"   • Periods: {result.get('number_of_periods')} × {result.get('period_duration_minutes')} min")
            
            if result.get('timetable_regenerated'):
                print(f"\n📅 Timetable Auto-Generated:")
                print(f"   • Version ID: {result.get('timetable_version_id')}")
                print(f"   • Status: {result.get('timetable_status')}")
            else:
                if result.get('warning'):
                    print(f"\n⚠️  {result.get('warning')}")
                else:
                    print(f"\nℹ️  No existing timetable to regenerate")
            
            print(f"\n   Last updated: {result.get('updated_at')}")
            return True
        else:
            print(f"❌ Error (Status {response.status_code}):")
            try:
                error = response.json()
                print(f"   {error.get('detail', 'Unknown error')}")
            except:
                print(f"   {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timeout (timetable generation may still be running)")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def show_presets():
    """Display available presets"""
    print_header("AVAILABLE PRESETS")
    for name, config in PRESETS.items():
        print(f"📌 {name.upper()}")
        print(f"   Periods: {config['number_of_periods']} × {config['period_duration_minutes']} min")
        print(f"   Time: {config['day_start_time']} - (working {config['working_minutes_per_day']} min/day)")
        print()

def main():
    print_header("TIMETABLE SCHEDULE CONFIGURATION MANAGER")
    print("Centralized admin tool for managing schedule configuration")
    print("Any changes here automatically update existing timetables")
    
    # Check server connection
    print("🔍 Checking server connection...")
    current = get_current_config()
    if not current:
        print("\n❌ Cannot connect to backend server!")
        print("   Start the backend with: python backend/run_uvicorn.py")
        return
    
    print("✅ Server is running\n")
    
    # Get configuration source
    config = None
    
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        
        # Preset mode
        if arg.startswith("preset="):
            preset_name = arg.split("=")[1]
            if preset_name in PRESETS:
                config = PRESETS[preset_name]
                print(f"📌 Using preset: {preset_name.upper()}\n")
            else:
                print(f"❌ Unknown preset: {preset_name}")
                show_presets()
                return
        # Parameters mode
        elif "=" in arg:
            print("📝 Using command-line parameters\n")
            # Parse all arguments
            # Example: day_start="09:00" number_of_periods=7 period_duration=60
            # For now, just use preset mode for simplicity
            print("❌ Parameter mode not yet implemented. Use: preset=7period")
            show_presets()
            return
        else:
            print(f"❌ Unknown argument: {arg}")
            show_presets()
            return
    else:
        # Interactive mode
        print("Options:")
        print("  1. Interactive setup")
        print("  2. Use preset (7period, 6period, 5period)")
        print("  3. View presets")
        print("  4. Show current config")
        choice = input("\nSelect option (1-4): ").strip()
        
        if choice == "1":
            config = interactive_mode()
        elif choice == "2":
            show_presets()
            preset = input("Enter preset name: ").strip()
            if preset in PRESETS:
                config = PRESETS[preset]
            else:
                print(f"❌ Unknown preset: {preset}")
                return
        elif choice == "3":
            show_presets()
            return
        elif choice == "4":
            display_config(current)
            return
        else:
            print("❌ Invalid option")
            return
    
    # Display configuration to be applied
    if config:
        print("\n📝 Configuration to be applied:")
        print(f"   • Start time: {config.get('day_start_time')}")
        print(f"   • Periods: {config.get('number_of_periods')} × {config.get('period_duration_minutes')} min")
        print(f"   • Working time: {config.get('working_minutes_per_day')} min/day")
        print(f"   • Lunch: {config.get('lunch_break_start')} - {config.get('lunch_break_end')}")
        print(f"   • Days: {', '.join(config.get('schedule_days', []))}")
        
        response = input("\n✅ Apply this configuration? (yes/no): ").strip().lower()
        if response in ["yes", "y"]:
            if apply_config(config):
                print("\n✨ Done!")
            else:
                print("\n❌ Configuration failed!")
        else:
            print("❌ Cancelled")

if __name__ == "__main__":
    main()
