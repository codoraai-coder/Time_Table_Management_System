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
        Fetches data, runs solver, saves snapshot.
        If target_section_names is provided, only those sections are re-scheduled,
        while others are kept fixed based on existing assignments.
        """
        # 1. Fetch Data
        all_sections = self.db.execute(select(Section)).scalars().all()
        rooms = self.db.execute(select(Room)).scalars().all()
        timeslots = self.db.execute(select(Timeslot)).scalars().all()
        faculty_all = self.db.execute(select(Faculty)).scalars().all()
        
        # 2. Identify Target vs Fixed Sections
        if target_section_names:
            # Suffix Cleaning for comparison (target_section_names should be clean)
            target_sections = [s for s in all_sections if s.name.split('-')[0] in target_section_names]
            fixed_sections = [s for s in all_sections if s.name.split('-')[0] not in target_section_names]
            print(f">> Partial Generation: Target={target_section_names}, Fixed={[s.name for s in fixed_sections]}")
        else:
            target_sections = all_sections
            fixed_sections = []
            print(">> Full Generation: All sections targeted.")

        # 3. Load Existing Assignments for Fixed Sections
        fixed_assignments_map = {}
        if fixed_sections:
            fixed_ids = [s.id for s in fixed_sections]
            existing = self.db.execute(select(Assignment).where(Assignment.section_id.in_(fixed_ids))).scalars().all()
            for a in existing:
                if a.section_id not in fixed_assignments_map:
                    fixed_assignments_map[a.section_id] = []
                fixed_assignments_map[a.section_id].append({"room_id": a.room_id, "timeslot_id": a.timeslot_id})

        # 4. Transform to Solver Model
        solver_sections = []
        for s in all_sections:
            # Fallback to first faculty if none assigned
            f_id = s.faculty_id if s.faculty_id else (faculty_all[0].id if faculty_all else 1)
            
            # Shift Resolution
            allowed_slots = []
            for t in timeslots:
                if t.day > 4: continue
                if s.shift == "SHIFT_8_4":
                    if t.start_time >= time(8, 0) and t.end_time <= time(16, 0):
                        allowed_slots.append(t.id)
                elif s.shift == "SHIFT_10_6":
                    if t.start_time >= time(10, 0) and t.end_time <= time(18, 0):
                        allowed_slots.append(t.id)
                else:
                    allowed_slots.append(t.id)

            # Check if this section is a Lab
            is_lab = (s.room_type == "Lab")
            req_periods = 2 if is_lab else (s.course.credits if s.course else 1)

            fixed_data = fixed_assignments_map.get(s.id)
            
            solver_sections.append(SolverSection(
                id=s.id,
                name=s.name,
                course_id=s.course_id,
                faculty_id=f_id,
                room_type_required=s.room_type,
                required_periods=req_periods,
                allowed_slot_ids=allowed_slots,
                is_lab=is_lab,
                fixed_assignments=fixed_data
            ))
            
        solver_rooms = [SolverRoom(id=r.id, name=r.name, type=r.type) for r in rooms]
        solver_slots = [SolverTimeslot(id=t.id, day=t.day, start_time=str(t.start_time), end_time=str(t.end_time)) for t in timeslots]

        # 5. Run Solver
        result = self.solver.solve(solver_sections, solver_rooms, solver_slots)

        if not result.is_feasible:
            print(f"[!] Timetable Generation Failed: {result.status} (Reason: {result.conflict_reason})")
            return None

        # 6. Save Results
        # If target sections were specified, first clear their OLD assignments from the DB
        if target_section_names:
            target_ids = [s.id for s in target_sections]
            self.db.execute(Assignment.__table__.delete().where(Assignment.section_id.in_(target_ids)))
            self.db.commit()

        # Insert new assignments (only for target sections, others are already in DB if we didn't clear them)
        # Actually, for simplicity, if it's a new TimetableVersion, we might want to refresh all assignments in the table.
        # But if we want to keep it incremental, we only insert what changed.
        # However, the solver returns ALL assignments.
        
        # Let's clear everything in the Assignment table and insert the fresh set from solver
        self.db.query(Assignment).delete()
        new_assignments = []
        for a in result.assignments:
            sec = next(s for s in all_sections if s.id == a["section_id"])
            new_assignments.append(Assignment(
                section_id=a["section_id"],
                faculty_id=sec.faculty_id if sec.faculty_id else 1,
                course_id=sec.course_id,
                room_id=a["room_id"],
                timeslot_id=a["timeslot_id"]
            ))
        self.db.add_all(new_assignments)
        self.db.commit()

        # 7. Group and Enrich Output for Snapshot
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
        
        print(f"[ok] Timetable Version {version_number} generated and saved!")
        return new_version

    def _build_structured_output(self, assignments: List[dict]) -> dict:
        """Groups assignments by Section and Day for a professional view."""
        # 1. Fetch maps for performance
        sections = {s.id: s for s in self.db.execute(select(Section)).scalars().all()}
        rooms = {r.id: r for r in self.db.execute(select(Room)).scalars().all()}
        slots = {t.id: t for t in self.db.execute(select(Timeslot)).scalars().all()}
        
        days_map = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        # Structure: output[section_name][day_name] = [list of sessions]
        output = {}
        
        for a in assignments:
            s = sections.get(a["section_id"])
            r = rooms.get(a["room_id"])
            t = slots.get(a["timeslot_id"])
            
            # Get base section name like 'CSE_2A' from 'CSE_2A-DBMS'
            sec_name = s.name.split('-')[0] if '-' in s.name else s.name
            day_name = days_map[t.day]
            
            if sec_name not in output:
                output[sec_name] = {d: [] for d in days_map[:5]} # Monday to Friday
            
            output[sec_name][day_name].append({
                "time": f"{t.start_time.strftime('%H:%M')} - {t.end_time.strftime('%H:%M')}",
                "course": s.course.name if s and s.course else "Unknown",
                "course_code": s.course.code if s and s.course else "Unknown",
                "faculty": s.faculty.name if s and s.faculty else "Unknown",
                "room": r.name if r else "Unknown",
                "room_type": r.type if r else "Unknown"
            })
        
        # Sort each day's sessions by time
        for sec in output:
            for day in output[sec]:
                output[sec][day].sort(key=lambda x: x["time"])
                
        return output
