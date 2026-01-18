"""
Test script to verify database connection and models.
Works in both local development and production.

Usage:
    python -m backend.tests.test_db_connection
"""

import sys
import os
from datetime import time

# Add project root to path (works whether run from root or backend/)
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../.."))
if os.path.basename(project_root) == "backend":
    project_root = os.path.abspath(os.path.join(project_root, ".."))
sys.path.insert(0, project_root)

try:
    # Try importing with full package path first (run from root)
    from backend.app.models.base import Base
    from backend.app.models import (
        Faculty, Course, Section, Room, Timeslot, Assignment, TimetableVersion
    )
except ImportError:
    # Fallback for running from inside backend/
    sys.path.insert(0, os.path.abspath(os.path.join(current_dir, "..")))
    from app.models.base import Base
    from app.models import (
        Faculty, Course, Section, Room, Timeslot, Assignment, TimetableVersion
    )

from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect

# Load environment variables from .env file (for local development)
load_dotenv()

def test_database_connection():
    """Test database connection and create tables"""
    
    print("=" * 60)
    print("DATABASE CONNECTION TEST")
    print("=" * 60)
    
    # Get DATABASE_URL
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ ERROR: DATABASE_URL environment variable not set")
        print("\nFor local testing, create a .env file in the project root:")
        print("DATABASE_URL=postgresql://user:password@host/dbname")
        sys.exit(1)
    
    # Mask password in output
    masked_url = database_url.split("@")[-1] if "@" in database_url else database_url
    print(f"✓ DATABASE_URL found: ...@{masked_url}")

    # Fix: Force usage of psycopg (v3) driver if psycopg2 is missing
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+psycopg://")

    # Create engine
    print("\n1. Creating database engine...")
    try:
        engine = create_engine(database_url, pool_pre_ping=True)
        print("✓ Engine created successfully")
    except Exception as e:
        print(f"❌ Failed to create engine: {e}")
        sys.exit(1)
    
    # Test connection
    print("\n2. Testing database connection...")
    try:
        with engine.connect() as conn:
            print("✓ Database connection successful")
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        sys.exit(1)
    
    # Create all tables
    print("\n3. Creating database tables...")
    try:
        Base.metadata.create_all(engine)
        print("✓ All tables created successfully")
    except Exception as e:
        print(f"❌ Failed to create tables: {e}")
        sys.exit(1)
    
    # Verify tables exist
    print("\n4. Verifying tables...")
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    expected_tables = {
        "faculty", "courses", "sections", "rooms", 
        "timeslots", "assignments", "timetable_versions"
    }
    
    found_tables = set(tables)
    missing = expected_tables - found_tables
    
    if missing:
        print(f"❌ Missing tables: {missing}")
        sys.exit(1)
    
    print(f"✓ All {len(expected_tables)} tables verified:")
    for table in sorted(expected_tables):
        print(f"  - {table}")
    
    # Test data insertion
    print("\n5. Testing data insertion...")
    from sqlalchemy.orm import Session
    
    try:
        with Session(engine) as session:
            # Cleanup existing test data to avoid UniqueConstraint errors
            session.query(Assignment).delete()
            session.query(Section).delete()
            session.query(Timeslot).delete()
            session.query(Room).delete()
            session.query(Course).delete()
            session.query(Faculty).delete()
            session.commit()
            print("✓ Cleaned up existing test data")

            # Create sample faculty
            faculty = Faculty(name="Dr. John Smith", email="john.smith@example.com")
            session.add(faculty)
            
            # Create sample course
            course = Course(code="CS101", name="Introduction to Programming", credits=4)
            session.add(course)
            
            # Create sample room
            room = Room(name="Room-101", capacity=50, type="Lecture")
            session.add(room)
            
            # Create sample timeslot
            timeslot = Timeslot(day=0, start_time=time(9, 0), end_time=time(10, 0))
            session.add(timeslot)
            
            session.commit()
            
            print("✓ Sample data inserted successfully")
            print(f"  - Faculty: {faculty.name} (ID: {faculty.id})")
            print(f"  - Course: {course.code} (ID: {course.id})")
            print(f"  - Room: {room.name} (ID: {room.id})")
            print(f"  - Timeslot: Day {timeslot.day}, {timeslot.start_time}-{timeslot.end_time} (ID: {timeslot.id})")
            
    except Exception as e:
        print(f"❌ Failed to insert data: {e}")
        sys.exit(1)
    
    # Test data retrieval
    print("\n6. Testing data retrieval...")
    try:
        with Session(engine) as session:
            faculty_count = session.query(Faculty).count()
            course_count = session.query(Course).count()
            room_count = session.query(Room).count()
            timeslot_count = session.query(Timeslot).count()
            
            print(f"✓ Data retrieved successfully:")
            print(f"  - Faculty: {faculty_count} record(s)")
            print(f"  - Courses: {course_count} record(s)")
            print(f"  - Rooms: {room_count} record(s)")
            print(f"  - Timeslots: {timeslot_count} record(s)")
            
    except Exception as e:
        print(f"❌ Failed to retrieve data: {e}")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED - Database is ready for production!")
    print("=" * 60)

if __name__ == "__main__":
    test_database_connection()
