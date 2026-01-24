"""
Generate timetable only (no export).
Usage:
    python scripts/generate.py
"""
import sys
import os
from dotenv import load_dotenv
# Path setup
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../.."))
if os.path.basename(project_root) == "backend":
    project_root = os.path.abspath(os.path.join(project_root, ".."))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "backend"))
load_dotenv()
from app.services.timetable_manager import TimetableManager
from app.core.database import SessionLocal
from app.models import Timeslot, TimetableVersion

def main():
    db = SessionLocal()
    try:
        print(">> Checking Timeslots...\n")
        slot_count = db.query(Timeslot).count()
        if slot_count == 0:
            print("(!) No timeslots found. Generating standard Mon-Fri (8:00 - 18:00) slots...")
            slots_to_add = []
            for day in range(5):
                for hour in range(8, 18):
                    from datetime import time
                    start = time(hour, 0)
                    end = time(hour + 1, 0)
                    slots_to_add.append(Timeslot(day=day, start_time=start, end_time=end))
            db.add_all(slots_to_add)
            db.commit()
            print(f"[OK] Created {len(slots_to_add)} timeslots.\n")
        else:
            print(f"[OK] Found {slot_count} existing timeslots.\n")
        db.query(TimetableVersion).delete()
        db.commit()
        print(">> Generating Timetable...\n")
        manager = TimetableManager(db)
        timetable_version = manager.generate_timetable()
        if not timetable_version:
            print("[-] Solver failed to generate timetable")
            return False
        print(f"[OK] Timetable generated successfully!\n  Version ID: {timetable_version.id}")
        return True
    except Exception as e:
        print(f"[-] Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()
if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
