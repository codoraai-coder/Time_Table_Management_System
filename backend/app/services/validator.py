from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import pydantic

@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[str]      # Fatal: Stops solver execution
    warnings: List[str]    # Non-fatal: Notified but execution continues
    suggestions: List[str] # Strategic advice

class ValidatorService:
    """
    Validates CSV/JSON input data before it reaches the Database or Solver.
    """
    
    # Maps entity to acceptable column name alternatives
    # Format: entity -> list of required column groups (each group has alternatives)
    # A valid file must have at least one column from each group
    REQUIRED_HEADERS = {
        "faculty": [["id", "faculty_id", "code"], ["name"]],  # email is optional (rawData doesn't have it)
        "courses": [["code", "course_id"], ["name"], ["credits", "weekly_periods"]],
        "rooms": [["room_id", "code"], ["capacity"], ["room_type", "type"]],
        "sections": [["id", "section_id", "code"], ["student_count"]],  # course_code and room_type are optional
        "faculty_course_map": [["faculty_email", "faculty_id", "faculty_code"], ["section_id", "code", "section"], ["course_id", "course_code"]]  # course_id is required in rawData format
    }

    def _find_column(self, row: Dict[str, Any], acceptable_names: List[str]) -> str:
        """
        Helper to find a column by any of its acceptable names.
        Returns the first matching column name or None.
        """
        for name in acceptable_names:
            if name in row:
                return name
        return None

    def validate_structure(self, data: Dict[str, List[Dict[str, Any]]]) -> ValidationResult:
        """
        Level 1 & 2: Structural and Referential Validation
        Accepts alternative column names from rawData files.
        """
        errors = []
        warnings = []
        suggestions = []

        # 1. Structural Checks (Headers with alternatives)
        for entity, header_groups in self.REQUIRED_HEADERS.items():
            if entity not in data:
                errors.append(f"Missing entity data: {entity}")
                continue
            
            items = data[entity]
            if not items:
                warnings.append(f"Entity '{entity}' data is empty.")
                continue

            # Check that each required header group has at least one match
            first_item = items[0]
            for header_group in header_groups:
                found = self._find_column(first_item, header_group)
                if not found:
                    errors.append(f"File '{entity}' is missing mandatory column (one of): {header_group}")

        if errors:
            return ValidationResult(False, errors, warnings, suggestions)

        # 2. Referential Integrity
        # Build lookup maps using actual column names found in data
        faculty_data = data.get("faculty", [])
        faculty_emails = set()
        faculty_ids = set()
        for f in faculty_data:
            email = self._find_column(f, ["email"])
            faculty_id = self._find_column(f, ["id", "faculty_id"])
            if email and email in f:
                faculty_emails.add(f[email])
            if faculty_id and faculty_id in f:
                faculty_ids.add(f[faculty_id])
        
        course_data = data.get("courses", [])
        course_codes = set()
        for c in course_data:
            code_col = self._find_column(c, ["code", "course_id"])
            if code_col and code_col in c:
                course_codes.add(c[code_col])
        
        section_data = data.get("sections", [])
        section_ids = set()
        for s in section_data:
            id_col = self._find_column(s, ["id", "section_id"])
            if id_col and id_col in s:
                section_ids.add(s[id_col])
        
        room_data = data.get("rooms", [])
        room_types = set()
        for r in room_data:
            type_col = self._find_column(r, ["room_type", "type"])
            if type_col and type_col in r:
                room_types.add(r[type_col])

        # Check mapping -> faculty, courses & sections
        for mapping in data.get("faculty_course_map", []):
            fac_col = self._find_column(mapping, ["faculty_email", "faculty_id"])
            sec_col = self._find_column(mapping, ["section_id"])
            
            if fac_col and fac_col in mapping:
                fac_val = mapping[fac_col]
                if fac_val not in faculty_emails and fac_val not in faculty_ids:
                    errors.append(f"Mapping refers to unknown faculty: '{fac_val}'")
            
            if sec_col and sec_col in mapping:
                sec_val = mapping[sec_col]
                if sec_val not in section_ids:
                    errors.append(f"Mapping refers to unknown section ID: '{sec_val}'")

        # 3. Logical/Capacity-Related Checks
        # Check for courses needing room types
        for c in course_data:
            needs_col = self._find_column(c, ["needs_room_type"])
            if needs_col and needs_col in c:
                needed_type = c[needs_col]
                if needed_type not in room_types:
                    warnings.append(f"Course requires room type '{needed_type}' but no such room exists.")

        # Orphan Sections (Warning)
        mapped_section_ids = set()
        for m in data.get("faculty_course_map", []):
            sec_col = self._find_column(m, ["section_id"])
            if sec_col and sec_col in m:
                mapped_section_ids.add(m[sec_col])
        
        for s_id in section_ids:
            if s_id not in mapped_section_ids:
                warnings.append(f"Section '{s_id}' has no courses assigned. It will not be scheduled.")

        # Suggestions
        if len(data.get("rooms", [])) < (len(data.get("sections", [])) / 5):
            suggestions.append("Low room-to-section ratio detected. Consider adding more rooms to avoid high competition.")

        return ValidationResult(len(errors) == 0, errors, warnings, suggestions)

    def validate_time_config(self, config: Dict[str, Any]) -> ValidationResult:
        """
        Validates the shifts and working days configuration.
        """
        errors = []
        if "shifts" not in config or not config["shifts"]:
            errors.append("Missing 'shifts' in time_config.json")
        else:
            for i, shift in enumerate(config["shifts"]):
                if "start" not in shift or "end" not in shift:
                    errors.append(f"Shift {i} is missing start/end times.")
                if "lunch" not in shift:
                    errors.append(f"Shift '{shift.get('name', i)}' is missing lunch break config.")

        if "working_days" not in config or not config["working_days"]:
            errors.append("No working days defined in time_config.json")

        return ValidationResult(len(errors) == 0, errors, [], [])
