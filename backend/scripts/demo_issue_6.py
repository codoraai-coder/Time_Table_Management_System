import io
import csv
import sys
import os
import asyncio

# Add the backend directory to sys.path to resolve 'app' module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.validator_row import ValidationService
from app.services.explainer import HumanExplainer


async def demo_feature():
    print("=" * 80)
    print("DEMO: HUMAN-READABLE VALIDATION EXPLANATIONS (#6)")
    print("=" * 80)
    
    validator = ValidationService()
    
    # 1. Scenario: Messy Faculty Data
    # Errors: 
    # - Row 1: Name too short ('A')
    # - Row 2: Invalid email ('not-an-email')
    messy_csv = """name,email
A,valid@college.edu
Dr. Smith,not-an-email
"""
    
    print("\n[STEP 1] Validating messy faculty CSV...")
    result = await validator.validate_csv(messy_csv.encode('utf-8'), 'faculty')
    
    print(f"\nResult: {'❌ FAILED' if not result['valid'] else '✅ PASSED'}")
    print("\nCaptured Explanations:")
    for error in result['errors']:
        print(f"  - {error}")

    # 2. Use Case Explanation
    print("\n" + "=" * 80)
    print("USE CASE: IMPROVING ADMIN EXPERIENCE")
    print("-" * 80)
    print("WITHOUT THIS FEATURE (Technical):")
    print("  Row 1: email - value_error.email: value is not a valid email address")
    print("\nWITH THIS FEATURE (Human-Friendly):")
    print("  Row 1: The email address for email is invalid. → Use the format: name@college.edu")
    
    print("\n" + "=" * 80)
    print("INTEGRATION: HOW IT WORKS IN THE APP")
    print("-" * 80)
    print("1. Admin uploads file to Frontend.")
    print("2. Frontend calls POST /api/upload/validate/faculty.")
    print("3. Backend 'ValidationService' runs Pydantic checks.")
    print("4. On error, 'HumanExplainer' translates technical code to a sentence.")
    print("5. Frontend displays 'message' and 'suggestion' to the Admin.")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(demo_feature())
