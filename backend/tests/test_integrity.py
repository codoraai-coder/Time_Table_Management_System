import sys
import os
import unittest

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../.."))
if os.path.basename(project_root) == "backend":
    project_root = os.path.abspath(os.path.join(project_root, ".."))

sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "backend"))

from app.services.data_integrity_verifier import DataIntegrityVerifier
from app.services.normalization_verifier import NormalizationVerifier

class TestDataIntegrityVerifier(unittest.TestCase):
    def setUp(self):
        self.verifier = DataIntegrityVerifier()
        self.valid_data = {
            "faculty": [
                {"id": "F001", "name": "Dr. Smith", "email": "smith@college.edu"},
                {"id": "F002", "name": "Prof. Jones", "email": "jones@college.edu"},
            ],
            "courses": [
                {"code": "CS101", "name": "Intro", "type": "LECTURE", "credits": 3},
                {"code": "CS102", "name": "OOP", "type": "LECTURE", "credits": 4},
            ],
            "rooms": [
                {"room_id": "R1", "capacity": 30, "room_type": "LECTURE"},
                {"room_id": "R2", "capacity": 20, "room_type": "LAB"},
            ],
            "sections": [
                {"id": "S1", "student_count": 30},
                {"id": "S2", "student_count": 25},
            ],
            "faculty_course_map": [
                {"faculty_id": "F001", "course_id": "CS101", "section_id": "S1"},
                {"faculty_id": "F002", "course_id": "CS102", "section_id": "S2"},
            ]
        }

    def test_valid_data(self):
        report = self.verifier.verify_all(self.valid_data)
        self.assertTrue(report.is_healthy)
        self.assertEqual(len(report.issues), 0)

    def test_duplicate_faculty(self):
        bad_data = self.valid_data.copy()
        bad_data["faculty"] = [
            {"id": "F001", "name": "Dr. Smith"},
            {"id": "F001", "name": "Smith, Dr."},
        ]
        report = self.verifier.verify_all(bad_data)
        self.assertEqual(report.metrics["faculty"].duplicates_count, 1)

    def test_empty_student_count(self):
        bad_data = self.valid_data.copy()
        bad_data["sections"] = [
            {"id": "S1", "student_count": 0},
            {"id": "S2", "student_count": 25},
        ]
        report = self.verifier.verify_all(bad_data)
        self.assertIn("S1", report.metrics["sections"].orphan_records)

    def test_invalid_credits(self):
        bad_data = self.valid_data.copy()
        bad_data["courses"] = [
            {"code": "CS101", "name": "Intro", "credits": 0},
        ]
        report = self.verifier.verify_all(bad_data)
        self.assertGreater(len(report.metrics["courses"].issues), 0)

    def test_broken_mapping_reference(self):
        bad_data = self.valid_data.copy()
        bad_data["faculty_course_map"] = [
            {"faculty_id": "UNKNOWN", "course_id": "CS101", "section_id": "S1"},
        ]
        report = self.verifier.verify_all(bad_data)
        self.assertGreater(len(report.metrics["mappings"].issues), 0)

    def test_health_score_calculation(self):
        report = self.verifier.verify_all(self.valid_data)
        self.assertGreaterEqual(report.overall_score, 80)

class TestNormalizationVerifier(unittest.TestCase):
    def setUp(self):
        self.verifier = NormalizationVerifier(faculty_threshold=80, course_threshold=75)
        self.valid_data = {
            "faculty": [
                {"id": "F001", "name": "Dr. Smith"},
                {"id": "F002", "name": "dr. smith"},
                {"id": "F003", "name": "Smith, Dr"},
                {"id": "F004", "name": "Prof. Jones"},
            ],
            "courses": [
                {"code": "CS101", "name": "Database"},
                {"code": "CS102", "name": "DBMS"},
            ]
        }

    def test_faculty_clustering(self):
        report = self.verifier.get_clustering_report(self.valid_data)
        self.assertGreater(len(report.faculty_clusters), 0)
        self.assertGreater(len(report.unmatched_faculty), 0)

    def test_course_clustering(self):
        report = self.verifier.get_clustering_report(self.valid_data)
        self.assertGreaterEqual(len(report.course_clusters) + len(report.unmatched_courses), 1)

    def test_clustering_confidence_in_range(self):
        report = self.verifier.get_clustering_report(self.valid_data)
        for cluster in report.faculty_clusters + report.course_clusters:
            self.assertGreaterEqual(cluster.confidence, 0.0)
            self.assertLessEqual(cluster.confidence, 1.0)

    def test_overall_confidence_calculation(self):
        report = self.verifier.get_clustering_report(self.valid_data)
        self.assertGreaterEqual(report.overall_confidence, 0.0)
        self.assertLessEqual(report.overall_confidence, 1.0)

if __name__ == '__main__':
    unittest.main()
