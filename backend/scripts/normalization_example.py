"""
Quick Start Example for Normalization Agent.

This script demonstrates the complete workflow:
1. Analyze messy data
2. Review suggestions
3. Apply confirmations
4. Get final mapping

Usage:
    python -m backend.scripts.normalization_example
"""

import sys
import os
import logging
from json import dumps

# Setup path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../.."))
if os.path.basename(project_root) == "backend":
    project_root = os.path.abspath(os.path.join(project_root, ".."))

sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "backend"))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    from app.services.normalization_agent import (
        NormalizationAgent,
        NormalizationRequest
    )
except ImportError:
    from backend.app.services.normalization_agent import (
        NormalizationAgent,
        NormalizationRequest
    )


def main():
    """Run example normalization workflow"""
    
    print("\n" + "="*80)
    print("NORMALIZATION AGENT - QUICK START EXAMPLE")
    print("="*80 + "\n")
    
    # ========== STEP 1: Messy Upload Data ==========
    print("STEP 1: Messy Upload Data")
    print("-" * 80)
    
    faculty_names = [
        "Dr. Smith",
        "Dr. John Smith",
        "smith, john",
        "DR SMITH",
        "Prof. Johnson",
        "Prof. Mike Johnson",
        "Dr. Sarah Williams"
    ]
    
    course_names = [
        "DBMS LAB",
        "Database Lab",
        "DB Systems",
        "Data Structures",
        "ds",
        "Data Structures & Algorithms",
        "Algorithms"
    ]
    
    print("\nFaculty Names (messy):")
    for i, name in enumerate(faculty_names, 1):
        print(f"  {i}. {name}")
    
    print("\nCourse Names (messy):")
    for i, name in enumerate(course_names, 1):
        print(f"  {i}. {name}")
    
    # ========== STEP 2: Analyze ==========
    print("\n" + "="*80)
    print("STEP 2: Analyze - Detect Similar Names")
    print("-" * 80)
    
    try:
        agent = NormalizationAgent(similarity_threshold=80.0)
        request = NormalizationRequest(
            faculty_names=faculty_names,
            course_names=course_names,
            similarity_threshold=80.0
        )
        response = agent.analyze(request)
        
        print(f"\n[OK] Analysis complete!")
        print(f"  Faculty clusters detected: {len(response.faculty_suggestions)}")
        print(f"  Course clusters detected: {len(response.course_suggestions)}")
        
        # ========== STEP 3: Display Suggestions ==========
        print("\n" + "="*80)
        print("STEP 3: Review Suggestions - Faculty")
        print("-" * 80)
        
        for i, suggestion in enumerate(response.faculty_suggestions, 1):
            print(f"\n  Suggestion #{i} (Cluster ID: {suggestion.cluster_id})")
            print(f"    Similar names: {', '.join(suggestion.detected_names)}")
            print(f"    Suggested canonical: '{suggestion.suggested_canonical}'")
            print(f"    Confidence: {suggestion.confidence:.0%}")
            print(f"    Status: {suggestion.status.value}")
        
        print("\n" + "="*80)
        print("STEP 3: Review Suggestions - Courses")
        print("-" * 80)
        
        for i, suggestion in enumerate(response.course_suggestions, 1):
            print(f"\n  Suggestion #{i} (Cluster ID: {suggestion.cluster_id})")
            print(f"    Similar names: {', '.join(suggestion.detected_names)}")
            print(f"    Suggested canonical: '{suggestion.suggested_canonical}'")
            print(f"    Confidence: {suggestion.confidence:.0%}")
            print(f"    Status: {suggestion.status.value}")
        
        # ========== STEP 4: User Confirmation ==========
        print("\n" + "="*80)
        print("STEP 4: User Confirmation")
        print("-" * 80)
        
        print("\n[OK] Simulating user review...")
        print("  - All faculty suggestions: ACCEPTED")
        print("  - All course suggestions: ACCEPTED")
        
        # Build confirmations
        faculty_confirmations = {
            s.cluster_id: "accepted" 
            for s in response.faculty_suggestions
        }
        course_confirmations = {
            s.cluster_id: "accepted" 
            for s in response.course_suggestions
        }
        
        # ========== STEP 5: Apply & Finalize ==========
        print("\n" + "="*80)
        print("STEP 5: Apply Confirmations & Finalize Mapping")
        print("-" * 80)
        
        final_mapping = agent.finalize_mapping(
            response,
            faculty_confirmations,
            course_confirmations,
            version=1
        )
        
        print(f"\n[OK] Mapping finalized! Version: {final_mapping.version}")
        print(f"  Faculty mappings created: {len(final_mapping.faculty_mapping)}")
        print(f"  Course mappings created: {len(final_mapping.course_mapping)}")
        
        # ========== STEP 6: Display Final Mapping ==========
        print("\n" + "="*80)
        print("STEP 6: Final Mapping - Faculty")
        print("-" * 80)
        
        for original, canonical in final_mapping.faculty_mapping.items():
            if original != canonical:
                print(f"\n  '{original}'")
                print(f"    --> normalize to -->")
                print(f"  '{canonical}'")
        
        print("\n" + "="*80)
        print("STEP 6: Final Mapping - Courses")
        print("-" * 80)
        
        for original, canonical in final_mapping.course_mapping.items():
            if original != canonical:
                print(f"\n  '{original}'")
                print(f"    --> normalize to -->")
                print(f"  '{canonical}'")
        
        # ========== JSON Output ==========
        print("\n" + "="*80)
        print("STEP 7: JSON Output (For API Response)")
        print("-" * 80)
        
        mapping_dict = final_mapping.to_dict()
        print("\n" + dumps(mapping_dict, indent=2))
        
        # ========== Summary ==========
        print("\n" + "="*80)
        print("SUMMARY")
        print("="*80)
        
        print(f"""
[OK] Normalization workflow completed successfully!

Results:
  * Faculty names: {len(faculty_names)} -> {len(set(final_mapping.faculty_mapping.values()))} canonical
  * Course names: {len(course_names)} -> {len(set(final_mapping.course_mapping.values()))} canonical
  
Key Design Principles:
  [OK] No silent auto-fixes (explicit user confirmation required)
  [OK] Structured JSON output for easy integration
  [OK] Confidence scores for decision support
  [OK] Auditable and reversible

Next Steps:
  1. Apply final_mapping to uploaded data (replace messy names)
  2. Insert normalized data into database
  3. Run solver to generate timetable
        """)
        
    except Exception as e:
        logger.exception(f"Error during normalization: {e}")
        print(f"\n[ERROR] {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
