from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List, Optional
import json

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

    def generate_timetable(self, version_number: int = 1) -> Optional[TimetableVersion]:
        """
        Fetches Assignments from DB, runs solver, saves results to DB and Snapshot.
        """
        # 1. Fetch Data
        # We schedule ALL assignments currently in the DB.
        # In future, we might filter by semester or active status.
        assignments_db = self.db.execute(select(Assignment)).scalars().all()
        rooms_db = self.db.execute(select(Room)).scalars().all()
        timeslots_db = self.db.execute(select(Timeslot)).scalars().all()
        
        if not assignments_db:
            print("⚠️ No assignments found to schedule.")
            return None

        # 2. Transform to Solver Model
        # Map Assignment (DB) -> SolverSection (Solver Logic)
        # We treat each Assignment row as a "Section" to be scheduled.
        solver_sections = []
        for a in assignments_db:
            # We use Assignment ID as the unique identifier for the solver
            solver_sections.append(SolverSection(
                id=a.id, 
                name=f"{a.section.code}_{a.course.code}", # Debug name
                course_id=a.course_id,
                faculty_id=a.faculty_id,
                room_type_required=a.course.needs_room_type 
            ))
            
        solver_rooms = [
            SolverRoom(id=r.id, name=r.code, type=r.type) # Use code as name
            for r in rooms_db
        ]
        
        solver_slots = [
            SolverTimeslot(id=t.id, day=t.day, start_time=str(t.start_time), end_time=str(t.end_time))
            for t in timeslots_db
        ]

        # 3. Run Solver
        print(f"🧩 Solving for {len(solver_sections)} assignments, {len(solver_rooms)} rooms, {len(solver_slots)} slots...")
        result = self.solver.solve(solver_sections, solver_rooms, solver_slots)

        if not result.is_feasible:
            print(f"❌ Timetable Generation Failed: {result.status}")
            print(f"   Reason: {result.conflict_reason}")
            return None

        # 4. Save Results to Database (Update Assignments)
        # result.assignments is a list of {section_id, room_id, timeslot_id}
        # Remember: section_id here maps to Assignment.id
        
        generated_map = {} # assignment_id -> {room_id, timeslot_id}
        for alloc in result.assignments:
            assign_id = alloc["section_id"]
            generated_map[assign_id] = alloc
            
            # Update DB object (will be committed later)
            # Find the corresponding assignment object (optimization: use map if list is large)
            assign_obj = next((a for a in assignments_db if a.id == assign_id), None)
            if assign_obj:
                assign_obj.room_id = alloc["room_id"]
                assign_obj.timeslot_id = alloc["timeslot_id"]

        # 5. Save to TimetableVersion (Snapshot)
        snapshot = {
            "version": version_number,
            "status": result.status,
            "assignments": result.assignments,
            "metrics": {
                "total_assignments": len(assignments_db),
                "scheduled": len(result.assignments)
            }
        }

        new_version = TimetableVersion(
            version_number=version_number,
            is_published=False,
            snapshot_data=snapshot
        )

        self.db.add(new_version)
        self.db.commit()
        self.db.refresh(new_version)
        
        print(f"✅ Timetable Version {version_number} generated and saved! (Assignments updated in DB)")
        return new_version
