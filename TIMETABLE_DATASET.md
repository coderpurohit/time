# Timetable Dataset - Tabular Format

## Dataset Summary

- **Total Teachers**: 10
- **Total Subjects**: 5  
- **Total Rooms**: 15
- **Days**: Monday to Friday
- **Time Slots per Day**: 6 (09:00-16:00)
- **Class Groups**: 5 (TE-A, TE-B, SE-A, SE-B, FE-A)
- **Total Timetable Entries**: 150

## Sample Timetable - Class TE-A

| Day | Time | Subject | Teacher | Room |
|-----|------|---------|---------|------|
| Monday | 09:00-10:00 | ENG | Prof. Iyer | Room 302 |
| Monday | 10:00-11:00 | CS | Prof. Verma | Lab 204 |
| Monday | 11:00-12:00 | PHY | Prof. Kumar | Lab 401 |
| Monday | 13:00-14:00 | CHEM | Dr. Reddy | Lab 401 |
| Monday | 14:00-15:00 | MATH | Dr. Patel | Room 502 |
| Monday | 15:00-16:00 | CS | Dr. Joshi | Lab 204 |
| Tuesday | 09:00-10:00 | ENG | Dr. Nair | Room 302 |
| Tuesday | 10:00-11:00 | CS | Prof. Verma | Lab 201 |
| Tuesday | 11:00-12:00 | PHY | Prof. Singh | Lab 401 |
| Tuesday | 13:00-14:00 | MATH | Dr. Patel | Room 501 |
| Tuesday | 14:00-15:00 | CHEM | Dr. Reddy | Lab 203 |
| Tuesday | 15:00-16:00 | CS | Dr. Joshi | Lab 203 |
| Wednesday | 09:00-10:00 | ENG | Prof. Iyer | Room 103 |
| Wednesday | 10:00-11:00 | PHY | Prof. Singh | Lab 203 |
| Wednesday | 11:00-12:00 | MATH | Dr. Patel | Room 102 |
| Wednesday | 13:00-14:00 | CHEM | Dr. Reddy | Lab 202 |
| Wednesday | 14:00-15:00 | CS | Dr. Joshi | Lab 203 |
| Wednesday | 15:00-16:00 | PHY | Prof. Kumar | Lab 402 |
| Thursday | 09:00-10:00 | CHEM | Dr. Reddy | Lab 202 |
| Thursday | 10:00-11:00 | CS | Prof. Verma | Lab 203 |
| Thursday | 11:00-12:00 | PHY | Prof. Singh | Lab 202 |
| Thursday | 13:00-14:00 | MATH | Dr. Patel | Room 301 |
| Thursday | 14:00-15:00 | ENG | Dr. Nair | Room 302 |
| Thursday | 15:00-16:00 | PHY | Prof. Kumar | Lab 201 |
| Friday | 09:00-10:00 | CHEM | Dr. Reddy | Lab 201 |
| Friday | 10:00-11:00 | CS | Prof. Verma | Lab 401 |
| Friday | 11:00-12:00 | PHY | Prof. Singh | Lab 203 |
| Friday | 13:00-14:00 | ENG | Dr. Nair | Room 101 |
| Friday | 14:00-15:00 | MATH | Dr. Patel | Room 103 |
| Friday | 15:00-16:00 | CHEM | Dr. Reddy | Lab 201 |

## Teachers & Subject Assignment

| Teacher | Email | Subject |
|---------|-------|---------|
| Dr. Sharma | sharma@college.edu | MATH |
| Dr. Patel | patel@college.edu | MATH |
| Prof. Kumar | kumar@college.edu | PHY |
| Prof. Singh | singh@college.edu | PHY |
| Dr. Reddy | reddy@college.edu | CHEM |
| Dr. Gupta | gupta@college.edu | CHEM |
| Prof. Verma | verma@college.edu | CS |
| Dr. Joshi | joshi@college.edu | CS |
| Prof. Iyer | iyer@college.edu | ENG |
| Dr. Nair | nair@college.edu | ENG |

## Subjects

| Subject | Code | Is Lab | Credits | Required Room Type |
|---------|------|--------|---------|-------------------|
| Mathematics | MATH | No | 3 | LectureHall |
| Physics | PHY | Yes | 4 | Lab |
| Chemistry | CHEM | Yes | 4 | Lab |
| Computer Science | CS | Yes | 4 | Lab |
| English | ENG | No | 3 | LectureHall |

## Rooms

| Room | Type | Capacity | Resources |
|------|------|----------|-----------|
| Room 101 | LectureHall | 60 | Projector, Whiteboard |
| Room 102 | LectureHall | 60 | Projector, Whiteboard |
| Room 103 | LectureHall | 60 | Projector, Whiteboard |
| Lab 201 | Lab | 30 | Projector, Whiteboard, Lab Equipment |
| Lab 202 | Lab | 30 | Projector, Whiteboard, Lab Equipment |
| Lab 203 | Lab | 30 | Projector, Whiteboard, Lab Equipment |
| Lab 204 | Lab | 30 | Projector, Whiteboard, Lab Equipment |
| Room 301 | LectureHall | 50 | Projector, Whiteboard |
| Room 302 | LectureHall | 50 | Projector, Whiteboard |
| Room 303 | LectureHall | 50 | Projector, Whiteboard |
| Lab 401 | Lab | 25 | Projector, Whiteboard, Lab Equipment |
| Lab 402 | Lab | 25 | Projector, Whiteboard, Lab Equipment |
| Room 501 | LectureHall | 40 | Projector, Whiteboard |
| Room 502 | LectureHall | 40 | Projector, Whiteboard |
| Room 503 | LectureHall | 40 | Projector, Whiteboard |

## Constraint Validation

✅ **All constraints satisfied:**
- Each subject is taught every day
- No teacher teaches two classes at the same time
- No room is double-booked
- Each teacher is assigned exactly one subject
- Lab subjects are allocated to lab rooms
- Lecture subjects are allocated to lecture halls
- Lunch break observed (12:00-13:00)

## JSON Database Format

Complete structured JSON available in: [timetable_dataset.json](file:///c:/Users/bhara/Documents/trae_projects/TimeTable-Generator/timetable_dataset.json)

The JSON file contains:
```json
{
  "teachers": [...],      // 10 teachers
  "subjects": [...],      // 5 subjects
  "rooms": [...],         // 15 rooms  
  "class_groups": [...],  // 5 class groups
  "timetable_entries": [...] // 150 timetable entries
}
```

Each timetable entry includes:
- Day, Period, Start/End Time
- Subject (name, code, is_lab)
- Teacher (name, email)
- Room (name)
- Class Group

This data can be directly imported into your database using the backend API endpoints.
