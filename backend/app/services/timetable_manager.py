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
        Fetches data, runs solver, saves snapshot.
        """
        # 1. Fetch Data
        sections = self.db.execute(select(Section)).scalars().all()
        rooms = self.db.execute(select(Room)).scalars().all()
        timeslots = self.db.execute(select(Timeslot)).scalars().all()
        faculty_all = self.db.execute(select(Faculty)).scalars().all()
        
        # 2. Pre-Validation
        # Convert DB models to dict for validator (simulating CSV input)
        data_to_validate = {
            "faculty": [{"id": f.id, "name": f.name, "email": f.email} for f in faculty_all],
            "courses": [{"code": c.code, "name": c.name} for c in self.db.execute(select(Course)).scalars().all()],
            "rooms": [{"name": r.name, "type": r.type} for r in rooms],
            "sections": [
                {"id": s.id, "course_code": s.course.code, "student_count": 30, "room_type": "Lecture"} # Defaults for now
                for s in sections
            ],
            # This mapping logic needs better data in future
            "faculty_course_map": [{"faculty_email": faculty_all[0].email, "section_id": sections[0].id}] if faculty_all and sections else []
        }
        
        val_result = self.validator.validate_structure(data_to_validate)
        if not val_result.is_valid:
            print(f"❌ Validation Failed: {val_result.errors}")
            return None
        
        if val_result.warnings:
            print(f"⚠️ Validation Warnings: {val_result.warnings}")

        # 3. Transform to Solver Model
        # In a real scenario, we'd have a mapping of which Faculty teaches which Section.
        # For this Phase 1 fulfillment, we'll assign the FIRST found faculty to all sections
        # to demonstrate the conflict logic.
        faculty = self.db.execute(select(Faculty)).scalars().first()
        faculty_id = faculty.id if faculty else 1

        solver_sections = []
        for s in sections:
            solver_sections.append(SolverSection(
                id=s.id,
                name=s.name,
                course_id=s.course_id,
                faculty_id=faculty_id,
                room_type_required="Lecture" 
            ))
            
        solver_rooms = [
            SolverRoom(id=r.id, name=r.name, type=r.type)
            for r in rooms
        ]
        
        solver_slots = [
            SolverTimeslot(id=t.id, day=t.day, start_time=str(t.start_time), end_time=str(t.end_time))
            for t in timeslots
        ]

        # 3. Run Solver
        result = self.solver.solve(solver_sections, solver_rooms, solver_slots)

        if not result.is_feasible:
            print(f"❌ Timetable Generation Failed: {result.status}")
            return None

        # 4. Save to TimetableVersion (The Snapshot)
        snapshot = {
            "version": version_number,
            "status": result.status,
            "assignments": result.assignments
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
