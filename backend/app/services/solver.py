from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass

try:
    from ortools.sat.python import cp_model
    _ORTOOLS_AVAILABLE = True
except (ImportError, OSError):
    _ORTOOLS_AVAILABLE = False
    print("⚠️  OR-Tools not available (Missing DLLs?). Using Pure Python Fallback Solver.")

# --- Internal Solver Models (Decoupled from DB) ---
# We use dataclasses/pydantic for speed and clarity

@dataclass
class SolverSection:
    id: int
    name: str
    course_id: int
    faculty_id: int
    room_type_required: str  # 'Lecture' or 'Lab'
    # Future: valid_room_ids

@dataclass
class SolverRoom:
    id: int
    name: str
    type: str  # 'Lecture' or 'Lab'

@dataclass
class SolverTimeslot:
    id: int
    day: int
    start_time: str # Simplified for debug
    end_time: str

@dataclass
class SolverResult:
    is_feasible: bool
    status: str
    assignments: List[Dict[str, int]]  # List of {section_id, room_id, timeslot_id}
    conflict_reason: Optional[str] = None

class SolverService:
    def __init__(self):
        if _ORTOOLS_AVAILABLE:
            self.model = cp_model.CpModel()
            self.solver = cp_model.CpSolver()
            # Determinism settings
            self.solver.parameters.random_seed = 42
            self.solver.parameters.num_search_workers = 1  # Single thread for determinism
        else:
            self.model = None
            self.solver = None

    def solve(
        self,
        sections: List[SolverSection],
        rooms: List[SolverRoom],
        timeslots: List[SolverTimeslot]
    ) -> SolverResult:
        """
        Main entry point to generate timetable.
        """
        if not _ORTOOLS_AVAILABLE:
            return self._solve_fallback(sections, rooms, timeslots)

        # 1. Variables
        # x[section_id, room_id, timeslot_id] -> 1 if assigned, 0 otherwise
        x = {}
        
        for section in sections:
            for room in rooms:
                for slot in timeslots:
                    # Pre-filter: Type Compatibility
                    if section.room_type_required != room.type:
                        continue 

                    x[(section.id, room.id, slot.id)] = self.model.NewBoolVar(
                        f'x_{section.id}_{room.id}_{slot.id}'
                    )

        # 2. Hard Constraints

        # C1: Each section must be assigned exactly ONE room and ONE timeslot
        for section in sections:
            candidates = []
            for room in rooms:
                for slot in timeslots:
                    if (section.id, room.id, slot.id) in x:
                        candidates.append(x[(section.id, room.id, slot.id)])
            
            if not candidates:
                # Basic check failed
                return SolverResult(False, "INFEASIBLE_NO_CANDIDATES", [], f"Section {section.id} has no valid rooms (Type/Capacity mismatch)")
            
            self.model.Add(sum(candidates) == 1)

        # C2: Room Conflict
        for room in rooms:
            for slot in timeslots:
                potential_sections = []
                for section in sections:
                    if (section.id, room.id, slot.id) in x:
                        potential_sections.append(x[(section.id, room.id, slot.id)])
                
                if potential_sections:
                    self.model.Add(sum(potential_sections) <= 1)

        # C3: Faculty Conflict
        sections_by_faculty = {}
        for section in sections:
            if section.faculty_id not in sections_by_faculty:
                sections_by_faculty[section.faculty_id] = []
            sections_by_faculty[section.faculty_id].append(section)
        
        for faculty_id, fac_sections in sections_by_faculty.items():
            for slot in timeslots:
                fac_assignments_at_slot = []
                for section in fac_sections:
                    for room in rooms:
                        if (section.id, room.id, slot.id) in x:
                            fac_assignments_at_slot.append(x[(section.id, room.id, slot.id)])
                
                if fac_assignments_at_slot:
                    self.model.Add(sum(fac_assignments_at_slot) <= 1)

        # 3. Solve
        status = self.solver.Solve(self.model)

        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            result_assignments = []
            for (sec_id, room_id, slot_id), variable in x.items():
                if self.solver.Value(variable) == 1:
                    result_assignments.append({
                        "section_id": sec_id,
                        "room_id": room_id,
                        "timeslot_id": slot_id
                    })
            return SolverResult(True, "FEASIBLE", result_assignments)
        else:
            return SolverResult(False, "INFEASIBLE", [], "Conflicts detected (No solution found)")

    def _solve_fallback(self, sections, rooms, timeslots) -> SolverResult:
        """
        Pure Python backtracking solver for local debugging/testing without OR-Tools.
        """
        assignments = {} # section_id -> (room_id, slot_id)

        # Group sections by faculty for fast lookup
        sections_by_faculty = {}
        for s in sections:
            if s.faculty_id not in sections_by_faculty: sections_by_faculty[s.faculty_id] = []
            sections_by_faculty[s.faculty_id].append(s)

        def is_valid(section, room, slot):
            # 1. Type
            if section.room_type_required != room.type: return False
            
            # 2. Room Conflict
            for s_id, (r_id, sl_id) in assignments.items():
                if r_id == room.id and sl_id == slot.id:
                    return False
            
            # 4. Faculty Conflict
            # Check other sections taught by same faculty
            # If any are assigned to this same slot, conflict.
            # (Note: simpler to just check all current assignments)
            for s_id, (r_id, sl_id) in assignments.items():
                # Find section object for s_id
                assigned_sec = next((s for s in sections if s.id == s_id), None)
                if assigned_sec and assigned_sec.faculty_id == section.faculty_id and sl_id == slot.id:
                    return False
            
            return True

        def backtrack(section_index):
            if section_index == len(sections):
                return True # All assigned!
            
            section = sections[section_index]
            
            for room in rooms:
                for slot in timeslots:
                    if is_valid(section, room, slot):
                        assignments[section.id] = (room.id, slot.id)
                        if backtrack(section_index + 1):
                            return True
                        del assignments[section.id]
            
            return False

        if backtrack(0):
            result = []
            for sec_id, (r_id, sl_id) in assignments.items():
                result.append({"section_id": sec_id, "room_id": r_id, "timeslot_id": sl_id})
            return SolverResult(True, "FEASIBLE_PYTHON", result)
        else:
            return SolverResult(False, "INFEASIBLE_PYTHON", [], "Constraints violated")
