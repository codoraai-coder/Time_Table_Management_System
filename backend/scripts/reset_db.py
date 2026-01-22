import os
import sys

# Path setup
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../.."))
if os.path.basename(project_root) == "backend":
    project_root = os.path.abspath(os.path.join(project_root, ".."))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "backend"))

from dotenv import load_dotenv
load_dotenv()

from app.core.database import engine
from app.models import Base

def reset_db():
    print("⚠️  DANGER: Dropping all tables in the database...")
    Base.metadata.drop_all(bind=engine)
    print("✓ Dropped all tables.")
    
    print("🔨 Creating all tables with updated schema...")
    Base.metadata.create_all(bind=engine)
    print("✓ Created all tables.")

if __name__ == "__main__":
    reset_db()
