import unittest
import sys
import os

# Robust path setup
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../.."))
if os.path.basename(project_root) == "backend":
    project_root = os.path.abspath(os.path.join(project_root, ".."))

sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "backend"))

try:
    from app.services.validator import ValidatorService
except ImportError:
    from backend.app.services.validator import ValidatorService

class TestValidator(unittest.TestCase):
    def setUp(self):
        self.validator = ValidatorService()
        self.valid_data = {
            "faculty": [{"faculty_id": "F001", "name": "Dr. A"}],
            "courses": [{"course_id": "CS101", "name": "Intro", "type": "LECTURE", "weekly_periods": 3, "needs_room_type": "LECTURE"}],
            "rooms": [{"room_id": "R1", "capacity": 30, "room_type": "LECTURE"}],
            "sections": [{"section_id": "S1", "dept": "CSE", "program": "B.Tech", "year": 1, "sem": "Even", "shift": "MORN", "student_count": 30, "section_name": "A"}],
            "faculty_course_map": [{"faculty_id": "F001", "course_id": "CS101", "section_id": "S1"}]
        }

    def test_valid_data(self):
        result = self.validator.validate_structure(self.valid_data)
        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.errors), 0)

    def test_missing_column(self):
        bad_data = self.valid_data.copy()
        bad_data["faculty"] = [{"faculty_id": "F001"}] # Missing name
        result = self.validator.validate_structure(bad_data)
        self.assertFalse(result.is_valid)
        self.assertIn("missing mandatory column: 'name'", result.errors[0])

    def test_broken_reference_course(self):
        bad_data = self.valid_data.copy()
        # Mapping refers to unknown course
        bad_data["faculty_course_map"] = [{"faculty_id": "F001", "course_id": "NONEXISTENT", "section_id": "S1"}]
        result = self.validator.validate_structure(bad_data)
        self.assertFalse(result.is_valid)
        self.assertIn("unknown course ID", result.errors[0])

    def test_impossible_room_type(self):
        bad_data = self.valid_data.copy()
        # Course requires LAB but no LAB rooms
        bad_data["courses"][0]["needs_room_type"] = "LAB"
        # No 'LAB' rooms exist in self.valid_data
        result = self.validator.validate_structure(bad_data)
        self.assertTrue(result.is_valid) # It's a warning now
        self.assertIn("Course requires room type 'LAB'", result.warnings[0])

    def test_orphan_section_warning(self):
        bad_data = self.valid_data.copy()
        bad_data["faculty_course_map"] = [] # S1 is now orphan
        result = self.validator.validate_structure(bad_data)
        self.assertTrue(result.is_valid) # Warnings don't block
        self.assertTrue(any("has no courses assigned" in w for w in result.warnings))

if __name__ == "__main__":
    unittest.main()
