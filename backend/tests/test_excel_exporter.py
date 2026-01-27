"""
Unit tests for ExcelExporterService.

Run with:
    pytest tests/test_excel_exporter.py -v
"""

import unittest
import tempfile
import os
from datetime import time

from app.core.database import SessionLocal, engine
from app.models import Base, TimetableVersion, Assignment, Course, Section, Faculty, Room, Timeslot
from app.services.excel_exporter import ExcelExporterService


class TestExcelExporter(unittest.TestCase):
    """Test cases for Excel export functionality."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test database."""
        Base.metadata.create_all(bind=engine)
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test database."""
        Base.metadata.drop_all(bind=engine)
    
    def setUp(self):
        """Set up test fixtures."""
        self.db = SessionLocal()
        self._create_test_data()
    
    def tearDown(self):
        """Clean up after tests."""
        self.db.query(Assignment).delete()
        self.db.query(TimetableVersion).delete()
        self.db.query(Course).delete()
        self.db.query(Section).delete()
        self.db.query(Faculty).delete()
        self.db.query(Room).delete()
        self.db.query(Timeslot).delete()
        self.db.commit()
        self.db.close()
    
    def _create_test_data(self):
        """Create minimal test data."""
        # Create faculty
        faculty = Faculty(id=1, code="FAC001", name="Dr. Smith", email="smith@college.edu")
        self.db.add(faculty)
        
        # Create rooms
        room = Room(id=1, code="AB101", capacity=60, room_type="LECTURE")
        self.db.add(room)
        
        # Create sections
        section = Section(id=1, code="CSE_2A", name="2A", student_count=60)
        self.db.add(section)
        
        # Create courses
        course_lecture = Course(id=1, code="DBMS", name="Database Management", type="LECTURE", credits=3)
        course_lab = Course(id=2, code="DBMS_LAB", name="Database Lab", type="LAB", credits=2)
        self.db.add(course_lecture)
        self.db.add(course_lab)
        
        # Create timeslots
        timeslot_1 = Timeslot(id=1, day=0, start_time=time(8, 0), end_time=time(9, 0))
        timeslot_2 = Timeslot(id=2, day=0, start_time=time(9, 0), end_time=time(10, 0))
        self.db.add(timeslot_1)
        self.db.add(timeslot_2)
        
        # Create timetable version
        version = TimetableVersion(id=1, version_number=1, status="FEASIBLE")
        self.db.add(version)
        
        self.db.commit()
        
        # Create assignments
        assignment_lecture = Assignment(
            id=1,
            course_id=1,
            section_id=1,
            faculty_id=1,
            room_id=1,
            timeslot_id=1,
            timetable_version_id=1
        )
        assignment_lab = Assignment(
            id=2,
            course_id=2,
            section_id=1,
            faculty_id=1,
            room_id=1,
            timeslot_id=2,
            timetable_version_id=1
        )
        self.db.add(assignment_lecture)
        self.db.add(assignment_lab)
        self.db.commit()
    
    def test_export_creates_file(self):
        """Test that export creates an Excel file."""
        exporter = ExcelExporterService(self.db)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "test_export.xlsx")
            result = exporter.export_timetable(version_id=1, output_path=output_path)
            
            self.assertTrue(os.path.exists(result))
            self.assertTrue(result.endswith(".xlsx"))
    
    def test_export_invalid_version(self):
        """Test that export raises error for invalid version ID."""
        exporter = ExcelExporterService(self.db)
        
        with self.assertRaises(ValueError):
            exporter.export_timetable(version_id=999)
    
    def test_grid_structure(self):
        """Test that grid structure is created correctly."""
        exporter = ExcelExporterService(self.db)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "test_grid.xlsx")
            exporter.export_timetable(version_id=1, output_path=output_path)
            
            # Verify workbook structure
            self.assertIsNotNone(exporter.workbook)
            self.assertIsNotNone(exporter.sheet)
            
            # Check headers
            self.assertEqual(exporter.sheet["A1"].value, "Day/Time")
            self.assertEqual(exporter.sheet["B1"].value, "Monday")
            self.assertEqual(exporter.sheet["F1"].value, "Friday")
    
    def test_time_slots_generated(self):
        """Test that time slots are generated correctly."""
        exporter = ExcelExporterService(self.db)
        slots = exporter._generate_time_slots()
        
        self.assertEqual(len(slots), 10)  # 8:00 to 18:00 = 10 slots
        self.assertEqual(slots[0], "8:00 - 9:00")
        self.assertEqual(slots[-1], "17:00 - 18:00")
    
    def test_timeslot_row_mapping(self):
        """Test timeslot to row mapping."""
        exporter = ExcelExporterService(self.db)
        
        # 8:00 should map to row 2 (row 1 is header)
        self.assertEqual(exporter._get_timeslot_row(time(8, 0)), 2)
        
        # 9:00 should map to row 3
        self.assertEqual(exporter._get_timeslot_row(time(9, 0)), 3)
        
        # 17:00 should map to row 11
        self.assertEqual(exporter._get_timeslot_row(time(17, 0)), 11)
    
    def test_day_column_mapping(self):
        """Test day to column mapping."""
        exporter = ExcelExporterService(self.db)
        
        # Monday (day 0) should map to column 2
        self.assertEqual(exporter._get_day_column(0), 2)
        
        # Friday (day 4) should map to column 6
        self.assertEqual(exporter._get_day_column(4), 6)
    
    def test_cell_content_format(self):
        """Test cell content formatting."""
        exporter = ExcelExporterService(self.db)
        
        course = self.db.query(Course).filter(Course.id == 1).first()
        section = self.db.query(Section).filter(Section.id == 1).first()
        
        content = exporter._format_cell_content(course, section)
        
        self.assertIn("DBMS", content)
        self.assertIn("2A", content)
        self.assertIn("\n", content)  # Should have line break


class TestExcelExporterEdgeCases(unittest.TestCase):
    """Test edge cases for Excel exporter."""
    
    def setUp(self):
        """Set up test database."""
        Base.metadata.create_all(bind=engine)
        self.db = SessionLocal()
    
    def tearDown(self):
        """Clean up."""
        Base.metadata.drop_all(bind=engine)
        self.db.close()
    
    def test_empty_timetable(self):
        """Test export with empty timetable (no assignments)."""
        # Create version without assignments
        version = TimetableVersion(id=1, version_number=1, status="FEASIBLE")
        self.db.add(version)
        self.db.commit()
        
        exporter = ExcelExporterService(self.db)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "test_empty.xlsx")
            result = exporter.export_timetable(version_id=1, output_path=output_path)
            
            # Should still create valid file
            self.assertTrue(os.path.exists(result))


if __name__ == "__main__":
    unittest.main()
