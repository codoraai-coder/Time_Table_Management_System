"""
FastAPI Router for Normalization Agent endpoints.

Provides API endpoints for:
1. POST /analyze - Analyze messy data and get suggestions
2. POST /apply-confirmations - Apply user confirmations and get final mapping
"""

import logging
from typing import Dict, List, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field, validator

from app.services.normalization_agent import (
    NormalizationAgent,
    NormalizationRequest,
    ConfirmationStatus,
    EntityType
)

logger = logging.getLogger(__name__)

# ============= Pydantic Models for API =============

class NormalizationSuggestionResponse(BaseModel):
    """API response model for a single suggestion"""
    cluster_id: int = Field(..., description="Cluster identifier within entity type")
    detected_names: List[str] = Field(..., description="Similar names detected in this cluster")
    suggested_canonical: str = Field(..., description="Recommended canonical name")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score 0.0-1.0")
    status: str = Field(
        default="pending_confirmation",
        description="Current status: pending_confirmation, accepted, rejected"
    )
    entity_type: str = Field(..., description="Entity type: faculty or course")

    class Config:
        schema_extra = {
            "example": {
                "cluster_id": 0,
                "detected_names": ["Dr. Smith", "Dr. John Smith"],
                "suggested_canonical": "Dr. John Smith",
                "confidence": 0.95,
                "status": "pending_confirmation",
                "entity_type": "faculty"
            }
        }


class AnalyzeRequestAPI(BaseModel):
    """API request model for normalization analysis"""
    faculty_names: List[str] = Field(
        default_factory=list,
        description="List of faculty names from upload"
    )
    course_names: List[str] = Field(
        default_factory=list,
        description="List of course names from upload"
    )
    similarity_threshold: float = Field(
        default=80.0,
        ge=0.0,
        le=100.0,
        description="Minimum fuzzy match score (0-100) to consider names similar"
    )

    @validator("faculty_names", "course_names", pre=True)
    def filter_empty_strings(cls, v):
        """Remove empty strings from name lists"""
        return [name.strip() for name in v if name and name.strip()]

    class Config:
        schema_extra = {
            "example": {
                "faculty_names": ["Dr. Smith", "Dr. John Smith", "smith, john"],
                "course_names": ["DBMS LAB", "Database Lab"],
                "similarity_threshold": 80.0
            }
        }


class AnalyzeResponseAPI(BaseModel):
    """API response model for normalization analysis"""
    faculty_suggestions: List[NormalizationSuggestionResponse]
    course_suggestions: List[NormalizationSuggestionResponse]
    analysis_timestamp: str = Field(..., description="ISO format timestamp")
    request_id: Optional[str] = Field(None, description="Optional tracking ID")

    class Config:
        schema_extra = {
            "example": {
                "faculty_suggestions": [
                    {
                        "cluster_id": 0,
                        "detected_names": ["Dr. Smith", "Dr. John Smith"],
                        "suggested_canonical": "Dr. John Smith",
                        "confidence": 0.95,
                        "status": "pending_confirmation",
                        "entity_type": "faculty"
                    }
                ],
                "course_suggestions": [],
                "analysis_timestamp": "2026-01-19T10:30:00Z",
                "request_id": None
            }
        }


class ConfirmationRequestAPI(BaseModel):
    """API request model for applying confirmations"""
    faculty_confirmations: Dict[int, str] = Field(
        default_factory=dict,
        description='Map cluster_id to "accepted" or "rejected"'
    )
    course_confirmations: Dict[int, str] = Field(
        default_factory=dict,
        description='Map cluster_id to "accepted" or "rejected"'
    )

    @validator("faculty_confirmations", "course_confirmations", pre=True)
    def validate_confirmation_values(cls, v):
        """Ensure all values are 'accepted' or 'rejected'"""
        if not isinstance(v, dict):
            return v
        for cluster_id, status in v.items():
            if status.lower() not in ["accepted", "rejected"]:
                raise ValueError(
                    f"Confirmation status must be 'accepted' or 'rejected', got '{status}'"
                )
        return v

    class Config:
        schema_extra = {
            "example": {
                "faculty_confirmations": {"0": "accepted"},
                "course_confirmations": {"0": "accepted"}
            }
        }


