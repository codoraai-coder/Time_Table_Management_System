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
            
            clean_code = self.normalize_text(raw_code, uppercase=True)
            clean_name = self.normalize_text(raw_name)
            
            if mock:
                logs.append(f"[Mock Course] '{raw_name}' normalized to '{clean_name}' (Code: {clean_code})")
                count += 1
                continue

            # Entity Resolution by Code
            existing = self.db.execute(select(Course).where(Course.code == clean_code)).scalar_one_or_none()
            
            if existing:
                if existing.name != clean_name:
                    logs.append(f"[Course] Unified '{clean_name}' into existing '{existing.name}' (Code: {clean_code})")
            else:
                new_c = Course(code=clean_code, name=clean_name)
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
            
            clean_name = self.normalize_text(raw_id, uppercase=True)
            clean_course = self.normalize_text(raw_course, uppercase=True)
            
            if mock:
                logs.append(f"[Mock Section] '{raw_id}' linked to Course '{clean_course}'")
                count += 1
                continue

            c_id = course_map.get(clean_course)
            if not c_id:
                continue # Should be caught by validator
                
            existing = self.db.execute(select(Section).where(Section.name == clean_name)).scalar_one_or_none()
            
            if existing:
                existing.course_id = c_id
            else:
                new_s = Section(name=clean_name, course_id=c_id)
                self.db.add(new_s)
                count += 1
        
        if not mock:
            self.db.commit()
        return count, logs
