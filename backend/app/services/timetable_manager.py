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

class TimetableManager:
    """
    Orchestrates data fetching, solving, and saving results.
    """
    def __init__(self, db: Session):
        self.db = db
        self.solver = SolverService()

    def generate_timetable(self, version_number: int = 1) -> Optional[TimetableVersion]:
        """
        Fetches data, runs solver, saves snapshot.
        """
        # 1. Fetch Data
        sections = self.db.execute(select(Section)).scalars().all()
        rooms = self.db.execute(select(Room)).scalars().all()
        timeslots = self.db.execute(select(Timeslot)).scalars().all()
        
        # In a real scenario, we'd have a mapping of which Faculty teaches which Section.
        # For this Phase 1 fulfillment, we'll assign the FIRST found faculty to all sections
        # to demonstrate the conflict logic.
        faculty = self.db.execute(select(Faculty)).scalars().first()
        faculty_id = faculty.id if faculty else 1

        # 2. Transform to Solver Models
        solver_sections = []
        for s in sections:
            solver_sections.append(SolverSection(
                id=s.id,
                name=s.name,
                student_count=s.student_count,
                course_id=s.course_id,
                faculty_id=faculty_id,
                room_type_required="Lecture" 
            ))
            
        solver_rooms = [
            SolverRoom(id=r.id, name=r.name, capacity=r.capacity, type=r.type)
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
