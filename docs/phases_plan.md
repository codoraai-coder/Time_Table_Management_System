**# CodoraAI Timetable Agent

## Complete End-to-End Development Roadmap

---

## BIG PICTURE (keep this fixed in mind)

Your product has 4 brains, built in this order:

1️⃣ Constraint Brain (Solver)
2️⃣ Repair Brain (Incremental fixing)
3️⃣ Trust Brain (Explain + approve)
4️⃣ Convenience Brain (AI + UI)

If you break this order → product fails.

---

# PHASE 0 — Product Definition (Day 0–1)

### Objective

Freeze scope so you don’t keep changing direction.

### Define this clearly (write it down)

* Target: Engineering colleges (India)
* Users:
  * Admin (Academic office)
  * HOD
  * Class Advisor
  * Faculty
* Core promise:
  “Conflict-free timetable + safe auto-repair with explanations”

❌ Do NOT promise “AI timetable”
✅ Promise “error-free + explainable + change-friendly timetable”

---

# PHASE 1 — Data Foundation (Week 1)

### Goal

Make data predictable, even if uploads are messy.

### What to build FIRST

#### 1️⃣ Finalize Input Contracts (MOST IMPORTANT)

Lock these templates forever:

* sections.csv
* rooms.csv
* faculty.csv
* courses.csv
* faculty_course_map.csv
* time_config.json

For EACH column define:

* meaning
* allowed values
* example

👉 This is your API contract with colleges

If this is weak → everything breaks.

---

#### 2️⃣ Validation Engine

Build strict validation:

* missing columns
* wrong room types
* capacity mismatch
* unknown faculty/course/section
* impossible constraints (lab with no lab room)

Output:

{

  "errors": [...],

  "warnings": [...],

  "suggestions": [...]

}

This alone already saves HODs hours.

---

#### 3️⃣ Normalization Layer

Before solver:

* trim spaces
* unify naming
* generate internal IDs

This is non-negotiable.

---

# PHASE 2 — Core Timetable Solver (Week 2)

### Goal

Generate a guaranteed valid timetable.

### This is the HEART of the product.

---

## Build Solver in this exact order

### 4️⃣ Hard Constraints (never violated)

Implement first:

* One class per section per slot
* One class per room per slot
* One class per faculty per slot
* Room capacity ≥ section strength
* Room type matches course type
* Faculty max load per day
* Shift timing respected

💡 If solver fails → return why, not just “failed”.

---

### 5️⃣ Medium Constraints

Add next:

* Labs must be consecutive (2–3 slots)
* Avoid faculty having 4 continuous periods
* No class during recess

---

### 6️⃣ Soft Optimization (later)

Objective function:

* minimize faculty idle gaps
* minimize room changes
* spread heavy subjects

⚠️ Soft constraints come AFTER hard constraints.

---

### Output of this phase

* Draft timetable
* Conflict report
* Feasibility explanation
* **[ACCELERATED]** Basic Upload UI & Timetable Viewer

At this point:
✅ Backend works
✅ Basic UI works (Upload -> View)
❌ No AI Agents yet
❌ No Manual Changes yet

---

# PHASE 3 — Repair & Change Handling (Week 3)

### Goal

Handle real-world chaos (this is your USP).

---

## This is where most products fail — you will win here.

### 7️⃣ Conflict Detector

Any change should instantly detect:

* room conflict
* faculty conflict
* section conflict
* capacity issue

Return structured conflict graph.

---

### 8️⃣ Incremental Repair Engine (CRITICAL)

This implements your requirement:

“If faculty changes room and room is occupied, system auto-handles sequentially”

#### Repair logic:

1. Identify impacted nodes only
2. Freeze everything else
3. Re-solve small sub-problem
4. Rank solutions by:
   * minimum changes
   * same faculty
   * same day
   * same room type

This is NOT AI.
This is solver logic.

---

### 9️⃣ Versioning System

Every change creates:

* Draft v1
* Draft v2
* Published v1

Store:

* who changed
* what changed
* why changed

This builds institutional trust.

---

# PHASE 4 — Minimal Frontend (Week 4)

### Goal

Make it usable, not beautiful.

---

## Build ONLY these screens

### 10️⃣ Upload Wizard

* Upload bundle
* See validation report
* Fix errors
* Generate timetable

---

### 11️⃣ Timetable Views

* Section timetable
* Faculty timetable
* Room timetable

Simple grid.
No animations.
No drag-drop yet.

---

### 12️⃣ Manual Change Screen

* Select class
* Propose move
* See conflict/repair options
* Apply

At this point:
🎉 You already have a SELLABLE product.

---

# PHASE 5 — AI Agents (Week 5)

### Goal

Reduce human effort, not replace logic.

---

## Add AI ONLY here

### 13️⃣ Upload Mapper Agent

Purpose:

* map messy Excel to templates
* auto-fix column names
* ask clarifying questions

This saves days for colleges.

---

### 14️⃣ Repair Explainer Agent

After repair:

“We moved DBMS from Tue P2 to Wed P4 to avoid faculty conflict with AIML2A.”

This builds confidence, not automation hype.

---

### 15️⃣ Natural Language Change Agent (Optional)

Example:

“Swap CSE2A DBMS Tue P2 with Wed P5”

Agent:

* converts to structured request
* solver decides feasibility

---

# PHASE 6 — Notifications & Roles (Week 6)

### Goal

Operational readiness.

---

### 16️⃣ Role-Based Access

* Admin: everything
* HOD: approve/publish
* Advisor: propose edits
* Faculty: view only

---

### 17️⃣ Notifications

* Publish → notify faculty
* Change → notify impacted only

Email first → WhatsApp later.

---

# PHASE 7 — Production Hardening (Week 7)

### Goal

Make it reliable for real colleges.

---

### 18️⃣ Performance

* Async solver jobs
* Progress tracking
* Timeout handling

---

### 19️⃣ Data Safety

* Backup
* Rollback
* Audit logs

---

### 20️⃣ Pilot Deployment

* One department
* One semester
* Real data

Fix pain points.

---

# FINAL PRODUCT STACK (End State)

Frontend (Next.js)

↓

FastAPI Backend

↓

Validation + Repair Engine

↓

OR-Tools Solver

↓

AI Agents (mapping + explanation)

↓

Postgres + Redis

↓

Notifications

---

## MOST IMPORTANT ADVICE (Read this twice)

❌ Don’t start with AI
❌ Don’t start with UI
❌ Don’t over-optimize early

✅ Start with constraints + repair
✅ Make failures explainable
✅ Win trust of HODs

---

**
