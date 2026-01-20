# Backend File Structure

This document provides a map of the backend project directory and explains the purpose of each key file.

## 📂 Root Folder: `/backend`

| File / Folder | Description |
| :--- | :--- |
| `README.md` | General project overview, feature lists, and quick-start instructions. |
| `requirements.txt` | List of Python dependencies required to run the project. |
| `.env` | Local environment variables (e.g., `DATABASE_URL`). **Do not commit secrets.** |
| `.env.example` | Template for environment variables to help new developers set up. |

---

## 📂 Core Logic: `/backend/app`

### `main.py`
The entry point for the FastAPI application. It initializes the web server and hooks up the API routes.

### `database.py`
Handles the connection logic to the PostgreSQL (Neon) database using SQLAlchemy.

### 📁 `models/` (Database Tables)
- `base.py`: The SQLAlchemy "Declarative Base" and common mixins (like timestamps).
- `faculty.py`: Stores teacher information (names, emails).
- `course.py`: Stores the list of subjects offered by the college.
- `room.py`: Stores physical locations (Lecture halls, Labs).
- `section.py`: Stores groups of students (e.g., "Class-A").
- `timeslot.py`: Defines common periods (e.g., "9:00 AM - 10:00 AM").
- `assignment.py`: Records which section meets in which room at which time with which teacher.
- `timetable.py`: Represents a full "Snapshot" or version of a generated timetable.

### 📁 `services/` (Business Logic)
- `solver.py`: The computational engine. It uses OR-Tools (or a Python fallback) to solve the timetable puzzle without conflicts.
- `timetable_manager.py`: The orchestrator. It fetches data from models, sends it to the solver, and saves the results.
- `validator.py`: The "Gatekeeper." It checks if uploaded CSV files follow the system rules (Issue 4).

---

## 📂 Utility & Metadata

### 📁 `data_templates/`
Contains sample `.csv` and `.json` files. Use these to understand exactly how students, faculty, and rooms should be formatted.

### 📁 `docs/`
- `data_contracts.md`: Detailed technical specifications for every data column.
- `files.md`: (This file) Map of the project structure.

### 📁 `scripts/`
- `generate_v1.py`: A CLI script that populates the database with sample data and triggers the very first timetable generation.

### 📁 `tests/`
- `test_db_connection.py`: Verifies that Python can talk to the Neon database.
- `test_solver_logic.py`: Rigorously tests the scheduling engine to ensure no conflicts are possible.
- `test_validator.py`: Verifies that the validation system can catch faulty user data.
