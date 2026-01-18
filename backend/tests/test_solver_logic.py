import sys
import os
import unittest
from datetime import time

# Robust path setup (works from root or backend/)
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../.."))
# If we are inside backend/ already, root might be one level up
if os.path.basename(project_root) == "backend":
    project_root = os.path.abspath(os.path.join(project_root, ".."))

sys.path.insert(0, project_root)

# Also try to insert backend/ explicitly
sys.path.insert(0, os.path.join(project_root, "backend"))

try:
    from backend.app.services.solver import SolverService, SolverSection, SolverRoom, SolverTimeslot
except ImportError:
    from app.services.solver import SolverService, SolverSection, SolverRoom, SolverTimeslot

class TestSolverLogic(unittest.TestCase):
    def setUp(self):
        self.solver_service = SolverService()

    def test_feasible_scenario(self):
        """Test a simple scenario that should definitely work"""
        print("\nRunning test_feasible_scenario...")
        sections = [
            SolverSection(id=1, name="CS101-A", student_count=30, room_type_required="Lecture", course_id=101, faculty_id=10)
        ]
        rooms = [
            SolverRoom(id=1, name="Room 101", capacity=50, type="Lecture")
        ]
        timeslots = [
            SolverTimeslot(id=1, day=0, start_time="09:00", end_time="10:00")
        ]

        result = self.solver_service.solve(sections, rooms, timeslots)
        self.assertTrue(result.is_feasible)
        self.assertEqual(len(result.assignments), 1)
        print("✓ Feasible scenario passed")

    def test_capacity_constraint(self):
        """Test that solver respects room capacity"""
        print("\nRunning test_capacity_constraint...")
        sections = [
            SolverSection(id=1, name="CS101-Large", student_count=100, room_type_required="Lecture", course_id=101, faculty_id=10)
        ]
        rooms = [
            SolverRoom(id=1, name="Room Small", capacity=50, type="Lecture")
        ]
        timeslots = [
            SolverTimeslot(id=1, day=0, start_time="09:00", end_time="10:00")
        ]

        result = self.solver_service.solve(sections, rooms, timeslots)
        self.assertFalse(result.is_feasible)
        print("✓ Capacity constraint passed (Infeasible as expected)")

    def test_faculty_conflict(self):
        """Test that a faculty cannot be in 2 places at once"""
        print("\nRunning test_faculty_conflict...")
        # 2 Sections, Same Faculty, Only 1 Timeslot available
        sections = [
            SolverSection(id=1, name="CS101-A", student_count=30, room_type_required="Lecture", course_id=101, faculty_id=99),
            SolverSection(id=2, name="CS101-B", student_count=30, room_type_required="Lecture", course_id=101, faculty_id=99)
        ]
        rooms = [
            SolverRoom(id=1, name="Room 1", capacity=50, type="Lecture"),
            SolverRoom(id=2, name="Room 2", capacity=50, type="Lecture")
        ]
        timeslots = [
            SolverTimeslot(id=1, day=0, start_time="09:00", end_time="10:00")
        ]

        result = self.solver_service.solve(sections, rooms, timeslots)
        self.assertFalse(result.is_feasible)
        print("✓ Faculty conflict passed (Infeasible as expected)")

    def test_determinism(self):
        """Test that same input gives identical output"""
        print("\nRunning test_determinism...")
        # A slightly complex scenario where multiple valid solutions exist
        sections = [SolverSection(id=1, name="A", student_count=10, room_type_required="Lecture", course_id=1, faculty_id=1)]
        rooms = [
            SolverRoom(id=1, name="R1", capacity=20, type="Lecture"),
            SolverRoom(id=2, name="R2", capacity=20, type="Lecture")
        ]
        timeslots = [SolverTimeslot(id=1, day=0, start_time="09:00", end_time="10:00")]

        # Run 1
        result1 = self.solver_service.solve(sections, rooms, timeslots)
        # Run 2
        result2 = self.solver_service.solve(sections, rooms, timeslots)

        self.assertEqual(result1.assignments, result2.assignments)
        print("✓ Determinism passed")

if __name__ == '__main__':
    unittest.main()