class FinalMappingResponseAPI(BaseModel):
    """API response model for final applied mapping"""
    final_faculty_mapping: Dict[str, str] = Field(
        ...,
        description="Mapping of original faculty names to canonical names"
    )
    final_course_mapping: Dict[str, str] = Field(
        ...,
        description="Mapping of original course names to canonical names"
    )
    applied_timestamp: str = Field(..., description="ISO format timestamp when mapping was applied")
    version: int = Field(..., description="Mapping version number")

    class Config:
        schema_extra = {
            "example": {
                "final_faculty_mapping": {
                    "Dr. Smith": "Dr. John Smith",
                    "smith, john": "Dr. John Smith"
                },
                "final_course_mapping": {
                    "DBMS LAB": "Database Systems Lab"
                },
                "applied_timestamp": "2026-01-19T10:30:00Z",
                "version": 1
            }
        }


# ============= API Router =============

router = APIRouter(
    prefix="/api/normalization",
    tags=["Normalization"],
    responses={
        400: {"description": "Invalid request parameters"},
        500: {"description": "Internal server error"}
    }
)


@router.post(
    "/analyze",
    response_model=AnalyzeResponseAPI,
    summary="Analyze messy data for normalization",
    description="Detect similar names (faculty, courses) using fuzzy matching. "
                "Returns suggestions awaiting user confirmation.",
    status_code=status.HTTP_200_OK
)
async def analyze_upload(request: AnalyzeRequestAPI) -> AnalyzeResponseAPI:
    """
    Analyze uploaded data for name normalization.

    **Process:**
    1. Validates input faculty and course names
    2. Clusters similar names using fuzzy matching (token_set_ratio)
    3. Selects canonical name for each cluster (longest/most descriptive)
    4. Calculates confidence score based on cluster size
    5. Returns suggestions with status = "pending_confirmation"

    **Key Design:**
    - No silent auto-fixes (all suggestions require explicit confirmation)
    - Structured JSON output for easy integration
    - Confidence scores to help with decision-making

    **Response includes:**
    - Faculty suggestions (if similar faculty names detected)
    - Course suggestions (if similar course names detected)
    - Analysis timestamp (ISO 8601 format)

    **Example:**
    ```
    Request:
    {
      "faculty_names": ["Dr. Smith", "Dr. John Smith"],
      "course_names": ["DBMS LAB", "Database Lab"],
      "similarity_threshold": 80.0
    }

    Response:
    {
      "faculty_suggestions": [{
        "cluster_id": 0,
        "detected_names": ["Dr. Smith", "Dr. John Smith"],
        "suggested_canonical": "Dr. John Smith",
        "confidence": 0.95,
        "status": "pending_confirmation",
        "entity_type": "faculty"
      }],
      "course_suggestions": [...],
      "analysis_timestamp": "2026-01-19T10:30:00Z"
    }
    ```
    """
    try:
        logger.info(
            f"Analyzing upload: {len(request.faculty_names)} faculty, "
            f"{len(request.course_names)} courses"
        )

        # Initialize agent
        agent = NormalizationAgent(similarity_threshold=request.similarity_threshold)

        # Analyze
        internal_request = NormalizationRequest(
            faculty_names=request.faculty_names,
            course_names=request.course_names,
            similarity_threshold=request.similarity_threshold
        )
        response = agent.analyze(internal_request)

        # Transform to API response
        faculty_suggestions = [
            NormalizationSuggestionResponse(
                cluster_id=s.cluster_id,
                detected_names=s.detected_names,
                suggested_canonical=s.suggested_canonical,
                confidence=s.confidence,
                status=s.status.value,
                entity_type=s.entity_type.value
            )
            for s in response.faculty_suggestions
        ]

        course_suggestions = [
            NormalizationSuggestionResponse(
                cluster_id=s.cluster_id,
                detected_names=s.detected_names,
                suggested_canonical=s.suggested_canonical,
                confidence=s.confidence,
                status=s.status.value,
                entity_type=s.entity_type.value
            )
            for s in response.course_suggestions
        ]

        result = AnalyzeResponseAPI(
            faculty_suggestions=faculty_suggestions,
            course_suggestions=course_suggestions,
            analysis_timestamp=response.analysis_timestamp,
            request_id=response.request_id
        )

        logger.info(
            f"Analysis complete: {len(faculty_suggestions)} faculty suggestions, "
            f"{len(course_suggestions)} course suggestions"
        )
        return result

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Validation error: {str(e)}"
        )
    except ImportError as e:
        logger.error(f"Missing dependency: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Normalization service not properly configured. "
                   "Missing fuzzywuzzy dependency."
        )
    except Exception as e:
        logger.exception(f"Unexpected error during analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during analysis"
        )


