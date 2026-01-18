# Data Contracts - Timetable Management System

This document defines the official input schemas for the system. These contracts are frozen for Phase 1. All data uploaded by colleges must strictly adhere to these formats.

## CSV File Requirements
- **Encoding**: UTF-8
- **Delimiter**: Comma (`,`)
- **Headers**: Required, must match the names exactly (case-sensitive).

---

## 1. `faculty.csv`
Defines the teaching staff available for scheduling.

| Column | Meaning | Data Type | Required | Constraints | Example |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | Internal Unique ID | Integer | Yes | Positive, unique | `101` |
| `name` | Full Name | String | Yes | Max 100 chars | `Dr. Alice Smith` |
| `email` | Primary Email | String | Yes | Valid email format, unique | `alice@uni.edu` |

## 2. `courses.csv`
The catalog of subjects offered.

| Column | Meaning | Data Type | Required | Constraints | Example |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `code` | Unique Code | String | Yes | Alphanumeric, unique | `CS101` |
| `name` | Course Title | String | Yes | Max 150 chars | `Intro to CS` |

## 3. `rooms.csv`
Available physical venues.

| Column | Meaning | Data Type | Required | Constraints | Example |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `name` | Room Number/Name | String | Yes | Unique | `Lab-301` |
| `type` | Room Category | String | Yes | `Lecture` OR `Lab` | `Lab` |

## 4. `sections.csv`
Specific groups of students attending a course.

| Column | Meaning | Data Type | Required | Constraints | Example |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | Unique Section ID | String | Yes | Unique | `2024-CS-A` |
| `course_code` | Linked Course | String | Yes | Must exist in `courses.csv` | `CS101` |
| `student_count`| Current Strength | Integer | Yes | Minimum: 1 | `35` |
| `room_type` | Required Venue | String | Yes | `Lecture` OR `Lab` | `Lecture` |

## 5. `faculty_course_map.csv`
Linking sections to instructors.

| Column | Meaning | Data Type | Required | Constraints | Example |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `faculty_email`| Instructor | String | Yes | Must exist in `faculty.csv` | `alice@uni.edu` |
| `section_id` | Assigned Section | String | Yes | Must exist in `sections.csv` | `2024-CS-A` |

---

## 6. `time_config.json`
Configuration for the weekly timetable structure.

| Field | Meaning | Type | Required | Constraints |
| :--- | :--- | :--- | :--- | :--- |
| `working_days` | Active days of week | Array[Int] | Yes | 0 (Mon) to 6 (Sun) |
| `slots_per_day`| Specific time blocks | Array[Obj] | Yes | Must contain `start`, `end` |

**Example:**
```json
{
  "shifts": [
    {
      "name": "Morning Shift",
      "start": "08:00",
      "end": "16:00",
      "lunch": {"start": "12:00", "end": "13:00"}
    },
    {
      "name": "Evening Shift",
      "start": "10:00",
      "end": "18:00",
      "lunch": {"start": "13:00", "end": "14:00"}
    }
  ],
  "working_days": [0, 1, 2, 3, 4]
}
```
