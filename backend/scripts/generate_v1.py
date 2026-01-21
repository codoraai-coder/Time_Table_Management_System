import sys
import os

# Robust path setup
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../.."))
if os.path.basename(project_root) == "backend":
    project_root = os.path.abspath(os.path.join(project_root, ".."))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "backend"))

from dotenv import load_dotenv
load_dotenv()

from app.core.database import SessionLocal
from app.services.timetable_manager import TimetableManager
from app.models import Faculty, Course, Section, Room, Timeslot, Assignment, TimetableVersion
from datetime import time
from sqlalchemy import delete

def run():
    print("🚀 Starting Timetable Generation (V1)...")
    db = SessionLocal()
    try:
        # 1. Cleanup old data
        db.query(TimetableVersion).delete()
        db.query(Assignment).delete()
        db.query(Section).delete()
        db.query(Room).delete()
        db.query(Timeslot).delete()
        db.query(Course).delete()
        db.query(Faculty).delete()
        db.commit()
        print("✓ Cleaned up database")

        # 2. Add realistic sample data
        faculty = Faculty(name="Dr. Smith", email="smith@university.edu")
        course = Course(code="CS101", name="Intro to CS")
        db.add_all([faculty, course])
        db.flush()

        # 2 sections for the same course
        s1 = Section(name="CS101-Morning", student_count=30, course_id=course.id)
        s2 = Section(name="CS101-Afternoon", student_count=25, course_id=course.id)
        
        # 2 rooms 
        r1 = Room(name="Small Lab", type="Lecture")
        r2 = Room(name="Large Hall", type="Lecture")
        
        # 2 timeslots
        t1 = Timeslot(day=0, start_time=time(9, 0), end_time=time(10, 0)) # Mon 9am
        t2 = Timeslot(day=0, start_time=time(10, 0), end_time=time(11, 0)) # Mon 10am
        
        db.add_all([s1, s2, r1, r2, t1, t2])
        db.commit()
        print("✓ Realistic sample data created")

        # 3. Run the Manager
        manager = TimetableManager(db)
        version = manager.generate_timetable(version_number=1)

        if version:
            print(f"\n✨ SUCCESS! Timetable V1 Created.")
            print(f"Snapshot Data: {json.dumps(version.snapshot_data, indent=2)}")
        else:
            print("\n❌ Failed to generate version 1.")

    finally:
        db.close()

if __name__ == "__main__":
    import json
    run()
