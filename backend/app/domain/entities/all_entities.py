
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Teacher:
    id: int
    name: str
    email: str
    max_hours_per_week: int = 12
    available_slots: List[int] = field(default_factory=list)

@dataclass
class Room:
    id: int
    name: str
    capacity: int
    type: str = "LectureHall"
    resources: List[str] = field(default_factory=list)

@dataclass
class Subject:
    id: int
    name: str
    code: str
    is_lab: bool = False
    credits: int = 4
    required_room_type: str = "LectureHall"
    duration_slots: int = 1
    teacher_id: Optional[int] = None

@dataclass
class ClassGroup:
    id: int
    name: str
    student_count: int

@dataclass
class TimeSlot:
    id: int
    day: str
    period: int
    start_time: str
    end_time: str
    is_break: bool = False
