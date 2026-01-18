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
            "faculty": [{"id": 1, "name": "Dr. A", "email": "a@uni.edu"}],
            "courses": [{"code": "CS101", "name": "Intro"}],
            "rooms": [{"name": "R1", "type": "Lecture"}],
            "sections": [{"id": "S1", "course_code": "CS101", "student_count": 30, "room_type": "Lecture"}],
            "faculty_course_map": [{"faculty_email": "a@uni.edu", "section_id": "S1"}]
        }

    def test_valid_data(self):
        result = self.validator.validate_structure(self.valid_data)
        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.errors), 0)

    def test_missing_column(self):
        bad_data = self.valid_data.copy()
        bad_data["faculty"] = [{"id": 1, "name": "Dr. A"}] # Missing email
        result = self.validator.validate_structure(bad_data)
        self.assertFalse(result.is_valid)
        self.assertIn("missing mandatory column: 'email'", result.errors[0])

    def test_broken_reference_course(self):
        bad_data = self.valid_data.copy()
        bad_data["sections"] = [{"id": "S1", "course_code": "NONEXISTENT", "student_count": 10, "room_type": "Lecture"}]
        result = self.validator.validate_structure(bad_data)
        self.assertFalse(result.is_valid)
        self.assertIn("unknown course code", result.errors[0])

    def test_impossible_room_type(self):
        bad_data = self.valid_data.copy()
        bad_data["sections"] = [{"id": "S1", "course_code": "CS101", "student_count": 10, "room_type": "Lab"}]
        # No 'Lab' rooms exist in self.valid_data
        result = self.validator.validate_structure(bad_data)
        self.assertFalse(result.is_valid)
        self.assertIn("Required room type 'Lab' is not available", result.errors[0])

    def test_orphan_section_warning(self):
        bad_data = self.valid_data.copy()
        bad_data["faculty_course_map"] = [] # S1 is now orphan
        result = self.validator.validate_structure(bad_data)
        self.assertTrue(result.is_valid) # Warnings don't block
        self.assertEqual(len(result.warnings), 2)
        self.assertTrue(any("has no faculty assigned" in w for w in result.warnings))

if __name__ == "__main__":
    unittest.main()
