# 🏗 Codora Timetable — System Architecture

## 1. Overview

Codora Timetable is a **deterministic scheduling system** designed to generate and manage college timetables with high correctness, explainability, and controlled change handling.

The system follows a **layered architecture** where:
- data correctness is enforced before computation,
- a solver acts as the single source of truth,
- AI assists humans but never makes scheduling decisions.

---

## 2. Core Design Principles

1. **Correctness First**  
   Invalid data must never reach the solver.

2. **Deterministic Core**  
   Timetable generation is handled by a constraint solver, not AI.

3. **Clear Responsibility Separation**  
   Ingestion, validation, normalization, solving, repair, and explanation are isolated layers.

4. **Human-in-the-Loop**  
   No silent changes. All major changes are explainable and reviewable.

5. **Incremental Evolution**  
   Changes should minimally disrupt existing timetables.

---

## 3. High-Level Architecture

```
┌────────────────────────────┐
│          Frontend          │
│        (Next.js UI)        │
│                            │
│  - Upload data files       │
│  - View validation output  │
│  - View timetables         │
│  - Trigger generation      │
└───────────────┬────────────┘
                │
                ▼
┌────────────────────────────┐
│        API Gateway          │
│        (FastAPI)            │
│                            │
│  - Request routing         │
│  - Input validation        │
│  - Auth (future)           │
└───────────────┬────────────┘
                │
                ▼
┌────────────────────────────────────────────────────┐
│                   Backend Core                      │
│                                                    │
│  ┌────────────┐   ┌────────────┐   ┌────────────┐ │
│  │ Ingestion  │ → │ Validation │ → │Normalization│ │
│  └────────────┘   └────────────┘   └────────────┘ │
│                                                    │
│  ┌────────────┐   ┌────────────┐                  │
│  │   Solver   │ → │ Repair Eng │                  │
│  └────────────┘   └────────────┘                  │
│                                                    │
│  ┌────────────┐                                    │
│  │ Versioning │                                    │
│  └────────────┘                                    │
└───────────────┬────────────────────────────────────┘
                │
                ▼
┌────────────────────────────┐
│        PostgreSQL DB        │
│                            │
│  - Canonical entities      │
│  - Timetable versions      │
│  - Assignments             │
│  - Audit logs              │
└────────────────────────────┘

                ▲
                │
┌────────────────────────────┐
│        AI Services          │
│                            │
│  - Explain errors          │
│  - Suggest mappings        │
│  - Explain repairs         │
│  - Summarize changes       │
└────────────────────────────┘
```

---

## 4. Component Responsibilities

### 4.1 Frontend (Next.js)

**Responsibilities**
- Upload CSV/JSON files
- Display validation errors and warnings
- Render read-only timetables
- Trigger generation actions

**Non-responsibilities**
- Parsing CSVs
- Business logic
- Constraint enforcement

Frontend acts as a **viewer and controller**, not a decision-maker.

---

### 4.2 API Gateway (FastAPI)

**Responsibilities**
- Single entry point for all clients
- Routing requests to backend services
- Input/output schema enforcement
- Authentication (future)

---

### 4.3 Ingestion Service

**Input**
- Six raw files:
  - `sections.csv`
  - `faculty.csv`
  - `courses.csv`
  - `rooms.csv`
  - `faculty_course_map.csv`
  - `time_config.json`

**Responsibilities**
- Accept and store raw uploads
- Generate `upload_id`
- Forward data to validation

Raw files are **never trusted**.

---

### 4.4 Validation Engine

**Purpose**
Prevent invalid or impossible data from entering the system.

**Layers**
1. **Structural Validation**
2. **Semantic Validation**

**Output**
```json
{
  "errors": [],
  "warnings": [],
  "suggestions": []
}
```

---

### 4.5 Normalization Layer

**Purpose**
Convert messy human data into solver-safe canonical data.

**Responsibilities**
- Trim whitespace
- Normalize casing
- Generate stable internal IDs
- Preserve original labels for display

**Invariant**
The solver never sees raw human data.

---

### 4.6 Data Store (PostgreSQL)

**Why PostgreSQL**
- ACID transactions
- Strong relational integrity
- JSONB support
- Versioning-friendly

---

## 5. Solver Service (Deterministic Core)

**Technology**
- OR-Tools (CP-SAT)

**Responsibilities**
- Generate conflict-free timetables
- Enforce constraints (shifts, lunch, capacity, labs)

Solver never reads raw files.

---

## 6. Repair Engine

Handles timetable changes with minimal disruption by re-solving only affected slots.

---

## 7. AI Services (Assistant Layer)

AI explains, suggests, and summarizes.  
AI never decides schedules.

---

## 8. Versioning & Audit

Every major action creates a new version with full traceability.

---

## 9. End-to-End Data Flow

```
Upload → Validate → Normalize → Persist → Solve → Version → Display
```

---

## 10. Architecture Summary

Codora Timetable is a layered, deterministic scheduling system where correctness is enforced at every boundary, changes are versioned, and humans remain in control.
