import csv
import io
from typing import List, Dict, Any, Type
from pydantic import BaseModel, ValidationError
from app.schemas.validation import FacultyRow, CourseRow, RoomRow, SectionRow
from app.services.explainer import HumanExplainer

class ValidationService:
    """Service to validate uploaded CSV files against Pydantic schemas."""

    def __init__(self):
        self.schema_map = {
            'faculty': FacultyRow,
            'courses': CourseRow,
            'rooms': RoomRow,
            'sections': SectionRow
        }
        self.explainer = HumanExplainer()

    async def validate_csv(self, file_content: bytes, file_type: str) -> Dict[str, Any]:
        """
        Validates a CSV file.
        
        Args:
            file_content: Raw bytes of the CSV file
            file_type: Type of file ('faculty', 'courses', 'rooms', 'sections')
            
        Returns:
            Dict containing 'valid' (bool), 'errors' (list), 'stats' (dict)
        """
        if file_type not in self.schema_map:
            raise ValueError(f"Unknown file type: {file_type}")

        schema_class = self.schema_map[file_type]
        errors = []
        valid_rows = 0
        
        try:
            # Decode bytes to string
            content_str = file_content.decode('utf-8')
            # Create CSV reader
            reader = csv.DictReader(io.StringIO(content_str))
            
            # Check for empty file or missing headers
            if not reader.fieldnames:
                return {
                    "valid": False,
                    "errors": ["File is empty or missing headers"],
                    "stats": {"total_rows": 0, "valid_rows": 0}
                }

            # Validate header columns exist in schema (case-insensitive check could be added here)
            # For strict mode, we expect exact matches or we map them. 
            # For now, let Pydantic handle missing fields validation.
            
            row_index = 0
            for row in reader:
                row_index += 1
                try:
                    # Clean keys (strip whitespace)
                    clean_row = {k.strip(): v.strip() for k, v in row.items() if k}
                    schema_class(**clean_row)
                    valid_rows += 1
                except ValidationError as e:
                    for err in e.errors():
                        explanation = self.explainer.explain_pydantic_error(err)
                        error_msg = f"Row {row_index}: {explanation.message}"
                        if explanation.suggestion:
                            error_msg += f" → {explanation.suggestion}"
                        errors.append(error_msg)
                except Exception as e:
                    errors.append(f"Row {row_index}: Unexpected error - {str(e)}")

        except UnicodeDecodeError:
            return {
                "valid": False,
                "errors": ["File must be valid UTF-8 text"],
                "stats": {"total_rows": 0, "valid_rows": 0}
            }
        except Exception as e:
            return {
                "valid": False,
                "errors": [f"Failed to parse CSV: {str(e)}"],
                "stats": {"total_rows": 0, "valid_rows": 0}
            }

        return {
            "valid": len(errors) == 0,
            "errors": errors[:50],  # Limit error output
            "stats": {
                "total_rows": row_index,
                "valid_rows": valid_rows
            }
        }
