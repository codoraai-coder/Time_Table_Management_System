import sys
import os
import unittest
from typing import List

# Add backend to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../.."))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "backend"))

from app.services.solver import SolverRoom, SolverTimeslot
from app.services.repair_engine import RepairEngine, RepairResult

class TestRepairEngine(unittest.TestCase):
    def setUp(self):
        self.repair_engine = RepairEngine()
        
        # Setup basic data
        self.rooms = [
            SolverRoom(id=1, name="R1", type="Lecture", capacity=40),
            SolverRoom(id=2, name="R2", type="Lecture", capacity=40)
        ]
        self.timeslots = [
            SolverTimeslot(id=1, day=0, start_time="09:00", end_time="10:00"),
            SolverTimeslot(id=2, day=0, start_time="10:00", end_time="11:00")
        ]

    def test_basic_repair_move_one(self):
        """Test moving one assignment due to conflict, while keeping others stable"""
        print("\nRunning test_basic_repair_move_one...")
        
        # Current State:
        # A1: Room 1, Slot 1 (Problem! Maybe room is now blocked)
        # A2: Room 1, Slot 2 (Locked, should stay)
        
        current_assignments = [
            {
                "id": 101, "section_id": 1, "name": "A1", "course_id": 10, "faculty_id": 10,
                "room_type_required": "Lecture", "allowed_slot_ids": [1, 2],
                "room_id": 1, "timeslot_id": 1, "student_count": 20
            },
            {
                "id": 102, "section_id": 2, "name": "A2", "course_id": 11, "faculty_id": 11,
                "room_type_required": "Lecture", "allowed_slot_ids": [1, 2],
                "room_id": 1, "timeslot_id": 2, "student_count": 20
            }
        ]
        
        # We say A1 is a problem (must move). A2 is locked (must stay).
        problem_ids = [101]
        locked_ids = [102]
        
        # In this setup, A1 is at R1,S1.
        # It is forbidden from R1,S1.
        # R1,S2 is taken by A2 (and A2 is locked).
        # So A1 MUST move to R2,S1 or R2,S2 or R1,S2 (blocked) -> R2,S1 is best candidate?
        # Actually R2,S1 is free. R2,S2 is free.
        
        result = self.repair_engine.repair_schedule(
            current_assignments=current_assignments,
            problem_assignment_ids=problem_ids,
            locked_assignment_ids=locked_ids,
            rooms=self.rooms,
            timeslots=self.timeslots
        )
        
        self.assertTrue(result.success)
        
        # Verify A2 stayed put
        new_a2 = next(x for x in result.final_assignments if x["section_id"] == 102)
        self.assertEqual(new_a2["room_id"], 1)
        self.assertEqual(new_a2["timeslot_id"], 2)
        
        # Verify A1 moved
        new_a1 = next(x for x in result.final_assignments if x["section_id"] == 101)
        self.assertNotEqual((new_a1["room_id"], new_a1["timeslot_id"]), (1, 1))
        
        print("[OK] Repair successful: A1 moved, A2 stayed.")

    def test_repair_impossible(self):
        """Test that repair fails gracefully if no Move is possible"""
        print("\nRunning test_repair_impossible...")
        
        # Only 1 slot exists. 1 Room.
        # A1 is there. We say "Move A1". No other place to go.
        
        rooms = [SolverRoom(id=1, name="R1", type="Lecture", capacity=40)]
        slots = [SolverTimeslot(id=1, day=0, start_time="09:00", end_time="10:00")]
        
        current_assignments = [
            {
                "id": 101, "section_id": 1, "name": "A1", "course_id": 10, "faculty_id": 10,
                "room_type_required": "Lecture", "allowed_slot_ids": [1],
                "room_id": 1, "timeslot_id": 1, "student_count": 20
            }
        ]
        
        problem_ids = [101]
        locked_ids = []
        
        result = self.repair_engine.repair_schedule(
            current_assignments, problem_ids, locked_ids, rooms, slots
        )
        
        self.assertFalse(result.success)
        self.assertIn("Repair Failed", result.message)
        print("[OK] Impossible repair handled correctly.")

if __name__ == '__main__':
    unittest.main()