@router.post(
    "/apply-confirmations",
    response_model=FinalMappingResponseAPI,
    summary="Apply user confirmations and generate final mapping",
    description="User confirms/rejects suggestions. Returns final canonical name mapping "
                "that should be applied to the uploaded data.",
    status_code=status.HTTP_200_OK
)
async def apply_confirmations(
    analysis_response: AnalyzeResponseAPI,
    confirmations: ConfirmationRequestAPI,
    version: int = 1
) -> FinalMappingResponseAPI:
    """
    Apply user confirmations and generate final mapping.

    **Process:**
    1. For each ACCEPTED suggestion, maps all similar names to canonical name
    2. For each REJECTED suggestion, no mapping is created
    3. Returns structured mapping for application to uploaded data

    **Key Design:**
    - Only ACCEPTED suggestions create mappings
    - REJECTED suggestions are ignored (require manual handling)
    - Returns immutable final mapping for data transformation

    **Response includes:**
    - final_faculty_mapping: {original_name: canonical_name}
    - final_course_mapping: {original_name: canonical_name}
    - applied_timestamp: When mapping was finalized
    - version: Mapping version for tracking

    **Example:**
    ```
    Request confirmations:
    {
      "faculty_confirmations": {"0": "accepted"},
      "course_confirmations": {"0": "accepted"}
    }

    Response:
    {
      "final_faculty_mapping": {
        "Dr. Smith": "Dr. John Smith",
        "smith, john": "Dr. John Smith"
      },
      "final_course_mapping": {
        "DBMS LAB": "Database Systems Lab"
      },
      "applied_timestamp": "2026-01-19T10:30:00Z",
      "version": 1
    }
    ```
    """
    try:
        logger.info(
            f"Applying confirmations: "
            f"{len(confirmations.faculty_confirmations)} faculty, "
            f"{len(confirmations.course_confirmations)} course"
        )

        # Initialize agent
        agent = NormalizationAgent()

        # Convert API suggestions back to internal format
        faculty_suggestions = [
            _api_suggestion_to_internal(s, EntityType.FACULTY)
            for s in analysis_response.faculty_suggestions
        ]

        course_suggestions = [
            _api_suggestion_to_internal(s, EntityType.COURSE)
            for s in analysis_response.course_suggestions
        ]

        # Convert confirmations dict (string keys from JSON) to int keys
        faculty_confirmations = {
            int(k): v.lower() for k, v in confirmations.faculty_confirmations.items()
        }
        course_confirmations = {
            int(k): v.lower() for k, v in confirmations.course_confirmations.items()
        }

        # Apply confirmations
        faculty_mapping = agent.apply_confirmations(
            faculty_suggestions,
            faculty_confirmations
        )
        course_mapping = agent.apply_confirmations(
            course_suggestions,
            course_confirmations
        )

        result = FinalMappingResponseAPI(
            final_faculty_mapping=faculty_mapping,
            final_course_mapping=course_mapping,
            version=version
        )

        logger.info(
            f"Applied confirmations: {len(faculty_mapping)} faculty mappings, "
            f"{len(course_mapping)} course mappings"
        )
        return result

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Validation error: {str(e)}"
        )
    except Exception as e:
        logger.exception(f"Unexpected error during confirmation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while applying confirmations"
        )


# ============= Helper Functions =============

def _api_suggestion_to_internal(suggestion: NormalizationSuggestionResponse, entity_type: EntityType):
    """
    Convert API suggestion model to internal NormalizationSuggestion.

    Helper for converting between API and internal representations.
    """
    from app.services.normalization_agent import NormalizationSuggestion

    return NormalizationSuggestion(
        cluster_id=suggestion.cluster_id,
        detected_names=suggestion.detected_names,
        suggested_canonical=suggestion.suggested_canonical,
        confidence=suggestion.confidence,
        status=ConfirmationStatus(suggestion.status),
        entity_type=entity_type
    )
