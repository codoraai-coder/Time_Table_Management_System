import sys
import os
import traceback

# Add current directory to path
sys.path.append(os.getcwd())

print("Attempting to import app.main...")

try:
    from app import main
    print("Successfully imported app.main")
except Exception as e:
    print(f"Error importing app.main: {e}")
    traceback.print_exc()

print("Debug script finished.")
