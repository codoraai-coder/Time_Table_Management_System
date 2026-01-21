import requests
import io

BASE_URL = "http://localhost:8000/api/upload/validate"

# Mock some CSV content
valid_faculty_csv = """name,email
Dr. Smith,smith@college.edu
Prof. Jones,jones@college.edu
"""

invalid_faculty_csv = """name,email
,bad_email
Valid Name,
"""

def test_upload(file_type, content):
    print(f"\n--- Testing {file_type} ---")
    files = {'file': ('test.csv', content, 'text/csv')}
    try:
        response = requests.post(f"{BASE_URL}/{file_type}", files=files)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Failed to connect: {e}")
        print("Make sure the backend is running!")

if __name__ == "__main__":
    print("WARNING: This script expects the backend server to be running on localhost:8000")
    print("If it is not running, run: uvicorn app.main:app --reload")
    
    # 1. Test Valid Faculty
    test_upload('faculty', valid_faculty_csv)
    
    # 2. Test Invalid Faculty
    test_upload('faculty', invalid_faculty_csv)
