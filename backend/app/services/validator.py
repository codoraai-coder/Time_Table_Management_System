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
    
    REQUIRED_HEADERS = {
        "faculty": ["faculty_id", "name"],
        "courses": ["course_id", "name", "type", "weekly_periods"],
        "rooms": ["room_id", "capacity", "room_type"],
        "sections": ["section_id", "dept", "program", "year", "sem", "shift", "student_count"],
        "faculty_course_map": ["faculty_id", "course_id", "section_id"]
    }

    def validate_structure(self, data: Dict[str, List[Dict[str, Any]]]) -> ValidationResult:
        """
        Level 1 & 2: Structural and Referential Validation
        """
        errors = []
        warnings = []
        suggestions = []

        # 1. Structural Checks (Headers)
        for entity, expected_headers in self.REQUIRED_HEADERS.items():
            if entity not in data:
                errors.append(f"Missing entity data: {entity}")
                continue
            
            items = data[entity]
            if not items:
                warnings.append(f"Entity '{entity}' data is empty.")
                continue

            # Check headers of the first item
            first_item = items[0]
            for header in expected_headers:
                if header not in first_item:
                    errors.append(f"File '{entity}' is missing mandatory column: '{header}'")

        if errors:
            return ValidationResult(False, errors, warnings, suggestions)

        # 2. Referential Integrity
        faculty_ids = {f["faculty_id"] for f in data["faculty"]}
        course_ids = {c["course_id"] for c in data["courses"]}
        section_ids = {s["section_id"] for s in data["sections"]}
        room_types = {r["room_type"] for r in data["rooms"]}

        # Check mapping -> faculty, courses & sections
        for mapping in data["faculty_course_map"]:
            if mapping["faculty_id"] not in faculty_ids:
                errors.append(f"Mapping refers to unknown faculty ID: '{mapping['faculty_id']}'")
            if mapping["course_id"] not in course_ids:
                errors.append(f"Mapping refers to unknown course ID: '{mapping['course_id']}'")
            if mapping["section_id"] not in section_ids:
                errors.append(f"Mapping refers to unknown section ID: '{mapping['section_id']}'")

        # 3. Logical/Capacity-Related Checks
        # Validate that required room types behave correctly
        required_room_types = {c["needs_room_type"] for c in data["courses"]}
        for rt in required_room_types:
            if rt not in room_types:
                warnings.append(f"Course requires room type '{rt}' but no such room exists.")

        # Orphan Sections (Warning)
        mapped_section_ids = {m["section_id"] for m in data["faculty_course_map"]}
        for s_id in section_ids:
            if s_id not in mapped_section_ids:
                warnings.append(f"Section '{s_id}' has no courses assigned. It will not be scheduled.")

        # Suggestions
        if len(data["rooms"]) < (len(data["sections"]) / 5):
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
