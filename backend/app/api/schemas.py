
from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Any
from datetime import datetime

# --- Shared Bases ---

class TeacherBase(BaseModel):
    name: str
    email: str
    max_hours_per_week: int = 12
    available_slots: Optional[List[int]] = []

class SubjectBase(BaseModel):
    name: str
    code: str
    is_lab: bool = False
    credits: int
    required_room_type: str = "LectureHall"
    duration_slots: int = 1
    teacher_id: Optional[int] = None

class RoomBase(BaseModel):
    name: str
    capacity: int
    type: str = "LectureHall"
    resources: List[str] = []

class ClassGroupBase(BaseModel):
    name: str
    student_count: int

class TimeSlotBase(BaseModel):
    day: str
    period: int
    start_time: str
    end_time: str
    is_break: bool = False

# --- Create Schemas ---

class TeacherCreate(TeacherBase):
    pass

class SubjectCreate(SubjectBase):
    pass

class RoomCreate(RoomBase):
    pass

class ClassGroupCreate(ClassGroupBase):
    pass

class TimeSlotCreate(TimeSlotBase):
    pass

# --- Operation Schemas ---

class HolidayBase(BaseModel):
    date: str
    name: str

class HolidayCreate(HolidayBase):
    pass

class SubstitutionBase(BaseModel):
    date: str
    timetable_entry_id: int
    original_teacher_id: int
    substitute_teacher_id: Optional[int] = None
    status: str = "pending"

class SubstitutionCreate(SubstitutionBase):
    pass

class Holiday(HolidayBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class Substitution(SubstitutionBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class BreakDef(BaseModel):
    # Either position (after which period) or start_time (HH:MM) must be provided
    position: Optional[int] = None
    start_time: Optional[str] = None
    duration: int


class ScheduleConfigBase(BaseModel):
    day_start_time: str = "09:00"
    day_end_time: Optional[str] = None
    working_minutes_per_day: Optional[int] = None

    number_of_periods: Optional[int] = None
    period_duration_minutes: Optional[int] = None

    breaks: List[BreakDef] = []

    lunch_break_start: str = "12:00"
    lunch_break_end: str = "13:00"
    schedule_days: List[str] = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    institution: Optional[str] = None

class ScheduleConfig(ScheduleConfigBase):
    id: int
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

# --- Response Models ---

class Teacher(TeacherBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class Subject(SubjectBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class Room(RoomBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ClassGroup(ClassGroupBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class TimeSlot(TimeSlotBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class TimetableEntry(BaseModel):
    id: int
    version_id: Optional[int] = None
    time_slot_id: Optional[int] = None
    subject_id: Optional[int] = None
    room_id: Optional[int] = None
    class_group_id: Optional[int] = None
    teacher_id: Optional[int] = None
    
    time_slot: Optional[TimeSlot] = None
    subject: Optional[Subject] = None
    room: Optional[Room] = None
    class_group: Optional[ClassGroup] = None
    teacher: Optional[Teacher] = None
    
    model_config = ConfigDict(from_attributes=True)

class TimetableVersionShort(BaseModel):
    id: int
    name: str
    algorithm: str
    status: str
    is_valid: bool
    fitness_score: Optional[int]
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class TimetableVersion(TimetableVersionShort):
    entries: List[TimetableEntry] = []
    
    model_config = ConfigDict(from_attributes=True)

# --- Analytics Schemas ---

class UtilizationStats(BaseModel):
    id: int
    name: str
    assigned_slots: int
    total_slots: int
    utilization_percentage: float

class AnalyticsReport(BaseModel):
    teacher_utilization: List[UtilizationStats]
    room_utilization: List[UtilizationStats]
    conflicts: List[str]
    subject_load: dict # subject_id -> load_factor

# Substitution Schemas
class MarkAbsentRequest(BaseModel):
    teacher_id: int
    date: str  # Format: YYYY-MM-DD
    reason: Optional[str] = "Not specified"

class AssignSubstituteRequest(BaseModel):
    timetable_entry_id: int
    date: str
    substitute_teacher_id: int
    original_teacher_id: int

class CancelClassRequest(BaseModel):
    timetable_entry_id: int
    date: str
    original_teacher_id: int
    reason: Optional[str] = "No substitute available"

class AffectedClass(BaseModel):
    entry_id: int
    subject_name: str
    time_slot: str
    class_group_name: str
    room_name: str

class SuggestedTeacher(BaseModel):
    teacher_id: int
    teacher_name: str
    available_for_all: bool
    teaches_same_subject: bool
    current_classes_that_day: int

class AbsentResponse(BaseModel):
    teacher_name: str
    date: str
    affected_classes: List[AffectedClass]
    suggested_substitutes: List[SuggestedTeacher]

class SubstitutionResponse(BaseModel):
    id: int
    date: str
    original_teacher: str
    substitute_teacher: Optional[str]
    subject: str
    time_slot: str
    class_group: str
    status: str

class SubstitutionCreate(BaseModel):
    date: str
    timetable_entry_id: int
    original_teacher_id: int
    substitute_teacher_id: Optional[int] = None
    status: str = "pending"

# --- Lesson Schemas ---

class LessonCreate(BaseModel):
    teacher_ids: List[int]
    class_group_ids: List[int]
    subject_ids: List[int]
    lessons_per_week: int = 1
    length_per_lesson: int = 1

class LessonUpdate(LessonCreate):
    pass

class Lesson(BaseModel):
    id: int
    lessons_per_week: int
    length_per_lesson: int
    teachers: List[Teacher]
    class_groups: List[ClassGroup]
    subjects: List[Subject]
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class BulkImportRequest(BaseModel):
    text: str
    clear_existing: bool = False

class BulkImportResponse(BaseModel):
    success_count: int
    fail_count: int
    errors: List[str]
