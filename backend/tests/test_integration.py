import unittest
import sys
import os
from datetime import time

# Path setup
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../.."))
if os.path.basename(project_root) == "backend":
    project_root = os.path.abspath(os.path.join(project_root, ".."))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "backend"))

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from app.models.base import Base
from app.models import Faculty, Course, Section, Room, Timeslot, Assignment, TimetableVersion
from app.services.timetable_manager import TimetableManager

load_dotenv()

class TestIntegration(unittest.TestCase):
    def setUp(self):
        # Connect to DB (using same DB as dev for now, in CI use test DB)
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            self.skipTest("DATABASE_URL not set")
            
        if database_url.startswith("postgresql://"):
            database_url = database_url.replace("postgresql://", "postgresql+psycopg://")
            
        self.engine = create_engine(database_url)
        self.session = Session(self.engine)
        
        # Cleanup
        self.cleanup()
        
    def tearDown(self):
        self.session.close()

    def cleanup(self):
        try:
            self.session.query(Assignment).delete()
            self.session.query(Section).delete()
            self.session.query(TimetableVersion).delete()
            self.session.query(Timeslot).delete()
            self.session.query(Room).delete()
            self.session.query(Course).delete()
            self.session.query(Faculty).delete()
            self.session.commit()
        except:
            self.session.rollback()

    def test_full_scheduling_flow(self):
        # 1. Setup Data
        f1 = Faculty(code="F1", name="Prof X")
        c1 = Course(code="CS101", name="Computing", type="LECTURE", needs_room_type="LECTURE")
        r1 = Room(code="R101", capacity=50, type="LECTURE")
        t1 = Timeslot(day=0, start_time=time(9,0), end_time=time(10,0))
        t2 = Timeslot(day=0, start_time=time(10,0), end_time=time(11,0))
        
        # Section model has no course_id FK
        s1 = Section(code="S1", name="A", student_count=20)

        self.session.add_all([f1, c1, r1, t1, t2, s1])
        self.session.commit() # Get IDs
        
        # Create Requirement (Assignment)
        # We need "CS101 Section A needs 3 periods" -> 3 assignments?
        # For simple test, 1 assignment.
        a1 = Assignment(
            faculty_id=f1.id,
            course_id=c1.id,
            section_id=s1.id,
            room_id=None,
            timeslot_id=None
        )
        self.session.add(a1)
        self.session.commit()
        
        print(f"\nCreated Assignment ID: {a1.id} (Unscheduled)")
        
        # 2. Run Solver
        manager = TimetableManager(self.session)
        version = manager.generate_timetable(version_number=101)
        
        # 3. Verify
        self.assertIsNotNone(version)
        self.assertEqual(version.snapshot_data["status"], "FEASIBLE")
        
        # Refresh assignment
        self.session.refresh(a1)
        print(f"Scheduled Assignment: Room {a1.room_id}, Slot {a1.timeslot_id}")
        
        self.assertIsNotNone(a1.room_id)
        self.assertIsNotNone(a1.timeslot_id)
        self.assertEqual(a1.room_id, r1.id)
        self.assertTrue(a1.timeslot_id in [t1.id, t2.id])

if __name__ == "__main__":
    unittest.main()
