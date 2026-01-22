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
        """Imports faculty, unifying by code (faculty_id)."""
        count = 0
        logs = []
        for item in items:
            raw_id = item.get("faculty_id", "")
            raw_name = item.get("name", "")
            
            clean_code = self.normalize_text(raw_id, uppercase=True)
            clean_name = self.normalize_text(raw_name)
            
            if mock:
                logs.append(f"[Mock Faculty] '{clean_name}' (ID: {clean_code})")
                count += 1
                continue

            existing = self.db.execute(select(Faculty).where(Faculty.code == clean_code)).scalar_one_or_none()
            
            if existing:
                if existing.name != clean_name:
                    logs.append(f"[Faculty] Updated name for '{clean_code}' from '{existing.name}' to '{clean_name}'")
                    existing.name = clean_name
            else:
                new_f = Faculty(code=clean_code, name=clean_name)
                self.db.add(new_f)
                count += 1
        
        if not mock:
            self.db.commit()
        return count, logs

    def process_courses(self, items: List[Dict[str, Any]], mock: bool = False) -> Tuple[int, List[str]]:
        """Imports courses, unifying by course_id."""
        count = 0
        logs = []
        for item in items:
            raw_id = item.get("course_id", "")
            raw_name = item.get("name", "")
            raw_type = item.get("type", "LECTURE")
            try:
                raw_periods = int(item.get("weekly_periods", 3))
            except:
                raw_periods = 3
            raw_room_req = item.get("needs_room_type", "LECTURE")
            
            clean_code = self.normalize_text(raw_id, uppercase=True)
            clean_name = self.normalize_text(raw_name)
            
            if mock:
                logs.append(f"[Mock Course] '{clean_name}' (ID: {clean_code})")
                count += 1
                continue

            existing = self.db.execute(select(Course).where(Course.code == clean_code)).scalar_one_or_none()
            
            if existing:
                existing.name = clean_name
                existing.type = raw_type
                existing.weekly_periods = raw_periods
                existing.needs_room_type = raw_room_req
            else:
                new_c = Course(
                    code=clean_code, 
                    name=clean_name,
                    type=raw_type,
                    weekly_periods=raw_periods,
                    needs_room_type=raw_room_req
                )
                self.db.add(new_c)
                count += 1
        
        if not mock:
            self.db.commit()
        return count, logs

    def process_rooms(self, items: List[Dict[str, Any]], mock: bool = False) -> Tuple[int, List[str]]:
        """Imports rooms, unifying by room_id."""
        count = 0
        logs = []
        for item in items:
            raw_id = item.get("room_id", "")
            raw_block = item.get("block", "")
            raw_no = item.get("room_no", "")
            try:
                raw_cap = int(item.get("capacity", 30))
            except:
                raw_cap = 30
            raw_type = item.get("room_type", "LECTURE")
            
            clean_code = self.normalize_text(raw_id, uppercase=True)
            
            if mock:
                logs.append(f"[Mock Room] '{clean_code}' (Cap: {raw_cap})")
                count += 1
                continue

            existing = self.db.execute(select(Room).where(Room.code == clean_code)).scalar_one_or_none()
            
            if existing:
                existing.type = raw_type
                existing.capacity = raw_cap
                existing.block = raw_block
                existing.room_no = raw_no
            else:
                new_r = Room(
                    code=clean_code, 
                    capacity=raw_cap, 
                    type=raw_type,
                    block=raw_block,
                    room_no=raw_no
                )
                self.db.add(new_r)
                count += 1
        
        if not mock:
            self.db.commit()
        return count, logs

    def process_sections(self, items: List[Dict[str, Any]], mock: bool = False) -> Tuple[int, List[str]]:
        """Imports sections."""
        count = 0
        logs = []
        
        for item in items:
            raw_id = item.get("section_id", "")
            raw_name = item.get("section_name", "")
            raw_dept = item.get("dept", "")
            raw_prog = item.get("program", "")
            try:
                raw_year = int(item.get("year", 1))
            except:
                raw_year = 1
            raw_sem = item.get("sem", "")
            raw_shift = item.get("shift", "")
            try:
                raw_count = int(item.get("student_count", 0))
            except:
                raw_count = 0
            
            clean_code = self.normalize_text(raw_id, uppercase=True)
            
            if mock:
                logs.append(f"[Mock Section] '{clean_code}'")
                count += 1
                continue

            existing = self.db.execute(select(Section).where(Section.code == clean_code)).scalar_one_or_none()
            
            if existing:
                existing.student_count = raw_count
                existing.shift = raw_shift
            else:
                new_s = Section(
                    code=clean_code,
                    name=raw_name,
                    dept=raw_dept,
                    program=raw_prog,
                    year=raw_year,
                    sem=raw_sem,
                    shift=raw_shift,
                    student_count=raw_count
                )
                self.db.add(new_s)
                count += 1
        
        if not mock:
            self.db.commit()
        return count, logs
    
    def process_assignments(self, items: List[Dict[str, Any]], mock: bool = False) -> Tuple[int, List[str]]:
        """Imports faculty assignments (Faculty-Course-Section map)."""
        count = 0
        logs = []
        
        if mock:
            return len(items), [f"[Mock Assignment] Processed {len(items)} mappings"]

        from app.models import Assignment

        # Pre-cache IDs
        fac_map = {f.code: f.id for f in self.db.execute(select(Faculty)).scalars().all()}
        course_map = {c.code: c.id for c in self.db.execute(select(Course)).scalars().all()}
        sec_map = {s.code: s.id for s in self.db.execute(select(Section)).scalars().all()}

        for item in items:
            f_code = self.normalize_text(item.get("faculty_id"), uppercase=True)
            c_code = self.normalize_text(item.get("course_id"), uppercase=True)
            s_code = self.normalize_text(item.get("section_id"), uppercase=True)
            
            if f_code not in fac_map or c_code not in course_map or s_code not in sec_map:
                logs.append(f"[Error] Assignment skipped: Unknown entity (F:{f_code}, C:{c_code}, S:{s_code})")
                continue
            
            # Check duplicates?
            # ideally we just insert.
            new_assign = Assignment(
                faculty_id=fac_map[f_code],
                course_id=course_map[c_code],
                section_id=sec_map[s_code],
                room_id=None, # To be solved
                timeslot_id=None # To be solved
            )
            self.db.add(new_assign)
            count += 1
            
        self.db.commit()
        return count, logs
