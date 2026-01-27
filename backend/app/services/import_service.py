from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models import Faculty, Course, Room, Section
from app.services.validator import ValidationResult
from app.services.data_integrity_verifier import DataIntegrityVerifier
from app.services.normalization_verifier import NormalizationVerifier

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
        """Imports faculty, unifying by code (faculty_id or code)."""
        count = 0
        logs = []
        for item in items:
            # Support 'id', 'faculty_id', or 'code' columns
            raw_id = item.get("id") or item.get("faculty_id") or item.get("code", "")
            raw_name = item.get("name", "")
            raw_email = item.get("email", "")

            clean_code = self.normalize_text(raw_id, uppercase=True)
            clean_name = self.normalize_text(raw_name)
            clean_email = self.normalize_text(raw_email) if raw_email else None

            if not clean_code:
                logs.append(f"[Error] Faculty skipped: Missing code for '{clean_name}'")
                continue

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
                new_f = Faculty(code=clean_code, name=clean_name, email=clean_email)
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
            # Handle both 'code' (data_templates) and 'course_id' (rawData) column names
            raw_id = item.get("code") or item.get("course_id", "")
            raw_name = item.get("name", "")
            raw_type = item.get("type", "LECTURE")
            # Handle both 'credits' (data_templates) and 'weekly_periods' (rawData) column names
            try:
                raw_credits = int(item.get("credits") or item.get("weekly_periods", 3))
            except:
                raw_credits = 3
            raw_room_req = item.get("needs_room_type", raw_type)
            
            clean_code = self.normalize_text(raw_id, uppercase=True)
            clean_name = self.normalize_text(raw_name)
            
            if mock:
                logs.append(f"[Mock Course] '{clean_name}' (ID: {clean_code}, Credits: {raw_credits})")
                count += 1
                continue

            existing = self.db.execute(select(Course).where(Course.code == clean_code)).scalar_one_or_none()
            
            if existing:
                existing.name = clean_name
                existing.type = raw_type
                existing.credits = raw_credits
                existing.needs_room_type = raw_room_req
            else:
                new_c = Course(
                    code=clean_code, 
                    name=clean_name,
                    type=raw_type,
                    credits=raw_credits,
                    needs_room_type=raw_room_req
                )
                self.db.add(new_c)
                count += 1
        
        if not mock:
            self.db.commit()
        return count, logs

    def process_rooms(self, items: List[Dict[str, Any]], mock: bool = False) -> Tuple[int, List[str]]:
        """Imports rooms, unifying by room_id or code."""
        count = 0
        logs = []
        for item in items:
            raw_id = item.get("room_id") or item.get("code", "")
            raw_block = item.get("block", "")
            raw_no = item.get("room_no", "")
            try:
                raw_cap = int(item.get("capacity", 30))
            except:
                raw_cap = 30
            raw_type = item.get("room_type") or item.get("type", "LECTURE")

            clean_code = self.normalize_text(raw_id, uppercase=True)

            if not clean_code:
                logs.append(f"[Error] Room skipped: Missing code")
                continue

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
            # Support 'id', 'section_id', or 'code' columns
            raw_id = item.get("id") or item.get("section_id") or item.get("code", "")
            raw_name = item.get("name") or item.get("section_name", raw_id)
            raw_dept = item.get("dept", "")
            raw_prog = item.get("program", "")
            try:
                raw_year = int(item.get("year", 1))
            except:
                raw_year = 1
            raw_sem = item.get("sem", "")
            raw_shift = item.get("shift", "SHIFT_8_4")
            try:
                raw_count = int(item.get("student_count", 0))
            except:
                raw_count = 0

            clean_code = self.normalize_text(raw_id, uppercase=True)

            if not clean_code:
                logs.append(f"[Error] Section skipped: Missing code")
                continue

            if mock:
                logs.append(f"[Mock Section] '{clean_code}' (Shift: {raw_shift})")
                count += 1
                continue

            existing = self.db.execute(select(Section).where(Section.code == clean_code)).scalar_one_or_none()

            if existing:
                existing.name = raw_name
                existing.student_count = raw_count
                existing.shift = raw_shift
                existing.year = raw_year
                existing.sem = raw_sem
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

    def validate_room_capacities(self) -> Tuple[bool, List[str]]:
        sections = self.db.execute(select(Section)).scalars().all()
        rooms = self.db.execute(select(Room)).scalars().all()
        logs = []
        violations = []
        
        for section in sections:
            matching_rooms = [r for r in rooms if section.student_count <= r.capacity]
            if not matching_rooms:
                violation = f"Section {section.code} ({section.student_count} students) - No room with sufficient capacity"
                violations.append(violation)
                logs.append(f"[FAIL] {violation}")
        
        return len(violations) == 0, logs

    def process_assignments(self, items: List[Dict[str, Any]], mock: bool = False) -> Tuple[int, List[str]]:
        """Imports faculty assignments (Faculty-Course-Section map)."""
        count = 0
        logs = []

        if mock:
            return len(items), [f"[Mock Assignment] Processed {len(items)} mappings"]

        from app.models import Assignment

        fac_email_map = {f.email: f.id for f in self.db.execute(select(Faculty)).scalars().all() if f.email}
        fac_code_map = {f.code: f.id for f in self.db.execute(select(Faculty)).scalars().all()}
        course_map = {c.code: c.id for c in self.db.execute(select(Course)).scalars().all()}
        sec_map = {s.code: s.id for s in self.db.execute(select(Section)).scalars().all()}

        for item in items:
            f_email = item.get("faculty_email", "")
            f_code = item.get("faculty_id") or item.get("faculty_code", "")

            fac_id = None
            if f_email:
                f_email = self.normalize_text(f_email)
                fac_id = fac_email_map.get(f_email)
            if not fac_id and f_code:
                f_code = self.normalize_text(f_code, uppercase=True)
                fac_id = fac_code_map.get(f_code)

            # Get course code and section code
            s_code = item.get("section_id") or item.get("section", "")
            c_code = item.get("course_id") or item.get("course_code", "")

            s_code = self.normalize_text(s_code, uppercase=True)
            c_code = self.normalize_text(c_code, uppercase=True)

            if not fac_id:
                logs.append(f"[Error] Assignment skipped: Unknown faculty (Email:{f_email}, Code:{f_code})")
                continue

            if s_code not in sec_map:
                logs.append(f"[Error] Assignment skipped: Unknown section '{s_code}'")
                continue

            if c_code not in course_map:
                logs.append(f"[Error] Assignment skipped: Unknown course '{c_code}'")
                continue

            existing_list = self.db.execute(
                select(Assignment).where(
                    Assignment.faculty_id == fac_id,
                    Assignment.course_id == course_map[c_code],
                    Assignment.section_id == sec_map[s_code]
                )
            ).scalars().all()

            if not existing_list:
                new_assign = Assignment(
                    faculty_id=fac_id,
                    course_id=course_map[c_code],
                    section_id=sec_map[s_code]
                )
                self.db.add(new_assign)
                count += 1
            elif len(existing_list) > 1:
                logs.append(f"[Warning] Removing {len(existing_list)-1} duplicate assignments for {f_code}-{c_code}-{s_code}")
                for dup in existing_list[1:]:
                    self.db.delete(dup)

        self.db.commit()
    
    def verify_imported_data(self) -> Dict[str, Any]:
        verifier = DataIntegrityVerifier()
        
        faculty_data = [{"id": f.id, "name": f.name, "email": f.email} for f in self.db.query(Faculty).all()]
        course_data = [{"code": c.code, "name": c.name, "credits": c.weekly_periods} for c in self.db.query(Course).all()]
        room_data = [{"room_id": r.id, "capacity": r.capacity} for r in self.db.query(Room).all()]
        section_data = [{"id": s.id, "student_count": s.student_count} for s in self.db.query(Section).all()]
        
        data = {
            "faculty": faculty_data,
            "courses": course_data,
            "rooms": room_data,
            "sections": section_data,
            "faculty_course_map": []
        }
        
        integrity_report = verifier.verify_all(data)
        return {
            "is_healthy": integrity_report.is_healthy,
            "score": integrity_report.overall_score,
            "issues": integrity_report.issues,
            "summary": integrity_report.summary
        }
        return count, logs
