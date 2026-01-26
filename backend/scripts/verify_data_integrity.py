import os
import sys
import csv
import json
import argparse
from pathlib import Path

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../.."))
if os.path.basename(project_root) == "backend":
    project_root = os.path.abspath(os.path.join(project_root, ".."))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "backend"))

from app.services.data_integrity_verifier import DataIntegrityVerifier
from app.services.normalization_verifier import NormalizationVerifier
from app.config.verification import INTEGRITY_VERIFICATION

def load_csv(file_path: str) -> list:
    if not os.path.exists(file_path):
        return []
    with open(file_path, mode='r', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def generate_report(data_dir: str, output_file: str):
    print(f"Verifying data from: {data_dir}")
    
    data = {
        "faculty": load_csv(os.path.join(data_dir, "faculty.csv")),
        "courses": load_csv(os.path.join(data_dir, "courses.csv")),
        "rooms": load_csv(os.path.join(data_dir, "rooms.csv")),
        "sections": load_csv(os.path.join(data_dir, "sections.csv")),
        "faculty_course_map": load_csv(os.path.join(data_dir, "faculty_course_map.csv")),
    }
    
    verifier = DataIntegrityVerifier()
    integrity_report = verifier.verify_all(data)
    
    norm_config = INTEGRITY_VERIFICATION["fuzzy_match"]
    norm_verifier = NormalizationVerifier(
        faculty_threshold=norm_config["faculty_threshold"],
        course_threshold=norm_config["course_threshold"]
    )
    clustering_report = norm_verifier.get_clustering_report(data)
    
    report_md = _format_report(integrity_report, clustering_report, data)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report_md)
    
    print(f"✅ Report generated: {output_file}")
    print(f"Overall Health: {integrity_report.overall_score:.1f}/100")
    print(f"Status: {'PASS ✅' if integrity_report.is_healthy else 'FAIL ⚠️'}")

def _format_report(integrity_report, clustering_report, data) -> str:
    report = "# Data Integrity Verification Report\n\n"
    
    status = "✅ PASS" if integrity_report.is_healthy else "⚠️ WARNING"
    report += f"## Status: {status}\n\n"
    report += f"**Health Score:** {integrity_report.overall_score:.1f}/100\n\n"
    
    report += "## Data Quality Metrics\n\n"
    report += "| Entity | Total | Duplicates | Completeness | Status |\n"
    report += "|--------|-------|------------|--------------|--------|\n"
    
    for entity, metrics in integrity_report.metrics.items():
        status_icon = "✅" if metrics.completeness_percent >= 90 else "⚠️"
        report += f"| {entity} | {metrics.total_records} | {metrics.duplicates_count} | {metrics.completeness_percent:.1f}% | {status_icon} |\n"
    
    report += "\n## Issues Found\n\n"
    if integrity_report.issues:
        for issue in integrity_report.issues:
            report += f"- {issue}\n"
    else:
        report += "No issues found ✅\n"
    
    report += "\n## Normalization Clustering\n\n"
    if clustering_report.faculty_clusters:
        report += f"**Faculty Clusters:** {len(clustering_report.faculty_clusters)}\n"
        for cluster in clustering_report.faculty_clusters[:5]:
            report += f"- Canonical: '{cluster.canonical}' | Confidence: {cluster.confidence:.2f} | Names: {', '.join(cluster.names[:3])}\n"
    
    if clustering_report.course_clusters:
        report += f"\n**Course Clusters:** {len(clustering_report.course_clusters)}\n"
        for cluster in clustering_report.course_clusters[:5]:
            report += f"- Canonical: '{cluster.canonical}' | Confidence: {cluster.confidence:.2f} | Names: {', '.join(cluster.names[:3])}\n"
    
    report += f"\n**Overall Clustering Confidence:** {clustering_report.overall_confidence:.2f}\n"
    
    report += "\n## Data Summary\n\n"
    report += f"- Faculty: {len(data['faculty'])}\n"
    report += f"- Courses: {len(data['courses'])}\n"
    report += f"- Rooms: {len(data['rooms'])}\n"
    report += f"- Sections: {len(data['sections'])}\n"
    report += f"- Mappings: {len(data['faculty_course_map'])}\n"
    
    report += f"\n## Verdict\n\n"
    if integrity_report.is_healthy:
        report += "✅ **Data is clean and ready for import**\n"
    else:
        report += "⚠️ **Review issues before proceeding with import**\n"
    
    return report

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Verify data integrity")
    parser.add_argument("--data-dir", required=True, help="Directory containing CSV files")
    parser.add_argument("--output", required=True, help="Output report file")
    
    args = parser.parse_args()
    generate_report(args.data_dir, args.output)
