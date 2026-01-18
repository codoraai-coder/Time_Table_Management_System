# Backend - Timetable Management System

Production-ready FastAPI backend for automated timetable generation.

## Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Database

Create a `.env` file in the `backend/` directory:

```bash
cp .env.example .env
```

Edit `.env` and add your Neon database URL:

```env
DATABASE_URL=postgresql://user:password@ep-xxx.neon.tech/dbname?sslmode=require
```

### 3. Test Database Connection

Run the test script to verify everything works:

```bash
python -m backend.tests.test_db_connection
```

This will:
- ✅ Verify database connection
- ✅ Create all tables
- ✅ Insert sample data
- ✅ Verify data retrieval

## Project Structure

```
backend/
├── app/
│   ├── core/
│   │   ├── __init__.py
│   │   └── database.py          # Database configuration
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py              # Base model & mixins
│   │   ├── faculty.py           # Faculty model
│   │   ├── course.py            # Course model
│   │   ├── section.py           # Section model
│   │   ├── room.py              # Room model
│   │   ├── timeslot.py          # Timeslot model
│   │   ├── assignment.py        # Assignment model
│   │   └── timetable.py         # TimetableVersion model
│   ├── services/                # Business logic (future)
│   ├── api/                     # API routes (future)
│   └── utils/                   # Utilities (future)
├── tests/
│   ├── __init__.py
│   └── test_db_connection.py    # Database test script
├── .env.example                 # Environment variables template
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## Database Models

### Core Entities
- **Faculty**: Teachers/Professors
- **Course**: Subjects (e.g., "Database Systems")
- **Section**: Class groups (e.g., "CS-A", "CS-B")
- **Room**: Physical classrooms/labs
- **Timeslot**: Time periods (e.g., "Monday 9:00-10:00")

### Relationships
- **Assignment**: Links Section + Course + Faculty + Room + Timeslot
- **TimetableVersion**: Immutable snapshots of complete timetables

## Production Deployment

### Environment Variables

Set `DATABASE_URL` in your deployment platform:
- **Vercel/Netlify**: Add in dashboard
- **Docker**: Pass via `-e DATABASE_URL=...`
- **Heroku**: `heroku config:set DATABASE_URL=...`

### Database Migrations (Future)

We'll use Alembic for schema migrations in production.

## Development

### Running Tests

```bash
pytest backend/tests/
```

### Code Quality

```bash
# Format code
black backend/

# Type checking
mypy backend/
```

## Phase 1 - Data Foundation ✅

- [x] Define core data models
- [ ] Define input contracts (CSV/JSON schemas)
- [ ] Build validation engine
- [ ] Build normalization layer
- [ ] Build CP-SAT solver

## License

Proprietary - Codora AI
