# Data Contracts - Timetable Management System

This document defines the official input schemas for the system. The canonical sample files live in `backend/data_templates/`. The importer/validator will enforce these contracts and accepts a small set of header aliases for backward compatibility.

## CSV File Requirements
- Encoding: UTF-8
- Delimiter: comma (`,`) 
- Headers: required; use the canonical names below. The importer also accepts common aliases (documented per section).
- Time format: `HH:MM-HH:MM` or `HH:MM - HH:MM` (24-hour). Whitespace is normalized.

---

## 1) `faculty.csv`
Canonical columns:

- `id` (string): stable faculty identifier (e.g. `F_SHARMA`). Required, unique.
- `name` (string): faculty full name. Required.
- `email` (string): primary email. Required, valid email format, unique.

Accepted alias: `code` → `id`.

Example:

```
F_SHARMA,A. SHARMA,F_SHARMA@college.edu
```

---

## 2) `courses.csv`
Canonical columns:

- `code` (string): unique course code (e.g. `DBMS`, `DBMS_LAB`). Required, unique.
- `name` (string): course title. Required.
- `credits` (integer, optional): credit units.

Example:

```
DBMS,Database Management Systems,4
```

---

## 3) `rooms.csv`
Canonical columns:

- `code` or `name` (string): unique room identifier (e.g. `AB_101`, `LAB_1`). Required, unique.
- `type` (string): `Lecture` or `Lab` (case-insensitive). Required.
- `capacity` (integer, optional): seating capacity.

Importer notes: `name` is accepted as alias for `code` and normalized to `code` internally.

Example:

```
AB_101,Lecture,60
LAB_1,Lab,30
```

---

## 4) `sections.csv`
Canonical columns:

- `id` (string): section identifier (e.g. `CSE_2A-DBMS`). Required, unique.
- `course_code` (string): must reference `courses.code`. Required.
- `student_count` (integer): required, >= 1.
- `room_type` (string): `Lecture` or `Lab`. Required.
- `shift` (string): one of `SHIFT_8_4` or `SHIFT_10_6`. Required.

Accepted alias: `code` → `id`.

Example:

```
CSE_2A-DBMS,DBMS,60,Lecture,SHIFT_8_4
```

---

## 5) `faculty_course_map.csv` (mapping)
Canonical/accepted columns:

- `faculty_email` or `faculty_id` (string): identifies instructor. If email is provided it must match `faculty.email`; if id is provided it must match `faculty.id`.
- `section_id` or `section` (string): section identifier; must match `sections.id`.
- `course_code` (string, optional but recommended): must match `courses.code` when present.

Example:

```
F_DAROS@college.edu,CSE_2A-DBMS,DBMS
```

---

## 6) `time_config.json`
JSON configuration describing shifts and working days. Required fields:

- `shifts`: array of objects with `name`, `start`, `end`; each shift may include a `lunch` object with `start`/`end` times. Times MUST be `HH:MM` strings.
- `working_days`: array of integers 0..6 (0 = Monday).

Example:

```json
{
  "shifts": [
    { "name": "Morning", "start": "08:00", "end": "16:00", "lunch": { "start": "12:00", "end": "13:00" } },
    { "name": "Evening", "start": "10:00", "end": "18:00", "lunch": { "start": "13:00", "end": "14:00" } }
  ],
  "working_days": [0,1,2,3,4]
}
```

---

## Validation & Import rules (summary)

- Required unique keys: `faculty.id` (or `faculty.email`), `courses.code`, `rooms.code`, `sections.id`.
- Referential integrity: `sections.course_code` must exist in `courses`; mappings must resolve to existing faculty and sections.
- Normalization: whitespace trimmed, case normalization for codes, time strings normalized (e.g. `08:00 - 09:00` → `08:00-09:00`).
- Supported shifts: `SHIFT_8_4` → lunch `12:00-13:00`; `SHIFT_10_6` → lunch `13:00-14:00`.
- If only header aliases differ (e.g. `code` vs `id`), importer accepts them; structure or missing required fields will produce validation errors and an import report.

