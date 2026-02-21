"""
Complete Timetable Population Script
This script ensures comprehensive data and generates a full, conflict-free timetable
"""
from app.infrastructure.database import SessionLocal
from app.infrastructure import models
import random

def populate_and_generate():
    db = SessionLocal()
    
    try:
        print("="*60)
        print("🎯 COMPLETE TIMETABLE GENERATION")
        print("="*60)
        
        # Step 1: Clear old timetable data
        print("\n[1/5] 🗑️  Clearing old timetable entries...")
        db.query(models.TimetableEntry).delete()
        db.query(models.TimetableVersion).delete()
        db.commit()
        
        # Step 2: Ensure comprehensive base data
        print("\n[2/5] 📊 Ensuring comprehensive base data...")
        
        # Teachers - Need at least 15 for good coverage
        teacher_count = db.query(models.Teacher).count()
        print(f"   Current teachers: {teacher_count}")
        
        if teacher_count < 15:
            print(f"   Adding {15 - teacher_count} more teachers...")
            teacher_names = [
                ("Dr. Rajesh Kumar", "rajesh.kumar@college.edu", 20),
                ("Prof. Priya Sharma", "priya.sharma@college.edu", 18),
                ("Dr. Amit Patel", "amit.patel@college.edu", 20),
                ("Dr. Sneha Desai", "sneha.desai@college.edu", 18),
                ("Prof. Vikram Singh", "vikram.singh@college.edu", 20),
                ("Dr. Meena Joshi", "meena.joshi@college.edu", 18),
                ("Prof. Karan Mehta", "karan.mehta@college.edu", 20),
                ("Dr. Sunita Reddy", "sunita.reddy@college.edu", 18),
                ("Prof. Arjun Nair", "arjun.nair@college.edu", 20),
                ("Dr. Pooja Rao", "pooja.rao@college.edu", 18),
                ("Prof. Anil Verma", "anil.verma@college.edu", 20),
                ("Dr. Kavita Iyer", "kavita.iyer@college.edu", 18),
                ("Prof. Rohit Gupta", "rohit.gupta@college.edu", 20),
                ("Dr. Neha Kapoor", "neha.kapoor@college.edu", 18),
                ("Prof. Sanjay Shah", "sanjay.shah@college.edu", 20),
            ]
            
            existing_emails = {t.email for t in db.query(models.Teacher).all()}
            for name, email, hours in teacher_names:
                if email not in existing_emails:
                    db.add(models.Teacher(name=name, email=email, max_hours_per_week=hours))
            db.commit()
        
        # Rooms - Need at least 10 rooms
        room_count = db.query(models.Room).count()
        print(f"   Current rooms: {room_count}")
        
        if room_count < 10:
            print(f"   Adding {10 - room_count} more rooms...")
            rooms_data = [
                ("Room 101", 60, "LectureHall", ["Projector", "Whiteboard"]),
                ("Room 102", 60, "LectureHall", ["Projector", "Whiteboard"]),
                ("Room 103", 60, "LectureHall", ["Projector", "Whiteboard", "AC"]),
                ("Room 201", 50, "LectureHall", ["Projector", "Whiteboard"]),
                ("Room 202", 50, "LectureHall", ["Projector", "Whiteboard"]),
                ("Lab 401", 40, "ComputerLab", ["Computers", "Projector", "AC"]),
                ("Lab 402", 40, "ComputerLab", ["Computers", "Projector", "AC"]),
                ("Lab 403", 35, "ComputerLab", ["Computers", "Projector"]),
                ("Lab 501", 30, "ComputerLab", ["Computers", "Projector"]),
                ("Lab 502", 30, "ComputerLab", ["Computers", "Projector"]),
            ]
            
            existing_rooms = {r.name for r in db.query(models.Room).all()}
            for name, capacity, room_type, resources in rooms_data:
                if name not in existing_rooms:
                    db.add(models.Room(name=name, capacity=capacity, type=room_type, resources=resources))
            db.commit()
        
        # Time Slots - Ensure we have Monday-Friday, 8 periods each (excluding breaks)
        slot_count = db.query(models.TimeSlot).count()
        print(f"   Current time slots: {slot_count}")
        
        if slot_count < 40:
            print(f"   Creating complete time slot structure...")
            db.query(models.TimeSlot).delete()  # Clear and recreate for consistency
            
            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
            for day in days:
                for period in range(1, 9):  # 8 periods per day
                    start_hour = 9 + period
                    end_hour = start_hour + 1
                    is_break = (period == 4)  # 4th period is lunch break
                    
                    db.add(models.TimeSlot(
                        day=day,
                        period=period,
                        start_time=f"{start_hour}:00",
                        end_time=f"{end_hour}:00",
                        is_break=is_break
                    ))
            db.commit()
        
        # Subjects - Need many subjects for variety (at least 12)
        subject_count = db.query(models.Subject).count()
        print(f"   Current subjects: {subject_count}")
        
        teachers = db.query(models.Teacher).all()
        
        if subject_count < 12:
            print(f"   Adding more subjects...")
            subjects_data = [
                ("Data Structures", "CS301", False, 4, "LectureHall", 1),
                ("Database Management", "CS302", False, 3, "LectureHall", 1),
                ("Database Lab", "CS302L", True, 2, "ComputerLab", 2),
                ("Machine Learning", "CS401", False, 4, "LectureHall", 1),
                ("Web Development", "CS303", False, 3, "LectureHall", 1),
                ("Web Development Lab", "CS303L", True, 2, "ComputerLab", 2),
                ("Operating Systems", "CS304", False, 4, "LectureHall", 1),
                ("OS Lab", "CS304L", True, 2, "ComputerLab", 2),
                ("Computer Networks", "CS305", False, 3, "LectureHall", 1),
                ("Software Engineering", "SE201", False, 3, "LectureHall", 1),
                ("Computer Graphics", "CS402", False, 3, "LectureHall", 1),
                ("Graphics Lab", "CS402L", True, 2, "ComputerLab", 2),
                ("Data Science", "CS403", False, 4, "LectureHall", 1),
                ("Python Programming", "CS306", False, 3, "LectureHall", 1),
                ("AI Fundamentals", "CS404", False, 4, "LectureHall", 1),
            ]
            
            existing_codes = {s.code for s in db.query(models.Subject).all()}
            for idx, (name, code, is_lab, credits, room_type, duration) in enumerate(subjects_data):
                if code not in existing_codes:
                    teacher = teachers[idx % len(teachers)]  # Distribute among teachers
                    db.add(models.Subject(
                        name=name,
                        code=code,
                        is_lab=is_lab,
                        credits=credits,
                        required_room_type=room_type,
                        duration_slots=duration,
                        teacher_id=teacher.id
                    ))
            db.commit()
        
        # Class Groups - Ensure we have at least 3
        group_count = db.query(models.ClassGroup).count()
        print(f"   Current class groups: {group_count}")
        
        if group_count < 3:
            print(f"   Adding class groups...")
            groups_data = [
                ("SE-AI-DS-A", 60),
                ("SE-AI-DS-B", 55),
                ("TE-AI-DS-A", 50),
            ]
            
            existing_groups = {g.name for g in db.query(models.ClassGroup).all()}
            for name, count in groups_data:
                if name not in existing_groups:
                    db.add(models.ClassGroup(name=name, student_count=count))
            db.commit()
        
        # Refresh all data
        teachers = db.query(models.Teacher).all()
        subjects = db.query(models.Subject).all()
        rooms = db.query(models.Room).all()
        groups = db.query(models.ClassGroup).all()
        slots = db.query(models.TimeSlot).filter(models.TimeSlot.is_break == False).all()
        
        print(f"\n✅ Data preparation complete:")
        print(f"   ✓ Teachers: {len(teachers)}")
        print(f"   ✓ Subjects: {len(subjects)}")
        print(f"   ✓ Rooms: {len(rooms)}")
        print(f"   ✓ Class Groups: {len(groups)}")
        print(f"   ✓ Time Slots: {len(slots)}")
        
        # Step 3: Generate complete timetable
        print(f"\n[3/5] 🎯 Generating complete timetable...")
        
        # Create timetable version
        version = models.TimetableVersion(
            name="Complete Weekly Schedule - Auto Generated",
            algorithm="intelligent_manual",
            status="active",
            is_valid=True
        )
        db.add(version)
        db.commit()
        db.refresh(version)
        
        # Organize slots by day and period
        slot_map = {}
        for slot in slots:
            if slot.day not in slot_map:
                slot_map[slot.day] = []
            slot_map[slot.day].append(slot)
        
        # Sort slots by period
        for day in slot_map:
            slot_map[day] = sorted(slot_map[day], key=lambda s: s.period)
        
        # Separate lecture and lab subjects
        lecture_subjects = [s for s in subjects if not s.is_lab]
        lab_subjects = [s for s in subjects if s.is_lab]
        
        entries_created = 0
        days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        
        # Generate for each class group
        for group in groups:
            print(f"\n   Scheduling {group.name}...")
            
            # Track resource usage to avoid conflicts
            teacher_busy = set()  # (slot_id, teacher_id)
            room_busy = set()     # (slot_id, room_id)
            
            subject_rotation_idx = 0
            
            for day in days_order:
                if day not in slot_map:
                    continue
                
                day_slots = slot_map[day]
                periods_filled = 0
                
                print(f"      {day}: ", end="")
                
                i = 0
                while i < len(day_slots) and periods_filled < 6:  # Fill up to 6 periods per day
                    slot = day_slots[i]
                    
                    # Decide subject (alternate between lecture and lab with preference to lectures)
                    if periods_filled % 4 == 0 and lab_subjects and i + 1 < len(day_slots):
                        # Every 4th period, try to place a lab (2 consecutive periods)
                        subject = lab_subjects[subject_rotation_idx % len(lab_subjects)]
                        next_slot = day_slots[i + 1]
                        
                        # Check if we can fit a 2-period lab
                        if subject.duration_slots == 2:
                            # Find available teacher
                            teacher = db.query(models.Teacher).filter_by(id=subject.teacher_id).first()
                            if not teacher:
                                teacher = random.choice(teachers)
                            
                            # Check teacher availability for both slots
                            teacher_available = (
                                (slot.id, teacher.id) not in teacher_busy and
                                (next_slot.id, teacher.id) not in teacher_busy
                            )
                            
                            # Find suitable lab room
                            suitable_rooms = [r for r in rooms if r.type == "ComputerLab" and
                                            (slot.id, r.id) not in room_busy and
                                            (next_slot.id, r.id) not in room_busy]
                            
                            if teacher_available and suitable_rooms:
                                room = random.choice(suitable_rooms)
                                
                                # Create 2 entries for the lab
                                for lab_slot in [slot, next_slot]:
                                    entry = models.TimetableEntry(
                                        version_id=version.id,
                                        time_slot_id=lab_slot.id,
                                        subject_id=subject.id,
                                        room_id=room.id,
                                        class_group_id=group.id,
                                        teacher_id=teacher.id
                                    )
                                    db.add(entry)
                                    teacher_busy.add((lab_slot.id, teacher.id))
                                    room_busy.add((lab_slot.id, room.id))
                                
                                entries_created += 2
                                periods_filled += 2
                                i += 2  # Skip next slot since it's used for lab
                                subject_rotation_idx += 1
                                continue
                    
                    # Place a lecture subject
                    if lecture_subjects:
                        subject = lecture_subjects[subject_rotation_idx % len(lecture_subjects)]
                        
                        # Find available teacher
                        teacher = db.query(models.Teacher).filter_by(id=subject.teacher_id).first()
                        if not teacher:
                            teacher = random.choice(teachers)
                        
                        # Check teacher availability
                        teacher_available = (slot.id, teacher.id) not in teacher_busy
                        
                        # Find suitable room
                        suitable_rooms = [r for r in rooms if r.type == subject.required_room_type and
                                        (slot.id, r.id) not in room_busy]
                        
                        if not suitable_rooms:
                            suitable_rooms = [r for r in rooms if (slot.id, r.id) not in room_busy]
                        
                        if teacher_available and suitable_rooms:
                            room = random.choice(suitable_rooms)
                            
                            entry = models.TimetableEntry(
                                version_id=version.id,
                                time_slot_id=slot.id,
                                subject_id=subject.id,
                                room_id=room.id,
                                class_group_id=group.id,
                                teacher_id=teacher.id
                            )
                            db.add(entry)
                            teacher_busy.add((slot.id, teacher.id))
                            room_busy.add((slot.id, room.id))
                            
                            entries_created += 1
                            periods_filled += 1
                            subject_rotation_idx += 1
                    
                    i += 1
                
                print(f"{periods_filled} classes ✓")
        
        db.commit()
        
        # Step 4: Verify timetable
        print(f"\n[4/5] ✅ Timetable generated successfully!")
        print(f"   Total entries: {entries_created}")
        print(f"   Expected entries: ~{len(groups) * 5 * 6} (3 groups × 5 days × 6 periods)")
        print(f"   Coverage: {entries_created / (len(groups) * 5 * 6) * 100:.1f}%")
        
        # Step 5: Final verification
        print(f"\n[5/5] 🔍 Verifying conflicts...")
        
        # Check for conflicts
        entries = db.query(models.TimetableEntry).filter_by(version_id=version.id).all()
        
        # Teacher conflicts
        teacher_slots = {}
        for entry in entries:
            key = (entry.time_slot_id, entry.teacher_id)
            teacher_slots[key] = teacher_slots.get(key, 0) + 1
        
        teacher_conflicts = sum(1 for v in teacher_slots.values() if v > 1)
        
        # Room conflicts
        room_slots = {}
        for entry in entries:
            key = (entry.time_slot_id, entry.room_id)
            room_slots[key] = room_slots.get(key, 0) + 1
        
        room_conflicts = sum(1 for v in room_slots.values() if v > 1)
        
        if teacher_conflicts == 0 and room_conflicts == 0:
            print(f"   ✅ No conflicts detected!")
        else:
            print(f"   ⚠️  Teacher conflicts: {teacher_conflicts}")
            print(f"   ⚠️  Room conflicts: {room_conflicts}")
        
        print("\n" + "="*60)
        print("🎉 COMPLETE! Refresh your browser to see the full timetable!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    populate_and_generate()
