from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import os
import json
from datetime import datetime

from app.services.data_integrity_verifier import DataIntegrityVerifier, IntegrityReport
from app.services.normalization_verifier import NormalizationVerifier
from app.config.verification import INTEGRITY_VERIFICATION

router = APIRouter()

def load_imported_data() -> Dict[str, Any]:
    db_path = os.environ.get("DATABASE_URL", "sqlite:///./test.db")
    
    from app.database import SessionLocal
    session = SessionLocal()
    
    try:
        from app.models.faculty import Faculty
        from app.models.course import Course
        from app.models.room import Room
        from app.models.section import Section
        from app.models.assignment import FacultyCourseAssignment
        
        data = {
            "faculty": [{"id": f.id, "name": f.name, "email": f.email} for f in session.query(Faculty).all()],
            "courses": [{"code": c.code, "name": c.name, "credits": c.weekly_periods, "type": c.course_type} for c in session.query(Course).all()],
            "rooms": [{"room_id": r.id, "capacity": r.capacity, "room_type": r.room_type} for r in session.query(Room).all()],
            "sections": [{"id": s.id, "student_count": s.student_count} for s in session.query(Section).all()],
            "faculty_course_map": [{"faculty_id": a.faculty_id, "course_id": a.course_id, "section_id": a.section_id} for a in session.query(FacultyCourseAssignment).all()],
        }
        return data
    finally:
        session.close()

@router.get("/verify")
async def verify_data() -> Dict[str, Any]:
    try:
        data = load_imported_data()
        
        verifier = DataIntegrityVerifier()
        integrity_report = verifier.verify_all(data)
        
        norm_config = INTEGRITY_VERIFICATION["fuzzy_match"]
        norm_verifier = NormalizationVerifier(
            faculty_threshold=norm_config["faculty_threshold"],
            course_threshold=norm_config["course_threshold"]
        )
        clustering_report = norm_verifier.get_clustering_report(data)
        
        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "integrity": {
                "is_healthy": integrity_report.is_healthy,
                "overall_score": integrity_report.overall_score,
                "summary": integrity_report.summary,
                "issues": integrity_report.issues,
                "metrics": {
                    entity: {
                        "total_records": m.total_records,
                        "duplicates_count": m.duplicates_count,
                        "missing_fields": m.missing_fields,
                        "orphan_records": m.orphan_records,
                        "completeness_percent": m.completeness_percent,
                        "issues": m.issues,
                    }
                    for entity, m in integrity_report.metrics.items()
                }
            },
            "normalization": {
                "overall_confidence": clustering_report.overall_confidence,
                "faculty_clusters_count": len(clustering_report.faculty_clusters),
                "course_clusters_count": len(clustering_report.course_clusters),
                "unmatched_faculty_count": len(clustering_report.unmatched_faculty),
                "unmatched_courses_count": len(clustering_report.unmatched_courses),
                "faculty_clusters": [
                    {
                        "canonical": c.canonical,
                        "confidence": c.confidence,
                        "count": len(c.names)
                    }
                    for c in clustering_report.faculty_clusters[:10]
                ],
                "course_clusters": [
                    {
                        "canonical": c.canonical,
                        "confidence": c.confidence,
                        "count": len(c.names)
                    }
                    for c in clustering_report.course_clusters[:10]
                ],
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Verification failed: {str(e)}")

@router.get("/config")
async def get_verification_config() -> Dict[str, Any]:
    return INTEGRITY_VERIFICATION
