from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models import Faculty, Course, Room, Section
from app.services.validator import ValidationResult

class ImportService:
    """
    Normalization Layer: Cleans data and maps external entities to internal DB IDs.
    """
    def __init__(self, db: Session):
        self.db = db

    def normalize_text(self, text: Any, uppercase: bool = False) -> str:
        """Trims whitespace and handles casing."""
        if text is None:
            return ""
        cleaned = str(text).strip()
        return cleaned.upper() if uppercase else cleaned

    def process_faculty(self, items: List[Dict[str, Any]], mock: bool = False) -> Tuple[int, List[str]]:
        """Imports faculty, unifying by email."""
        count = 0
        logs = []
        for item in items:
            raw_name = item.get("name", "")
            raw_email = item.get("email", "")
            
            clean_email = self.normalize_text(raw_email, uppercase=True)
            clean_name = self.normalize_text(raw_name)
            
            if mock:
                logs.append(f"[Mock Faculty] '{raw_name}' normalized to '{clean_name}' (Email: {clean_email})")
                count += 1
                continue

            # Entity Resolution by Email
            existing = self.db.execute(select(Faculty).where(Faculty.email == clean_email)).scalar_one_or_none()
            
            if existing:
                if existing.name != clean_name:
                    logs.append(f"[Faculty] Unified '{clean_name}' into existing '{existing.name}' (Email: {clean_email})")
            else:
                new_f = Faculty(name=clean_name, email=clean_email)
                self.db.add(new_f)
                count += 1
        
        if not mock:
            self.db.commit()
        return count, logs

    def process_courses(self, items: List[Dict[str, Any]], mock: bool = False) -> Tuple[int, List[str]]:
        """Imports courses, unifying by code."""
        count = 0
        logs = []
        for item in items:
            raw_code = item.get("code", "")
            raw_name = item.get("name", "")
            raw_credits = item.get("credits", 3)
            
            clean_code = self.normalize_text(raw_code, uppercase=True)
            clean_name = self.normalize_text(raw_name)
            
            if mock:
                logs.append(f"[Mock Course] '{raw_name}' normalized to '{clean_name}' (Code: {clean_code}, Credits: {raw_credits})")
                count += 1
                continue

            # Entity Resolution by Code
            existing = self.db.execute(select(Course).where(Course.code == clean_code)).scalar_one_or_none()
            
            if existing:
                if existing.name != clean_name:
                    logs.append(f"[Course] Unified '{clean_name}' into existing '{existing.name}' (Code: {clean_code})")
                existing.credits = int(raw_credits)
            else:
                new_c = Course(code=clean_code, name=clean_name, credits=int(raw_credits))
                self.db.add(new_c)
                count += 1
        
        if not mock:
            self.db.commit()
        return count, logs

    def process_rooms(self, items: List[Dict[str, Any]], mock: bool = False) -> Tuple[int, List[str]]:
        """Imports rooms, unifying by name."""
        count = 0
        logs = []
        for item in items:
            raw_name = item.get("name", "")
            raw_type = item.get("type", "Lecture")
            
            clean_name = self.normalize_text(raw_name, uppercase=True)
            clean_type = self.normalize_text(raw_type)
            
            if mock:
                logs.append(f"[Mock Room] '{raw_name}' normalized to '{clean_name}' (Type: {clean_type})")
                count += 1
                continue

            existing = self.db.execute(select(Room).where(Room.name == clean_name)).scalar_one_or_none()
            
            if existing:
                if existing.type != clean_type:
                    logs.append(f"[Room] Updated type for '{clean_name}' to '{clean_type}'")
                    existing.type = clean_type
            else:
                new_r = Room(name=clean_name, type=clean_type)
                self.db.add(new_r)
                count += 1
        
        if not mock:
            self.db.commit()
        return count, logs

    def process_sections(self, items: List[Dict[str, Any]], mock: bool = False) -> Tuple[int, List[str]]:
        """Imports sections, linking to internal Course IDs."""
        count = 0
        logs = []
        
        # Pre-cache Course IDs for mapping
        if not mock:
            courses = self.db.execute(select(Course)).scalars().all()
            course_map = {c.code: c.id for c in courses}
        else:
            course_map = {} # Empty for mock
        
        for item in items:
            raw_id = item.get("id", "")
            raw_course = item.get("course_code", "")
            raw_count = item.get("student_count", 0)
            raw_room_type = item.get("room_type", "Lecture")
            raw_shift = item.get("shift", "SHIFT_8_4")
            
            # Suffix Cleaning: e.g. "CSE_2A-DBMS" -> "CSE_2A"
            if "-" in str(raw_id):
                raw_id = str(raw_id).split("-")[0]

            clean_name = self.normalize_text(raw_id, uppercase=True)
            clean_course = self.normalize_text(raw_course, uppercase=True)
            clean_room_type = self.normalize_text(raw_room_type)
            clean_shift = self.normalize_text(raw_shift, uppercase=True)
            
            if mock:
                logs.append(f"[Mock Section] '{raw_id}' linked to Course '{clean_course}' (Room: {clean_room_type}, Shift: {clean_shift})")
                count += 1
                continue

            c_id = course_map.get(clean_course)
            if not c_id:
                logs.append(f"[Error] Course code '{clean_course}' not found for section '{clean_name}'")
                continue 
                
            # Composite Uniqueness: (name, course_id)
            # This allows the SAME section name (e.g. CSE_2A) to have MULTIPLE courses.
            existing = self.db.execute(
                select(Section).where(Section.name == clean_name, Section.course_id == c_id)
            ).scalar_one_or_none()
            
            if existing:
                existing.student_count = int(raw_count)
                existing.room_type = clean_room_type
                existing.shift = clean_shift
            else:
                new_s = Section(
                    name=clean_name, 
                    course_id=c_id, 
                    student_count=int(raw_count), 
                    room_type=clean_room_type,
                    shift=clean_shift
                )
                self.db.add(new_s)
                count += 1
        
        if not mock:
            self.db.commit()
        return count, logs

    def process_faculty_mapping(self, items: List[Dict[str, Any]], mock: bool = False) -> Tuple[int, List[str]]:
        """Links faculty to sections based on mapping CSV."""
        count = 0
        logs = []
        
        if not mock:
            faculty_list = self.db.execute(select(Faculty)).scalars().all()
            faculty_map = {f.email.upper(): f.id for f in faculty_list}
            
            # Since sections are now (name, course_id), we need to handle the mapping carefully.
            # Usually, the mapping CSV provides section_id (which might have a suffix).
            # We match by clean name AND course_id if possible, or just clean name if unique.
            sections = self.db.execute(select(Section)).scalars().all()
            
        for item in items:
            raw_email = item.get("faculty_email", "")
            raw_section = item.get("section_id", "")
            raw_course = item.get("course_id", "") # Optional but helpful
            
            # Suffix Cleaning
            if "-" in str(raw_section):
                raw_section = str(raw_section).split("-")[0]

            clean_email = self.normalize_text(raw_email, uppercase=True)
            clean_section = self.normalize_text(raw_section, uppercase=True)
            clean_course = self.normalize_text(raw_course, uppercase=True)
            
            if mock:
                logs.append(f"[Mock Map] Linked Faculty {clean_email} to Section {clean_section}")
                count += 1
                continue
            
            f_id = faculty_map.get(clean_email)
            if not f_id:
                logs.append(f"[Warning] Faculty email '{clean_email}' not found.")
                continue

            # Find the specific section(s) to assign this faculty to
            # If course_id is provided in mapping, use it. Otherwise, match all sections with this name?
            # Usually, one faculty per subject-section.
            target_sections = [
                s for s in sections 
                if s.name == clean_section and (not clean_course or s.course.code == clean_course)
            ]
            
            if target_sections:
                for s in target_sections:
                    s.faculty_id = f_id
                    count += 1
            else:
                logs.append(f"[Warning] No section found for Mapping: {clean_section} (Course: {clean_course})")
                
        if not mock:
            self.db.commit()
        return count, logs
