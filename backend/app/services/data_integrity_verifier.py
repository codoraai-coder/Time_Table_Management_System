from dataclasses import dataclass, field
from typing import Dict, List, Set, Any
from collections import Counter

@dataclass
class QualityMetrics:
    entity: str
    total_records: int
    duplicates_count: int = 0
    missing_fields: Dict[str, int] = field(default_factory=dict)
    orphan_records: List[str] = field(default_factory=list)
    completeness_percent: float = 0.0
    issues: List[str] = field(default_factory=list)

@dataclass
class IntegrityReport:
    is_healthy: bool
    overall_score: float
    metrics: Dict[str, QualityMetrics] = field(default_factory=dict)
    summary: str = ""
    issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

class DataIntegrityVerifier:
    def __init__(self):
        self.min_health_threshold = 80

    def verify_all(self, data: Dict[str, List[Dict[str, Any]]]) -> IntegrityReport:
        report = IntegrityReport(is_healthy=True, overall_score=100.0)
        
        report.metrics["faculty"] = self.verify_faculty(data.get("faculty", []))
        report.metrics["courses"] = self.verify_courses(data.get("courses", []))
        report.metrics["rooms"] = self.verify_rooms(data.get("rooms", []))
        report.metrics["sections"] = self.verify_sections(data.get("sections", []))
        report.metrics["mappings"] = self.verify_mappings(data)
        
        self._aggregate_report(report, data)
        return report

    def verify_faculty(self, faculty_data: List[Dict]) -> QualityMetrics:
        metrics = QualityMetrics(entity="faculty", total_records=len(faculty_data))
        
        if not faculty_data:
            return metrics
        
        ids = []
        names = []
        empty_names = 0
        
        for f in faculty_data:
            f_id = f.get("id") or f.get("faculty_id")
            f_name = f.get("name", "").strip()
            
            if f_id:
                ids.append(f_id)
            if not f_name:
                empty_names += 1
            else:
                names.append(f_name)
        
        duplicates = [item for item, count in Counter(ids).items() if count > 1]
        metrics.duplicates_count = len(duplicates)
        
        if empty_names > 0:
            metrics.missing_fields["name"] = empty_names
            metrics.issues.append(f"{empty_names} faculty with empty names")
        
        metrics.completeness_percent = ((len(faculty_data) - empty_names) / len(faculty_data) * 100) if faculty_data else 0
        
        return metrics

    def verify_courses(self, course_data: List[Dict]) -> QualityMetrics:
        metrics = QualityMetrics(entity="courses", total_records=len(course_data))
        
        if not course_data:
            return metrics
        
        codes = []
        invalid_credits = 0
        
        for c in course_data:
            code = c.get("code") or c.get("course_id")
            if code:
                codes.append(code)
            
            try:
                credits = int(c.get("credits") or c.get("weekly_periods", 0))
                if credits <= 0:
                    invalid_credits += 1
            except:
                invalid_credits += 1
        
        duplicates = [item for item, count in Counter(codes).items() if count > 1]
        metrics.duplicates_count = len(duplicates)
        
        if invalid_credits > 0:
            metrics.missing_fields["credits"] = invalid_credits
            metrics.issues.append(f"{invalid_credits} courses with invalid credits")
        
        metrics.completeness_percent = ((len(course_data) - invalid_credits) / len(course_data) * 100) if course_data else 0
        
        return metrics

    def verify_rooms(self, room_data: List[Dict]) -> QualityMetrics:
        metrics = QualityMetrics(entity="rooms", total_records=len(room_data))
        
        if not room_data:
            return metrics
        
        room_ids = []
        invalid_capacity = 0
        
        for r in room_data:
            r_id = r.get("room_id")
            if r_id:
                room_ids.append(r_id)
            
            try:
                cap = int(r.get("capacity", 0))
                if cap <= 0:
                    invalid_capacity += 1
            except:
                invalid_capacity += 1
        
        duplicates = [item for item, count in Counter(room_ids).items() if count > 1]
        metrics.duplicates_count = len(duplicates)
        
        if invalid_capacity > 0:
            metrics.missing_fields["capacity"] = invalid_capacity
            metrics.issues.append(f"{invalid_capacity} rooms with invalid capacity")
        
        metrics.completeness_percent = ((len(room_data) - invalid_capacity) / len(room_data) * 100) if room_data else 0
        
        return metrics

    def verify_sections(self, section_data: List[Dict]) -> QualityMetrics:
        metrics = QualityMetrics(entity="sections", total_records=len(section_data))
        
        if not section_data:
            return metrics
        
        section_ids = []
        empty_sections = []
        
        for s in section_data:
            s_id = s.get("id") or s.get("section_id")
            if s_id:
                section_ids.append(s_id)
            
            try:
                count = int(s.get("student_count", 0))
                if count == 0:
                    empty_sections.append(s_id)
            except:
                pass
        
        metrics.orphan_records = empty_sections
        
        if empty_sections:
            metrics.issues.append(f"{len(empty_sections)} sections with 0 students")
        
        duplicates = [item for item, count in Counter(section_ids).items() if count > 1]
        metrics.duplicates_count = len(duplicates)
        
        metrics.completeness_percent = ((len(section_data) - len(empty_sections)) / len(section_data) * 100) if section_data else 0
        
        return metrics

    def verify_mappings(self, data: Dict) -> QualityMetrics:
        metrics = QualityMetrics(entity="mappings", total_records=len(data.get("faculty_course_map", [])))
        
        mappings = data.get("faculty_course_map", [])
        if not mappings:
            return metrics
        
        faculty_ids = {f.get("id") or f.get("faculty_id") for f in data.get("faculty", []) if f.get("id") or f.get("faculty_id")}
        course_codes = {c.get("code") or c.get("course_id") for c in data.get("courses", []) if c.get("code") or c.get("course_id")}
        section_ids = {s.get("id") or s.get("section_id") for s in data.get("sections", []) if s.get("id") or s.get("section_id")}
        
        broken_refs = []
        
        for m in mappings:
            f_id = m.get("faculty_id") or m.get("faculty_email")
            c_code = m.get("course_id")
            s_id = m.get("section_id")
            
            if f_id and f_id not in faculty_ids:
                broken_refs.append(f"Unknown faculty: {f_id}")
            if c_code and c_code not in course_codes:
                broken_refs.append(f"Unknown course: {c_code}")
            if s_id and s_id not in section_ids:
                broken_refs.append(f"Unknown section: {s_id}")
        
        if broken_refs:
            metrics.issues = broken_refs[:5]
        
        metrics.completeness_percent = ((len(mappings) - len(broken_refs)) / len(mappings) * 100) if mappings else 0
        
        return metrics

    def _aggregate_report(self, report: IntegrityReport, data: Dict):
        total_issues = sum(len(m.issues) for m in report.metrics.values())
        total_records = sum(m.total_records for m in report.metrics.values())
        
        avg_completeness = sum(m.completeness_percent for m in report.metrics.values()) / len(report.metrics) if report.metrics else 100
        
        report.overall_score = avg_completeness
        report.is_healthy = report.overall_score >= self.min_health_threshold and total_issues == 0
        
        for metrics in report.metrics.values():
            report.issues.extend(metrics.issues)
        
        report.summary = f"Health Score: {report.overall_score:.1f}/100 | Issues: {len(report.issues)}"
