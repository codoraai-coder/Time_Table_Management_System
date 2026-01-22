import os
import sys
from sqlalchemy import text

# Path setup
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../.."))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "backend"))

from dotenv import load_dotenv
load_dotenv()

from app.core.database import engine
from app.models import Base

def sync_db():
    print(">> Syncing Database Schema (Adopting New Architecture)...")
    
    # Support --force flag for automated sync
    force = "--force" in sys.argv
    if not force:
        confirm = input("This will DROP all tables and recreate them. Data in DB will be lost (CSV import needed). Proceed? (y/n): ")
        if confirm.lower() != 'y':
            print("Cancelled.")
            return

    try:
        Base.metadata.drop_all(bind=engine)
        print("[ok] Dropped all existing tables.")
        
        Base.metadata.create_all(bind=engine)
        print("[ok] Created all tables with new schema.")
        
        print("\nSUCCESS! Database is now in sync with the new architecture.")
        print("Next Step: Run 'python backend/scripts/import_pipeline.py' to reload data.")
        
    except Exception as e:
        print(f"[!] Error during sync: {e}")

if __name__ == "__main__":
    sync_db()
