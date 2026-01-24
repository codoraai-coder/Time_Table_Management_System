import os
import sys
import csv
from sqlalchemy.orm import Session
from dotenv import load_dotenv

# Path setup
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../.."))
if os.path.basename(project_root) == "backend":
    project_root = os.path.abspath(os.path.join(project_root, ".."))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "backend"))

load_dotenv()

from app.core.database import SessionLocal
from app.services.validator import ValidatorService
from app.services.import_service import ImportService
from app.models import Base

def load_csv(file_path: str) -> list:
    if not os.path.exists(file_path):
        return []
    with open(file_path, mode='r', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def run_pipeline(data_dir: str):
    print(f">> Starting Import Pipeline from: {data_dir}\n")
    
    # 1. Load Files
    data = {
        "faculty": load_csv(os.path.join(data_dir, "faculty.csv")),
        "courses": load_csv(os.path.join(data_dir, "courses.csv")),
        "rooms": load_csv(os.path.join(data_dir, "rooms.csv")),
        "sections": load_csv(os.path.join(data_dir, "sections.csv")),
        "faculty_course_map": load_csv(os.path.join(data_dir, "faculty_course_map.csv"))
    }
    
    # 2. Validate Structure & Integrity (Issue 4)
    validator = ValidatorService()
    val_result = validator.validate_structure(data)
    
    if not val_result.is_valid:
        print("[!] Pipeline Aborted. Validation Failed:")
        for err in val_result.errors:
            print(f"  - {err}")
        return

    print("[ok] Validation Passed.")

    # 3. Normalize & Persist (Issue 5)
    mock_mode = os.getenv("MOCK_DB", "false").lower() == "true"
    
    db = None
    if not mock_mode:
        try:
            db = SessionLocal()
        except Exception as e:
            print(f"[!] DB Connection Failed: {e}")
            print("[?] Switching to MOCK MODE for verification...")
            mock_mode = True

    try:
        importer = ImportService(db)
        
        print(f"\n--- Normalization Report {'(MOCK MODE)' if mock_mode else ''} ---")
        
        # Primary Entities
        f_count, f_logs = importer.process_faculty(data["faculty"], mock=mock_mode)
        for log in f_logs: print(f"  • {log}")
        
        c_count, c_logs = importer.process_courses(data["courses"], mock=mock_mode)
        for log in c_logs: print(f"  • {log}")
        
        r_count, r_logs = importer.process_rooms(data["rooms"], mock=mock_mode)
        for log in r_logs: print(f"  • {log}")
        
        # Dependent Entities
        s_count, s_logs = importer.process_sections(data["sections"], mock=mock_mode)
        for log in s_logs: print(f"  • {log}")
        
        m_count, m_logs = importer.process_assignments(data["faculty_course_map"], mock=mock_mode)
        for log in m_logs: print(f"  • {log}")
        
        print("\n--- Summary ---")
        print(f"  [ok] Faculty processed: {f_count}")
        print(f"  [ok] Courses processed: {c_count}")
        print(f"  [ok] Rooms processed:   {r_count}")
        print(f"  [ok] Sections processed: {s_count}")
        print(f"  [ok] Assignments processed: {m_count}")
        
        print(f"\n[DONE] {'Mock ' if mock_mode else ''}Success! Pipeline Complete.")
        
    finally:
        if db:
            db.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        target_dir = sys.argv[1]
    else:
        target_dir = os.path.join(os.path.dirname(__file__), "../data_templates")
    run_pipeline(target_dir)
