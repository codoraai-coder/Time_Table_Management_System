from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Dict, Any, List
from app.services.validator_row import ValidationService
import uuid

router = APIRouter()
validator = ValidationService()

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


@router.post("/")
async def upload_files(files: List[UploadFile] = File(...)) -> Dict[str, Any]:
    """
    Batch upload endpoint accepted by the frontend.
    Accepts multiple files under the form key `files`, runs CSV
    validation for known CSV filenames, and returns an `upload_id`
    with per-file results.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")

    results: Dict[str, Any] = {}
    filename_map = {
        'faculty.csv': 'faculty',
        'courses.csv': 'courses',
        'rooms.csv': 'rooms',
        'sections.csv': 'sections',
        'faculty_course_map.csv': 'faculty_course_map',
        'time_config.json': 'time_config'
    }

    for f in files:
        name = f.filename
        try:
            content = await f.read()
        except Exception as e:
            results[name] = {"status": "error", "message": f"Failed to read file: {e}"}
            continue

        key = name.lower()
        file_type = filename_map.get(key)

        if file_type in ['faculty', 'courses', 'rooms', 'sections']:
            try:
                res = await validator.validate_csv(content, file_type)
                results[name] = {"status": "validated", "details": res}
            except Exception as e:
                results[name] = {"status": "error", "message": str(e)}
        else:
            results[name] = {"status": "uploaded"}

    upload_id = str(uuid.uuid4())
    return {
        "status": "success",
        "message": "Files processed",
        "upload_id": upload_id,
        "results": results
    }
