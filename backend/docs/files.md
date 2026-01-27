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
- `import_service.py`: The "Normalizer." It cleans messy text and maps external names/emails to stable database IDs (Issue 5).
- `excel_exporter.py`: Exports timetables to Excel, always showing all slots (8:00-18:00), with lunch breaks and empty slots as required for every section, regardless of shift.
---

## 📂 Utility & Metadata

### 📁 `data_templates/`
Contains sample `.csv` and `.json` files. Use these to understand exactly how students, faculty, and rooms should be formatted.

# Backend File Structure (complete)

This file maps the `backend/` folder and gives a concise purpose for each important file and folder. Keep this page up to date when you add/remove scripts, services, or DB models.

## Top-level files
- `README.md`: Backend-specific quickstart, developer notes, and script usage (ingest → generate → export).
- `requirements.txt`: Python dependencies for the backend.
- `.env.example`: Example environment variables (copy to `.env` and set `DATABASE_URL`).
- `.gitignore`: Files and patterns excluded from version control.
- `alembic.ini`: Alembic configuration for DB migrations.

## `app/` — Application code
This folder contains the FastAPI app, DB core, models, services, routes and schema validation.

- `app/__init__.py`: Package marker and service exports.
- `app/main.py`: FastAPI application entrypoint; registers routes and starts the server.
- `app/database.py`: Legacy/compat DB helper (keeps connection utilities in one place).

### `app/core/`
- `app/core/__init__.py`: Core package marker.
- `app/core/database.py`: SQLAlchemy session factory and DB connection helpers used by services and CLI scripts.

### `app/models/` — Database models (SQLAlchemy)
- `base.py`: Declarative base and common mixins (timestamps, helper methods).
- `faculty.py`: `Faculty` model (name, email, code, metadata).
- `course.py`: `Course` model (code, name, credits, type (LECTURE/LAB), etc.).
- `room.py`: `Room` model (code, capacity, type LAB/LECTURE).
- `section.py`: `Section` model (name/code, batch, shift, linked courses).
- `timeslot.py`: `Timeslot` model (day, start_time, end_time).
- `assignment.py`: `Assignment` model linking `section`, `course`, `room`, `faculty`, `timeslot`.
- `timetable.py`: `TimetableVersion` snapshot model storing the solver output JSON.
- `__init__.py`: Exports or convenience imports for models.

### `app/schemas/`
- `validation.py`: Pydantic schemas used by the validator and upload endpoints to validate file rows and report user-friendly errors.

### `app/services/` — Business logic and helpers
- `solver.py`: The solver engine (OR-Tools CP-SAT integration with a pure-Python fallback). Responsible for building the constraint model and solving.
- `timetable_manager.py`: Orchestrates data extraction from DB, calls the solver, and persists `TimetableVersion` snapshots.
- `import_service.py`: Normalizes and imports CSV rows into the DB (maps CSV columns to models, upserts where appropriate).
- `normalization_agent.py`: Utilities for fuzzy / heuristic normalization (name matching, canonicalization).
- `validator.py`: High-level file/CSV validator that checks headers, required columns, and cross-file references.
- `validator_row.py`: Row-level validation and human-friendly error explanation (uses `explainer.py`).
- `explainer.py`: Converts low-level validation/exception details into readable messages for users.
- `excel_exporter.py`: The canonical Excel exporter. Produces per-section sheets, includes all time-slots (08:00–18:00), inserts lunch break slots per shift, and leaves unused slots empty. Note: `scripts/export.py` post-processes the output to merge adjacent LAB cells.

### `app/routes/` — API endpoints
- `routes/__init__.py`: Route registration helpers.
- `routes/upload.py`: HTTP endpoints to upload CSVs and trigger validation/import flows.
- `routes/normalization.py`: Endpoints to preview normalization suggestions and mapping decisions.

## `scripts/` — CLI utilities
These scripts are the recommended workflow for ingesting data, running the solver, and exporting results.

- `import_pipeline.py`: Full ingestion pipeline — validates CSVs in `backend/rawData/`, normalizes them, and writes normalized records to the DB. Run this first after placing CSVs in `rawData/`.
- `generate.py`: Reads normalized DB data, ensures standard `Timeslot` records exist (Mon–Fri 08:00–18:00 if missing), invokes `TimetableManager` to generate a new `TimetableVersion`.
- `export.py`: Exports a given `TimetableVersion` to Excel using `app.services.excel_exporter`, then post-processes the workbook to merge adjacent LAB cells (two-hour labs). Usage: `python backend/scripts/export.py <version_id>`.
- `reset_db.py`: Utility script for development to drop/reset DB state (use with caution; not for production).

## `data_templates/` and `rawData/`
- `data_templates/`: Canonical sample CSVs and JSON templates (faculty.csv, courses.csv, sections.csv, faculty_course_map.csv, rooms.csv, time_config.json). Use these as upload examples.
- `rawData/`: Directory where you place your real input CSVs before running `import_pipeline.py`.

## `docs/`
- `HIT.md`: High-level "How It Works" document describing ingestion → solver → export flow and testing steps.
- `files.md`: (this file) maps backend files — keep updated.
- `data_contracts.md`: Detailed data contracts and column-level expectations for CSV uploads.

## `tests/` — Unit & integration tests
- `test_db_connection.py`: Verifies DB connectivity and basic session behavior.
- `test_solver_logic.py`: Tests solver behavior and core constraints.
- `test_excel_exporter.py`: Tests exporter output structure (grid, lunch slots, merging behavior expectation).
- `test_validator.py`: Tests CSV validation logic.
- `test_explainer.py`: Tests the human-friendly explanation generator.
- `test_integration.py`, `test_connection_simple.py`: Combined/utility integration tests.

## `alembic/` — DB migrations
- `alembic/env.py`, `alembic/script.py.mako`, `alembic/versions/*.py`: Alembic config and migration scripts used to evolve the DB schema.

---
