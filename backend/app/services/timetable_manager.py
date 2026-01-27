from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List, Optional
import json
from datetime import time

from app.models import (
    Section, Room, Timeslot, Faculty, TimetableVersion, Assignment, Course
)
from app.services.solver import (
    SolverService, SolverSection, SolverRoom, SolverTimeslot, SolverResult
)
from app.services.validator import ValidatorService, ValidationResult

class TimetableManager:
    """
    Orchestrates data fetching, solving, and saving results.
    """
    def __init__(self, db: Session):
        self.db = db
        self.solver = SolverService()
        self.validator = ValidatorService()

    def generate_timetable(self, version_number: int = 1, target_section_names: Optional[List[str]] = None) -> Optional[TimetableVersion]:
        """
        Fetches Assignments from DB, runs solver, and saves scheduled results.
        If target_section_names is provided, only those sections are re-scheduled.
        """
        # 1. Fetch Data
        # We fetch all "contractual" assignments (those without room/timeslot yet, 
        # or we treat them as templates if we are regenerating).
        # For simplicity, we fetch all assignments and their related data.
        all_assignments = self.db.execute(select(Assignment)).scalars().all()
        rooms = self.db.execute(select(Room)).scalars().all()
        timeslots = self.db.execute(select(Timeslot)).scalars().all()
        
        if not all_assignments:
            print("⚠️ No assignments found in database. Import data first.")
            return None

        # 2. Identify Target vs Fixed Assignments
        # In the new architecture, we target by Section Code
        if target_section_names:
            target_assignments = [a for a in all_assignments if a.section.code in target_section_names]
            fixed_assignments = [a for a in all_assignments if a.section.code not in target_section_names]
            print(f">> Partial Generation: Target Sections={target_section_names}")
        else:
            target_assignments = all_assignments
            fixed_assignments = []
            print(">> Full Generation: All assignments targeted.")

        # 3. Transform to Solver Model
        # One Assignment row in DB -> One SolverSection entry (with N periods based on credits)
        solver_sections = []
        
        # We use a set to keep track of assignments we've already added as SolverSections
        # (Though unique assignments are expected from DB)
        for a in all_assignments:
            s_model = a.section
            c_model = a.course
            
            # Shift Resolution from Section
            allowed_slots = []
            for t in timeslots:
                if t.day > 4: continue # Mon-Fri only
                if s_model.shift == "SHIFT_8_4":
                    if t.start_time >= time(8, 0) and t.end_time <= time(16, 0):
                        allowed_slots.append(t.id)
                elif s_model.shift == "SHIFT_10_6":
                    if t.start_time >= time(10, 0) and t.end_time <= time(18, 0):
                        allowed_slots.append(t.id)
                else:
                    allowed_slots.append(t.id)

            # Enforce lunch as a hard empty slot per shift by removing that timeslot
            # from allowed_slots so solver cannot assign into it.
            try:
                if s_model.shift == "SHIFT_8_4":
                    lunch_time = time(12, 0)
                elif s_model.shift == "SHIFT_10_6":
                    lunch_time = time(13, 0)
                else:
                    lunch_time = None

                if lunch_time is not None:
                    # remove any timeslot that starts exactly at lunch_time
                    lunch_ids = [t.id for t in timeslots if t.start_time == lunch_time]
                    for lid in lunch_ids:
                        if lid in allowed_slots:
                            allowed_slots.remove(lid)
            except Exception:
                # conservative: if any issue, don't remove slots (avoid crashing generation)
                pass

            # Lab detection and Period calculation
            is_lab = (c_model.type.upper() == "LAB")
            req_periods = 2 if is_lab else c_model.credits
            
            # If this assignment is fixed, load its current slots (if any)
            # Note: The new model assumes 1 row = 1 slot. 
            # If multiple slots were previously assigned, we'd need to collect them.
            # For now, we assume regeneration clears the board.
            fixed_data = None
            if a in fixed_assignments and a.room_id and a.timeslot_id:
                fixed_data = [{"room_id": a.room_id, "timeslot_id": a.timeslot_id}]

            solver_sections.append(SolverSection(
                id=a.id,
                section_id=s_model.id,
                name=f"{s_model.code}_{c_model.code}",
                course_id=c_model.id,
                faculty_id=a.faculty_id,
                room_type_required=c_model.needs_room_type,
                required_periods=req_periods,
                allowed_slot_ids=allowed_slots,
                is_lab=is_lab,
                fixed_assignments=fixed_data
            ))

        solver_rooms = [SolverRoom(id=r.id, name=r.code, type=r.type) for r in rooms]
        solver_slots = [SolverTimeslot(id=t.id, day=t.day, start_time=str(t.start_time), end_time=str(t.end_time)) for t in timeslots]

        # 4. Run Solver
        print(f"🧩 Solving for {len(solver_sections)} assignments...")
        result = self.solver.solve(solver_sections, solver_rooms, solver_slots)

        if not result.is_feasible:
            print(f"❌ Timetable Generation Failed: {result.status} (Reason: {result.conflict_reason})")
            return None

        # 5. Save Results  
        # For full generation: delete all old and recreate with new room/timeslot assignments
        if not target_section_names:
            # Full generation
            self.db.query(Assignment).delete()
            self.db.commit()
            
            # Create a mapping of original assignment data by their old IDs
            orig_assignment_data = {a.id: a for a in all_assignments}
            
            # Create fresh assignments with solver results
            new_db_assignments = []
            for alloc in result.assignments:
                orig = orig_assignment_data[alloc["section_id"]]
                new_db_assignments.append(Assignment(
                    section_id=orig.section_id,
                    faculty_id=orig.faculty_id,
                    course_id=orig.course_id,
                    room_id=alloc["room_id"],
                    timeslot_id=alloc["timeslot_id"]
                ))
            self.db.add_all(new_db_assignments)
            self.db.commit()
        else:
            # Partial generation: only update target assignments
            for alloc in result.assignments:
                orig_id = alloc["section_id"]
                orig = next((a for a in all_assignments if a.id == orig_id), None)
                if orig:
                    orig.room_id = alloc["room_id"]
                    orig.timeslot_id = alloc["timeslot_id"]
                    self.db.merge(orig)
            self.db.commit()

        # 6. Build Snapshot
        # At this point, all new assignments are in the database
        structured_timetable = self._build_structured_output(result.assignments)
        
        snapshot = {
            "version": version_number,
            "status": result.status,
            "sections": structured_timetable
        }

        new_version = TimetableVersion(
            version_number=version_number,
            is_published=False,
            snapshot_data=snapshot
        )

        self.db.add(new_version)
        self.db.commit()
        self.db.refresh(new_version)
        
        print(f"✅ Timetable Version {version_number} generated and saved!")
        return new_version

    def _build_structured_output(self, assignments: List[dict]) -> dict:
        """Groups assignments by Section and Day for a professional view."""
        # Fetch all current assignments from database (after solver has updated them)
        all_current_assignments = self.db.execute(select(Assignment)).scalars().all()
        
        # Build lookup maps for relationships
        sections = {s.id: s for s in self.db.execute(select(Section)).scalars().all()}
        rooms = {r.id: r for r in self.db.execute(select(Room)).scalars().all()}
        slots = {t.id: t for t in self.db.execute(select(Timeslot)).scalars().all()}
        courses = {c.id: c for c in self.db.execute(select(Course)).scalars().all()}
        faculties = {f.id: f for f in self.db.execute(select(Faculty)).scalars().all()}
        
        days_map = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        output = {}
        
        # Process all current assignments (these now have room_id and timeslot_id filled in by solver)
        for assignment in all_current_assignments:
            if not assignment.room_id or not assignment.timeslot_id:
                continue  # Skip incomplete assignments
            
            sec_code = assignment.section.code
            day_name = days_map[assignment.timeslot.day]
            
            if sec_code not in output:
                output[sec_code] = {d: [] for d in days_map}
            
            output[sec_code][day_name].append({
                "time": f"{assignment.timeslot.start_time.strftime('%H:%M')} - {assignment.timeslot.end_time.strftime('%H:%M')}",
                "course": assignment.course.name,
                "course_code": assignment.course.code,
                "faculty": assignment.faculty.name,
                "room": assignment.room.code,
                "room_type": assignment.room.type
            })
        
        # Sort by time within each day
        for sec in output:
            for day in output[sec]:
                output[sec][day].sort(key=lambda x: x["time"])
                
        return output
