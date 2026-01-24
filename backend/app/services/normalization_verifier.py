from dataclasses import dataclass, field
from typing import List, Dict, Tuple
from collections import defaultdict

try:
    from fuzzywuzzy import fuzz
    FUZZYWUZZY_AVAILABLE = True
except ImportError:
    FUZZYWUZZY_AVAILABLE = False

@dataclass
class Cluster:
    cluster_id: int
    names: List[str]
    canonical: str
    confidence: float
    entity_type: str

@dataclass
class ClusteringReport:
    faculty_clusters: List[Cluster] = field(default_factory=list)
    course_clusters: List[Cluster] = field(default_factory=list)
    unmatched_faculty: List[str] = field(default_factory=list)
    unmatched_courses: List[str] = field(default_factory=list)
    overall_confidence: float = 0.0

class NormalizationVerifier:
    def __init__(self, faculty_threshold: int = 80, course_threshold: int = 75):
        self.faculty_threshold = faculty_threshold
        self.course_threshold = course_threshold
        self.fuzzywuzzy_available = FUZZYWUZZY_AVAILABLE

    def get_clustering_report(self, data: Dict) -> ClusteringReport:
        report = ClusteringReport()
        
        if not self.fuzzywuzzy_available:
            return report
        
        faculty_names = self._extract_faculty_names(data.get("faculty", []))
        course_names = self._extract_course_names(data.get("courses", []))
        
        report.faculty_clusters, report.unmatched_faculty = self._cluster_names(
            faculty_names, self.faculty_threshold, "faculty"
        )
        
        report.course_clusters, report.unmatched_courses = self._cluster_names(
            course_names, self.course_threshold, "course"
        )
        
        all_confidences = [c.confidence for c in report.faculty_clusters + report.course_clusters]
        report.overall_confidence = sum(all_confidences) / len(all_confidences) if all_confidences else 0.0
        
        return report

    def _extract_faculty_names(self, faculty_data: List[Dict]) -> List[str]:
        names = []
        for f in faculty_data:
            name = f.get("name", "").strip()
            if name:
                names.append(name)
        return names

    def _extract_course_names(self, course_data: List[Dict]) -> List[str]:
        names = []
        for c in course_data:
            name = c.get("name", "").strip()
            if name:
                names.append(name)
        return names

    def _cluster_names(self, names: List[str], threshold: int, entity_type: str) -> Tuple[List[Cluster], List[str]]:
        if not names:
            return [], []
        
        clusters = defaultdict(list)
        unmatched = []
        assigned = set()
        cluster_id = 0
        
        for i, name1 in enumerate(names):
            if i in assigned:
                continue
            
            cluster = [name1]
            scores = []
            
            for j, name2 in enumerate(names):
                if i != j and j not in assigned:
                    score = fuzz.token_set_ratio(name1.lower(), name2.lower())
                    if score >= threshold:
                        cluster.append(name2)
                        assigned.add(j)
                        scores.append(score)
            
            if len(cluster) > 1:
                assigned.add(i)
                canonical = max(cluster, key=len)
                avg_confidence = sum(scores) / len(scores) if scores else 100.0
                clusters[cluster_id] = Cluster(
                    cluster_id=cluster_id,
                    names=cluster,
                    canonical=canonical,
                    confidence=avg_confidence / 100.0,
                    entity_type=entity_type
                )
                cluster_id += 1
            else:
                unmatched.append(name1)
        
        for i, name in enumerate(names):
            if i not in assigned and name not in unmatched:
                unmatched.append(name)
        
        return list(clusters.values()), unmatched
