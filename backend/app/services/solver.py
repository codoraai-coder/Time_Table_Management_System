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
    required_periods: int
    allowed_slot_ids: List[int]
    is_lab: bool = False
    fixed_assignments: Optional[List[Dict[str, int]]] = None # List of {"room_id": int, "timeslot_id": int}

@dataclass
class SolverRoom:
    id: int
    name: str
    type: str  # 'Lecture' or 'Lab'

@dataclass
class SolverTimeslot:
    id: int
    day: int
    start_time: str 
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
            self.solver.parameters.random_seed = 42
            self.solver.parameters.num_search_workers = 1 
        else:
            self.model = None
            self.solver = None

    def solve(
        self,
        sections: List[SolverSection],
        rooms: List[SolverRoom],
        timeslots: List[SolverTimeslot]
    ) -> SolverResult:
        if not _ORTOOLS_AVAILABLE:
            return self._solve_fallback(sections, rooms, timeslots)

        # 0. Build Timeslot Metadata
        # Map (day, start_time) -> slot_id for consecutive check
        slot_map = {(t.day, t.start_time): t.id for t in timeslots}
        # Map slot_id -> (day, end_time) to find what comes next
        next_slot_lookup = {}
        for t in timeslots:
            # If there's a slot on the same day that starts when this one ends
            following_slot_id = slot_map.get((t.day, t.end_time))
            if following_slot_id:
                next_slot_lookup[t.id] = following_slot_id

        # 1. Variables
        # x[section_id, period_idx, room_id, timeslot_id]
        x = {}
        
        for section in sections:
            for p_idx in range(section.required_periods):
                for room in rooms:
                    if section.room_type_required != room.type:
                        continue
                    
                    for slot_id in section.allowed_slot_ids:
                        x[(section.id, p_idx, room.id, slot_id)] = self.model.NewBoolVar(
                            f'x_{section.id}_{p_idx}_{room.id}_{slot_id}'
                        )

        # 2. Hard Constraints

        # C1: Every period of every section must be assigned exactly once
        for section in sections:
            for p_idx in range(section.required_periods):
                # If this period is fixed, we just enforce that specific variable to 1
                if section.fixed_assignments and p_idx < len(section.fixed_assignments):
                    fa = section.fixed_assignments[p_idx]
                    fixed_key = (section.id, p_idx, fa["room_id"], fa["timeslot_id"])
                    
                    # We must ensure this variable was created (is in section.allowed_slot_ids)
                    if fixed_key in x:
                        self.model.Add(x[fixed_key] == 1)
                    else:
                        # If the fixed assignment is outside allowed slots, it's a conflict
                        return SolverResult(False, "INFEASIBLE", [], f"Fixed assignment for {section.name} is in an invalid slot/room.")
                    continue

                candidates = []
                for room in rooms:
                    for slot_id in section.allowed_slot_ids:
                        if (section.id, p_idx, room.id, slot_id) in x:
                            candidates.append(x[(section.id, p_idx, room.id, slot_id)])
                
                if not candidates:
                    return SolverResult(False, "INFEASIBLE", [], f"Section {section.name} (Period {p_idx}) has no valid candidates.")
                
                self.model.Add(sum(candidates) == 1)

        # C1.1: Lab Consecutive Periods (2 periods, same room, same day, consecutive time)
        for section in sections:
            if section.is_lab and section.required_periods == 2:
                for room in rooms:
                    if section.room_type_required != room.type: 
                        continue
                    
                    for slot_id in section.allowed_slot_ids:
                        p0_key = (section.id, 0, room.id, slot_id)
                        if p0_key in x:
                            p0_var = x[p0_key]
                            next_id = next_slot_lookup.get(slot_id)
                            
                            # Period 1 must be in the same room on the next slot
                            p1_key = (section.id, 1, room.id, next_id) if next_id else None
                            p1_var = x.get(p1_key)
                            
                            if p1_var is not None:
                                # p0_var == 1 implies p1_var == 1
                                self.model.Add(p1_var == 1).OnlyEnforceIf(p0_var)
                            else:
                                # If no next slot exists (e.g. end of day/shift), p0 cannot be assigned here
                                self.model.Add(p0_var == 0)

        # C2: Room Conflict
        for room in rooms:
            for slot in timeslots:
                room_slot_vars = []
                for section in sections:
                    for p_idx in range(section.required_periods):
                        if (section.id, p_idx, room.id, slot.id) in x:
                            room_slot_vars.append(x[(section.id, p_idx, room.id, slot.id)])
                
                if room_slot_vars:
                    self.model.Add(sum(room_slot_vars) <= 1)

        # C3: Faculty Conflict
        faculties = {s.faculty_id for s in sections}
        for f_id in faculties:
            fac_sections = [s for s in sections if s.faculty_id == f_id]
            for slot in timeslots:
                fac_slot_vars = []
                for s in fac_sections:
                    for p_idx in range(s.required_periods):
                        for room in rooms:
                            if (s.id, p_idx, room.id, slot.id) in x:
                                fac_slot_vars.append(x[(s.id, p_idx, room.id, slot.id)])
                
                if fac_slot_vars:
                    self.model.Add(sum(fac_slot_vars) <= 1)

        # C4: Student Group Conflict
        section_groups = {}
        for s in sections:
            base_name = s.name.split('-')[0]
            if base_name not in section_groups:
                section_groups[base_name] = []
            section_groups[base_name].append(s)
        
        for group_name, group_sections in section_groups.items():
            for slot in timeslots:
                group_slot_vars = []
                for s in group_sections:
                    for p_idx in range(s.required_periods):
                        for room in rooms:
                            if (s.id, p_idx, room.id, slot.id) in x:
                                group_slot_vars.append(x[(s.id, p_idx, room.id, slot.id)])
                
                if group_slot_vars:
                    self.model.Add(sum(group_slot_vars) <= 1)

        # C5: Daily Subject Limit (Don't clump one subject on one day)
        # Max 2 periods per day for the same section-subject
        days = sorted(list({t.day for t in timeslots}))
        for section in sections:
            if section.is_lab: continue # Labs are already handled as 2 periods together
            for day in days:
                day_slots = [t.id for t in timeslots if t.day == day]
                section_day_vars = []
                for p_idx in range(section.required_periods):
                    for room in rooms:
                        if section.room_type_required != room.type: continue
                        for slot_id in day_slots:
                            if (section.id, p_idx, room.id, slot_id) in x:
                                section_day_vars.append(x[(section.id, p_idx, room.id, slot_id)])
                
                if section_day_vars:
                    self.model.Add(sum(section_day_vars) <= 2)

        # 3. Solve
        status = self.solver.Solve(self.model)

        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            result_assignments = []
            for (sec_id, p_idx, room_id, slot_id), var in x.items():
                if self.solver.Value(var) == 1:
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
