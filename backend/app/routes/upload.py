from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Dict, Any, List
from app.services.validator_row import ValidationService
import uuid

router = APIRouter()
validator = ValidationService()

@router.post("/")
async def upload_files(
    files: List[UploadFile] = File(...)
) -> Dict[str, Any]:
    """
    Handle Generic File Upload (Zip or multiple CSVs).
    Currently mocks the processing and validation for demonstration.
    """
    # In a real implementation:
    # 1. Save zip / files to temp dir
    # 2. Extract if zip
    # 3. Validate each required file
    # 4. Return aggregated results
    
    upload_id = str(uuid.uuid4())
    
    # Mock Validation Logic based on filenames
    details = {
        "files_received": [f.filename for f in files],
        "status": "processed",
        "warnings": [],
        "errors": []
    }
    
    return {
        "status": "success",
        "upload_id": upload_id,
        "message": "Files uploaded and processed successfully",
        "details": details
    }

@router.post("/validate/{file_type}")
async def validate_file(
    file_type: str,
    file: UploadFile = File(...)
) -> Dict[str, Any]:
    """
    Validate an uploaded CSV file.
    
    file_type must be one of: faculty, courses, rooms, sections
    """
    if file_type not in ['faculty', 'courses', 'rooms', 'sections']:
        raise HTTPException(status_code=400, detail="Invalid file type. Must be faculty, courses, rooms, or sections.")

    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV.")

    content = await file.read()
    result = await validator.validate_csv(content, file_type)
    
    if not result['valid']:
        # Return 422 Unprocessable Entity if validation fails, or 200 with details? 
        # Usually 200 with error details is better for bulk upload UIs.
        return {
            "status": "error",
            "message": "Validation failed",
            "details": result
        }

    return {
        "status": "success",
        "message": "Validation successful",
        "details": result
    }
