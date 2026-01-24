import sys
import os
import unittest

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../.."))
if os.path.basename(project_root) == "backend":
    project_root = os.path.abspath(os.path.join(project_root, ".."))

sys.path.insert(0, project_root)
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
            SolverSection(id=1, section_id=1, name="CS101-A", course_id=101, faculty_id=10, room_type_required="Lecture", required_periods=1, allowed_slot_ids=[1], student_count=30)
        ]
        rooms = [
            SolverRoom(id=1, name="Room 101", type="Lecture", capacity=40)
        ]
        timeslots = [
            SolverTimeslot(id=1, day=0, start_time="09:00", end_time="10:00")
        ]

        result = self.solver_service.solve(sections, rooms, timeslots)
        self.assertTrue(result.is_feasible)
        self.assertEqual(len(result.assignments), 1)
        print("✓ Feasible scenario passed")


    def test_faculty_conflict(self):
        """Test that a faculty cannot be in 2 places at once"""
        print("\nRunning test_faculty_conflict...")
        sections = [
            SolverSection(id=1, section_id=1, name="CS101-A", course_id=101, faculty_id=99, room_type_required="Lecture", required_periods=1, allowed_slot_ids=[1], student_count=30),
            SolverSection(id=2, section_id=2, name="CS101-B", course_id=101, faculty_id=99, room_type_required="Lecture", required_periods=1, allowed_slot_ids=[1], student_count=25)
        ]
        rooms = [
            SolverRoom(id=1, name="Room 1", type="Lecture", capacity=40),
            SolverRoom(id=2, name="Room 2", type="Lecture", capacity=40)
        ]
        timeslots = [
            SolverTimeslot(id=1, day=0, start_time="09:00", end_time="10:00")
        ]

        result = self.solver_service.solve(sections, rooms, timeslots)
        self.assertFalse(result.is_feasible)
        print("✓ Faculty conflict passed (Infeasible as expected)")

    def test_room_capacity_violation(self):
        """Test that solver fails if section > room capacity"""
        print("\nRunning test_room_capacity_violation...")
        sections = [
            SolverSection(id=1, section_id=1, name="CS101-A", course_id=101, faculty_id=10, room_type_required="Lecture", required_periods=1, allowed_slot_ids=[1], student_count=100)
        ]
        rooms = [
            SolverRoom(id=1, name="Small Room", type="Lecture", capacity=30)
        ]
        timeslots = [
            SolverTimeslot(id=1, day=0, start_time="09:00", end_time="10:00")
        ]

        result = self.solver_service.solve(sections, rooms, timeslots)
        self.assertFalse(result.is_feasible)
        self.assertIn("exceeds room", result.conflict_reason)
        print("✓ Room capacity violation passed")

    def test_determinism(self):
        """Test that same input gives identical output"""
        print("\nRunning test_determinism...")
        sections = [SolverSection(id=1, section_id=1, name="A", course_id=1, faculty_id=1, room_type_required="Lecture", required_periods=1, allowed_slot_ids=[1], student_count=30)]
        rooms = [
            SolverRoom(id=1, name="R1", type="Lecture", capacity=40),
            SolverRoom(id=2, name="R2", type="Lecture", capacity=40)
        ]
        timeslots = [SolverTimeslot(id=1, day=0, start_time="09:00", end_time="10:00")]

        result1 = self.solver_service.solve(sections, rooms, timeslots)
        result2 = self.solver_service.solve(sections, rooms, timeslots)

        self.assertEqual(result1.assignments, result2.assignments)
        print("✓ Determinism passed")

if __name__ == '__main__':
    unittest.main()
