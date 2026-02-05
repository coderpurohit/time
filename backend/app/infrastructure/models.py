
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, JSON, DateTime, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class Teacher(Base):
    __tablename__ = "teachers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    max_hours_per_week = Column(Integer, default=12)
    available_slots = Column(JSON, default=list) 
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    subjects = relationship("Subject", back_populates="teacher")

class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    capacity = Column(Integer)
    type = Column(String)  # 'LectureHall', 'Lab'
    resources = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    code = Column(String, unique=True, index=True)
    is_lab = Column(Boolean, default=False)
    credits = Column(Integer)
    required_room_type = Column(String, default="LectureHall")
    duration_slots = Column(Integer, default=1)
    teacher_id = Column(Integer, ForeignKey("teachers.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    teacher = relationship("Teacher", back_populates="subjects")

class ClassGroup(Base):
    __tablename__ = "class_groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    student_count = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class TimeSlot(Base):
    __tablename__ = "time_slots"

    id = Column(Integer, primary_key=True, index=True)
    day = Column(String)
    period = Column(Integer)
    start_time = Column(String)
    end_time = Column(String)
    is_break = Column(Boolean, default=False)

class TimetableVersion(Base):
    __tablename__ = "timetable_versions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String) # e.g. "Spring 2024 V1"
    algorithm = Column(String) # "csp", "genetic", "hybrid"
    status = Column(String, default="draft") # draft, active, archived
    is_valid = Column(Boolean, default=True)
    fitness_score = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    entries = relationship("TimetableEntry", back_populates="version", cascade="all, delete-orphan")

class TimetableEntry(Base):
    __tablename__ = "timetable_entries"

    id = Column(Integer, primary_key=True, index=True)
    version_id = Column(Integer, ForeignKey("timetable_versions.id"))
    time_slot_id = Column(Integer, ForeignKey("time_slots.id"))
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    room_id = Column(Integer, ForeignKey("rooms.id"))
    class_group_id = Column(Integer, ForeignKey("class_groups.id"))
    teacher_id = Column(Integer, ForeignKey("teachers.id"))
    
    version = relationship("TimetableVersion", back_populates="entries")
    time_slot = relationship("TimeSlot")
    subject = relationship("Subject")
    room = relationship("Room")
    class_group = relationship("ClassGroup")
    teacher = relationship("Teacher")

class Holiday(Base):
    __tablename__ = "holidays"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(String, unique=True, index=True)
    name = Column(String)

class Substitution(Base):
    __tablename__ = "substitutions"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(String, index=True)
    timetable_entry_id = Column(Integer, ForeignKey("timetable_entries.id"))
    original_teacher_id = Column(Integer, ForeignKey("teachers.id"))
    substitute_teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=True)
    status = Column(String, default="pending")

    original_teacher = relationship("Teacher", foreign_keys=[original_teacher_id])
    substitute_teacher = relationship("Teacher", foreign_keys=[substitute_teacher_id])

