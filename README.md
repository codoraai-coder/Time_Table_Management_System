# Codora Timetable

Codora Timetable is a constraint-based timetable generation system for colleges.

## Current Phase
Phase 1 – Foundation

## What we are building right now
- Upload timetable data
- Generate a valid, conflict-free timetable
- Display timetable (read-only)

## What we are NOT building yet
- Auto-repair
- Editing
- Optimization
- Notifications

See `/docs/team-guide.pdf` for how we work.


cd backend

# 1. Install dependencies
pip install -r requirements.txt

# 2. Setup environment
cp .env.example .env
# Edit .env and add DATABASE_URL (or leave as SQLite for testing)

# 3. Run the server
uvicorn app.main:app --reload

# Server runs on: http://localhost:8000
# API docs: http://localhost:8000/docs


## frontend


cd frontend

# 1. Install dependencies
npm install

# 2. Set API URL (it defaults to localhost:8000)
# Create .env.local if needed:
# NEXT_PUBLIC_API_URL=http://localhost:8000

# 3. Run dev server
npm run dev

# Frontend runs on: http://localhost:3000