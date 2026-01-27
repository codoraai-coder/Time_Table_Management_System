# How It Works
# How It Works

This document describes the backend pipeline and quick test steps for generating and exporting timetables.

Key export invariants:
- Every section's Excel sheet always contains these slots: `08:00-09:00`, `09:00-10:00`, `16:00-17:00`, `17:00-18:00` (left empty if unused).
- Lunch break is inserted as an empty slot per section shift: `12:00-13:00` for the 08:00–16:00 shift; `13:00-14:00` for the 10:00–18:00 shift.

## Workflow (ingest → generate → export)

1. Place CSV input files into `backend/rawData/` (use `backend/data_templates/` as reference).
2. Validate and import the CSVs into the database:

```bash
python backend/scripts/import_pipeline.py <folder with data/>
```

3. Generate a timetable using the normalized DB data (creates standard timeslots if missing):

```bash
python backend/scripts/generate.py
```

4. Export a specific timetable version to Excel (post-processing merges two-hour LAB cells):

```bash
python backend/scripts/export.py <version_id>
```

Notes:
- The exporter module is `backend/app/services/excel_exporter.py` and always renders the full 08:00–18:00 grid per section; `export.py` additionally post-processes to merge adjacent LAB columns when appropriate.
- Do not run `reset_db.py` on production; it is a development helper.

## Quick test steps

- Populate `backend/rawData/` with the sample CSVs from `backend/data_templates/`.
- Run the three scripts above in order: `import_pipeline.py rawData/`, `generate.py`, `export.py 1`.
- Open the produced `timetable_v1.xlsx` to verify:
  - All required slots exist (including the four specified slots).
  - Lunch break slots are empty for each section according to its shift.
  - LAB sessions spanning two hours are merged in the exported sheet.

## Visual flow

```mermaid
graph TD
  A[rawData CSVs] --> B[ValidatorService]
  B --> C[ImportService]
  C --> D[(PostgreSQL DB)]
  D --> E[TimetableManager]
  E --> F[Solver Engine]
  F --> G[TimetableVersion (snapshot)]
  G --> H[Excel Export]
```

## Example (normalization → solver output)

Input CSV row (messy):

```
"  dr. smith ", CS101
```

Normalization log (example):

```
[Faculty] Trimming '  dr. smith ' -> 'dr. smith' (email normalized)
```

Solver JSON (example snapshot):

```json
{
  "version": 1,
  "status": "FEASIBLE",
  "assignments": [
    {
      "section": "CS-2024-A",
      "faculty": "dr. smith",
      "course": "CS101",
      "room": "Room-101",
      "timeslot": "Monday 09:00-10:00"
    }
  ]
}
```
