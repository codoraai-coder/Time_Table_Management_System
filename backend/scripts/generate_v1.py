import sys
import os
import json
from datetime import time

# Path setup
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../.."))
if os.path.basename(project_root) == "backend":
    project_root = os.path.abspath(os.path.join(project_root, ".."))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "backend"))

from dotenv import load_dotenv
load_dotenv()

from app.core.database import SessionLocal
from app.services.timetable_manager import TimetableManager
from app.models import Timeslot, Assignment, TimetableVersion
from sqlalchemy import text
import traceback

def run():
    print(">> Starting Timetable Generation (Production Mode)...")
    db = SessionLocal()
    try:
        # 0. Test database connection
        print("[*] Testing database connection...")
        db.execute(text("SELECT 1"))
        print("[ok] Database connection verified.")
        # 1. Clear previous results (keep imported assignments as they are the schedule inputs)
        db.query(TimetableVersion).delete()
        db.commit()
        print("[ok] Cleared previous timetable versions.")

        # 2. Ensure Timeslots exist
        slot_count = db.query(Timeslot).count()
        if slot_count == 0:
            print("(!) No timeslots found. Generating standard Mon-Fri (8:00 - 18:00) slots...")
            slots_to_add = []
            for day in range(5):  # Mon to Fri
                for hour in range(8, 18):
                    start = time(hour, 0)
                    end = time(hour + 1, 0)
                    slots_to_add.append(Timeslot(day=day, start_time=start, end_time=end))
            db.add_all(slots_to_add)
            db.commit()
            print(f"[ok] Created {len(slots_to_add)} timeslots.")

        # 3. Run the Manager
        manager = TimetableManager(db)
        version = manager.generate_timetable(version_number=1)

        if version:
            print(f"\n[ok] SUCCESS! Timetable V1 Created from imported data.")
            
            # Save output to a JSON file for the user
            output_path = os.path.join(project_root, "backend/timetable_output.json")
            with open(output_path, "w") as f:
                json.dump(version.snapshot_data, f, indent=2)
            print(f"[ok] Full JSON output saved to: backend/timetable_output.json")
            
            # Show a few sample assignments (grouped structure)
            sections_dict = version.snapshot_data.get("sections", {})
            if sections_dict:
                print("\nSample Schedule (First Section):")
                first_sec = list(sections_dict.keys())[0]
                print(f"  Section: {first_sec}")
                for day, sessions in sections_dict[first_sec].items():
                    if sessions:
                        print(f"    {day}: {len(sessions)} periods assigned")
        else:
            print("\n[!] Failed to generate timetable. Check validation logs or feasibility.")

    except Exception as e:
        print(f"[!] Error during generation: {e}")
        print("\n[DEBUG] Full traceback:")
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    run()
