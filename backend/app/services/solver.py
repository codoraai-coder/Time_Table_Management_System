from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass
from datetime import time as _time

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
    id: int # This is the Assignment ID
    section_id: int # The Group ID for student conflict
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

        # C4: Student Group Conflict (Ensure one section doesn't have 2 classes at once)
        section_groups = {}
        for s in sections:
            group_id = s.section_id
            if group_id not in section_groups:
                section_groups[group_id] = []
            section_groups[group_id].append(s)
        
        for group_id, group_sections in section_groups.items():
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
        # Improved fallback that supports multi-period assignments per section,
        # consecutive 2-hour lab placements, lunch-slot blocking, and all
        # basic conflict constraints (room, faculty, section-group/day limits).

        # Helpers / metadata
        slot_map = {(t.day, t.start_time): t.id for t in timeslots}
        next_slot_lookup = {}
        slot_by_id = {t.id: t for t in timeslots}
        for t in timeslots:
            following_slot_id = slot_map.get((t.day, t.end_time))
            if following_slot_id:
                next_slot_lookup[t.id] = following_slot_id

        # Identify lunch start times to avoid scheduling into them (global conservative block)
        # Use time objects for robust comparisons
        lunch_starts = set([_time(12, 0), _time(13, 0)])

        # assignments: (section_id, period_index) -> (room_id, slot_id)
        assignments = {}

        # Quick helper maps for conflict checks
        room_slot_map = {}       # (room_id, slot_id) -> (section_id, p_idx)
        faculty_slot_map = {}    # (faculty_id, slot_id) -> list of (section_id, p_idx)
        group_slot_map = {}      # (group_id, slot_id) -> list
        # track per-section per-day counts for non-lab subjects
        section_day_count = {}   # (section_id, day) -> count

        # Build a mapping for fast lookup of section objects by id
        sections_by_id = {s.id: s for s in sections}

        def _slot_time_obj(slot):
            # slot.start_time may be a string or a time object
            st = slot.start_time
            if isinstance(st, str):
                try:
                    return _time.fromisoformat(st)
                except Exception:
                    # Fallback: try HH:MM
                    parts = st.split(':')
                    return _time(int(parts[0]), int(parts[1]))
            if isinstance(st, _time):
                return st
            return _time(0, 0)


        def can_place(section: SolverSection, room: SolverRoom, slot_id: int, p_idx: int) -> bool:
            # Type match
            if section.room_type_required != room.type:
                return False

            # Slot allowed for this section
            if slot_id not in section.allowed_slot_ids:
                return False

            # Avoid lunch slots
            sl = slot_by_id[slot_id]
            sl_start = _slot_time_obj(sl)
            if sl_start in lunch_starts:
                return False

            # Room conflict
            if (room.id, slot_id) in room_slot_map:
                return False

            # Faculty conflict
            fkey = (section.faculty_id, slot_id)
            if fkey in faculty_slot_map and faculty_slot_map[fkey]:
                return False

            # Group (section_id) conflict: no two classes of same group at same slot
            gkey = (section.section_id, slot_id)
            if gkey in group_slot_map and group_slot_map[gkey]:
                return False

            # Daily subject limit: for non-lab subjects, max 2 periods per day per section
            if not section.is_lab:
                day = sl.day
                ckey = (section.section_id, day)
                existing = section_day_count.get(ckey, 0)
                # If placing this period would exceed 2 for the day, disallow
                if existing + 1 > 2:
                    return False

            return True

        # Backtracking order: sort sections by descending required_periods (harder first)
        order = sorted(sections, key=lambda s: (-s.required_periods, s.id))

        def backtrack(idx: int) -> bool:
            if idx == len(order):
                return True

            section = order[idx]

            # For labs with required_periods==2, we try to assign both periods together
            if section.is_lab and section.required_periods == 2:
                # Try all rooms of matching type
                for room in rooms:
                    if section.room_type_required != room.type: continue

                    for slot_id in section.allowed_slot_ids:
                        # slot_id must have a next consecutive slot on same day
                        next_id = next_slot_lookup.get(slot_id)
                        if not next_id: continue
                        # Ensure next slot also allowed
                        if next_id not in section.allowed_slot_ids: continue

                        # Avoid lunch overlapping either slot
                        s0 = slot_by_id[slot_id]
                        s1 = slot_by_id[next_id]
                        if s0.start_time in lunch_starts or s1.start_time in lunch_starts:
                            continue

                        # Check both slots available in room and faculty/group
                        if not can_place(section, room, slot_id, 0):
                            continue
                        # For second period, check conflicts too
                        if (room.id, next_id) in room_slot_map: continue
                        if (section.faculty_id, next_id) in faculty_slot_map and faculty_slot_map[(section.faculty_id, next_id)]:
                            continue
                        if (section.section_id, next_id) in group_slot_map and group_slot_map[(section.section_id, next_id)]:
                            continue

                        # Place both
                        assignments[(section.id, 0)] = (room.id, slot_id)
                        assignments[(section.id, 1)] = (room.id, next_id)
                        room_slot_map[(room.id, slot_id)] = (section.id, 0)
                        room_slot_map[(room.id, next_id)] = (section.id, 1)
                        faculty_slot_map.setdefault((section.faculty_id, slot_id), []).append((section.id, 0))
                        faculty_slot_map.setdefault((section.faculty_id, next_id), []).append((section.id, 1))
                        group_slot_map.setdefault((section.section_id, slot_id), []).append((section.id, 0))
                        group_slot_map.setdefault((section.section_id, next_id), []).append((section.id, 1))

                        # Labs count as 1 slot per day for daily-limit purposes (but they are skipped earlier)

                        if backtrack(idx + 1):
                            return True

                        # Undo placement
                        del assignments[(section.id, 0)]
                        del assignments[(section.id, 1)]
                        del room_slot_map[(room.id, slot_id)]
                        del room_slot_map[(room.id, next_id)]
                        faculty_slot_map[(section.faculty_id, slot_id)].pop()
                        faculty_slot_map[(section.faculty_id, next_id)].pop()
                        group_slot_map[(section.section_id, slot_id)].pop()
                        group_slot_map[(section.section_id, next_id)].pop()

                return False

            # Non-lab or multi-period (treat each required_periods as separate p_idx placements)
            # We will assign p_idx from 0..required_periods-1 sequentially
            def assign_period(p_idx: int) -> bool:
                if p_idx >= section.required_periods:
                    # done with this section
                    return backtrack(idx + 1)

                for room in rooms:
                    if section.room_type_required != room.type: continue
                    for slot_id in section.allowed_slot_ids:
                        if not can_place(section, room, slot_id, p_idx):
                            continue

                        # Place
                        assignments[(section.id, p_idx)] = (room.id, slot_id)
                        room_slot_map[(room.id, slot_id)] = (section.id, p_idx)
                        faculty_slot_map.setdefault((section.faculty_id, slot_id), []).append((section.id, p_idx))
                        group_slot_map.setdefault((section.section_id, slot_id), []).append((section.id, p_idx))
                        day = slot_by_id[slot_id].day
                        section_day_count[(section.section_id, day)] = section_day_count.get((section.section_id, day), 0) + 1

                        if assign_period(p_idx + 1):
                            return True

                        # undo
                        del assignments[(section.id, p_idx)]
                        del room_slot_map[(room.id, slot_id)]
                        faculty_slot_map[(section.faculty_id, slot_id)].pop()
                        group_slot_map[(section.section_id, slot_id)].pop()
                        section_day_count[(section.section_id, day)] -= 1

                return False

            return assign_period(0)

        ok = backtrack(0)
        if ok:
            result = []
            for (sec_id, p_idx), (r_id, sl_id) in assignments.items():
                result.append({"section_id": sec_id, "room_id": r_id, "timeslot_id": sl_id})
            return SolverResult(True, "FEASIBLE_PYTHON", result)
        else:
            return SolverResult(False, "INFEASIBLE_PYTHON", [], "Constraints violated in fallback solver")
