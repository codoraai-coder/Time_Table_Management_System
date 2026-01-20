"""
Normalization Agent Service for handling messy uploaded data.

Detects similar names (faculty, courses) using fuzzy matching and suggests
canonical mappings for user confirmation. Ensures no silent auto-fixes.
"""

import logging
from dataclasses import dataclass, asdict, field
from typing import List, Dict, Optional, Set
from enum import Enum
from datetime import datetime, timezone

try:
    from fuzzywuzzy import fuzz
    _FUZZYWUZZY_AVAILABLE = True
except ImportError:
    _FUZZYWUZZY_AVAILABLE = False
    logging.warning("⚠️  fuzzywuzzy not available. Install with: pip install fuzzywuzzy python-Levenshtein")

logger = logging.getLogger(__name__)


class ConfirmationStatus(str, Enum):
    """Status of a suggestion awaiting confirmation"""
    PENDING = "pending_confirmation"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class EntityType(str, Enum):
    """Type of entity being normalized"""
    FACULTY = "faculty"
    COURSE = "course"


@dataclass
class NormalizationSuggestion:
    """
    Single mapping suggestion for user confirmation.
    
    Attributes:
        cluster_id: Unique ID for this cluster within entity type
        detected_names: List of similar names detected
        suggested_canonical: Recommended canonical name (longest/most descriptive)
        confidence: Confidence score 0.0-1.0 based on cluster size and similarity
        status: Current confirmation status
        entity_type: Type of entity (faculty or course)
    """
    cluster_id: int
    detected_names: List[str]
    suggested_canonical: str
    confidence: float
    status: ConfirmationStatus = ConfirmationStatus.PENDING
    entity_type: EntityType = EntityType.FACULTY

    def __post_init__(self):
        """Validate confidence is in valid range"""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got {self.confidence}")
        if len(self.detected_names) < 1:
            raise ValueError("detected_names must contain at least one name")
        if not self.suggested_canonical:
            raise ValueError("suggested_canonical cannot be empty")

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "cluster_id": self.cluster_id,
            "detected_names": self.detected_names,
            "suggested_canonical": self.suggested_canonical,
            "confidence": round(self.confidence, 2),
            "status": self.status.value,
            "entity_type": self.entity_type.value
        }


@dataclass
class NormalizationRequest:
    """
    Input request for normalization analysis.
    
    Attributes:
        faculty_names: List of raw faculty names from upload
        course_names: List of raw course names from upload
        similarity_threshold: Minimum similarity score (0-100) to consider names as similar
    """
    faculty_names: List[str]
    course_names: List[str]
    similarity_threshold: float = 80.0

    def __post_init__(self):
        """Validate request parameters"""
        if not 0 <= self.similarity_threshold <= 100:
            raise ValueError(f"similarity_threshold must be 0-100, got {self.similarity_threshold}")
        if not self.faculty_names and not self.course_names:
            logger.warning("NormalizationRequest has no names to analyze")


@dataclass
class NormalizationResponse:
    """
    Output response with suggestions awaiting confirmation.
    
    Attributes:
        faculty_suggestions: List of faculty name clustering suggestions
        course_suggestions: List of course name clustering suggestions
        analysis_timestamp: When analysis was performed
        request_id: Unique ID for tracking this analysis
    """
    faculty_suggestions: List[NormalizationSuggestion] = field(default_factory=list)
    course_suggestions: List[NormalizationSuggestion] = field(default_factory=list)
    analysis_timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    )
    request_id: Optional[str] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "faculty_suggestions": [s.to_dict() for s in self.faculty_suggestions],
            "course_suggestions": [s.to_dict() for s in self.course_suggestions],
            "analysis_timestamp": self.analysis_timestamp,
            "request_id": self.request_id
        }


@dataclass
class FinalMapping:
    """
    Final confirmed mapping after user approval.
    
    Attributes:
        faculty_mapping: {original_name: canonical_name}
        course_mapping: {original_name: canonical_name}
        applied_timestamp: When mapping was applied
        version: Mapping version number
    """
    faculty_mapping: Dict[str, str] = field(default_factory=dict)
    course_mapping: Dict[str, str] = field(default_factory=dict)
    applied_timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    )
    version: int = 1

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "final_faculty_mapping": self.faculty_mapping,
            "final_course_mapping": self.course_mapping,
            "applied_timestamp": self.applied_timestamp,
            "version": self.version
        }


class NormalizationAgent:
    """
    AI agent for normalizing messy uploaded data.
    
    Key Design Principles:
    - No silent auto-fixes (all suggestions require explicit confirmation)
    - Fuzzy matching for detecting similar names
    - Confidence scoring based on cluster size and similarity
    - Structured JSON output for easy integration
    
    Example:
        agent = NormalizationAgent(similarity_threshold=80.0)
        request = NormalizationRequest(
            faculty_names=["Dr. Smith", "Dr. John Smith"],
            course_names=["DBMS LAB", "Database Lab"]
        )
        response = agent.analyze(request)
        # User confirms suggestions...
        mapping = agent.apply_confirmations(response, confirmations)
    """

    def __init__(self, similarity_threshold: float = 80.0):
        """
        Initialize the normalization agent.
        
        Args:
            similarity_threshold: Minimum fuzz.token_set_ratio score (0-100) to consider names similar
        
        Raises:
            ValueError: If similarity_threshold not in 0-100 range
            ImportError: If fuzzywuzzy is not installed
        """
        if not _FUZZYWUZZY_AVAILABLE:
            raise ImportError(
                "fuzzywuzzy is required for NormalizationAgent. "
                "Install with: pip install fuzzywuzzy python-Levenshtein"
            )

        if not 0 <= similarity_threshold <= 100:
            raise ValueError(f"similarity_threshold must be 0-100, got {similarity_threshold}")

        self.similarity_threshold = similarity_threshold
        logger.info(
            f"NormalizationAgent initialized with similarity_threshold={similarity_threshold}"
        )

    def _clean_names(self, names: List[str]) -> List[str]:
        """
        Clean and deduplicate names.
        
        - Strips whitespace
        - Removes empty strings
        - Case-sensitive deduplication (preserves original case)
        
        Args:
            names: Raw list of names
            
        Returns:
            Cleaned unique names
        """
        cleaned = []
        seen = set()
        for name in names:
            if not name:
                continue
            stripped = name.strip()
            if not stripped or stripped.lower() in seen:
                continue
            cleaned.append(stripped)
            seen.add(stripped.lower())
        
        logger.debug(f"Cleaned {len(names)} names to {len(cleaned)} unique names")
        return cleaned

    def _calculate_similarity(self, name1: str, name2: str) -> float:
        """
        Calculate similarity between two names using token set ratio.
        
        Uses fuzz.token_set_ratio which:
        - Ignores word order
        - Case-insensitive
        - Returns 0-100
        
        Args:
            name1: First name
            name2: Second name
            
        Returns:
            Similarity score 0.0-100.0
        """
        score = fuzz.token_set_ratio(name1.lower(), name2.lower())
        return float(score)

    def detect_similar_names(
        self, 
        names: List[str], 
        entity_type: EntityType = EntityType.FACULTY
    ) -> List[List[str]]:
        """
        Cluster similar names using fuzzy matching.
        
        Algorithm:
        1. Clean and deduplicate input names
        2. For each name, find all similar names
        3. Group into clusters (similar names in same cluster)
        4. Return only clusters with 2+ names (no singletons)
        
        Args:
            names: List of names to cluster
            entity_type: Type of entity for logging
            
        Returns:
            List of clusters, where each cluster is a list of similar names
        """
        cleaned_names = self._clean_names(names)
        
        if not cleaned_names:
            logger.info(f"No names to cluster for {entity_type.value}")
            return []

        clusters = []
        used: Set[str] = set()

        for i, name1 in enumerate(cleaned_names):
            if name1 in used:
                continue

            cluster = [name1]
            used.add(name1)

            # Find all similar names
            for name2 in cleaned_names[i + 1:]:
                if name2 in used:
                    continue

                similarity = self._calculate_similarity(name1, name2)
                
                if similarity >= self.similarity_threshold:
                    cluster.append(name2)
                    used.add(name2)

            # Only include clusters with 2+ names
            if len(cluster) > 1:
                clusters.append(cluster)
                logger.debug(
                    f"Found {entity_type.value} cluster: {cluster} "
                    f"(similarity threshold: {self.similarity_threshold})"
                )

        logger.info(
            f"Detected {len(clusters)} {entity_type.value} clusters "
            f"from {len(cleaned_names)} unique names"
        )
        return clusters

    def _suggest_canonical_name(self, cluster: List[str]) -> str:
        """
        Select canonical name for a cluster.
        
        Strategy: Longest name (usually most descriptive/formal)
        Examples:
        - ["Dr. Smith", "Smith"] → "Dr. Smith"
        - ["DBMS", "Database Systems"] → "Database Systems"
        
        Args:
            cluster: List of similar names
            
        Returns:
            Suggested canonical name
        """
        canonical = max(cluster, key=len)
        logger.debug(f"Selected canonical name: '{canonical}' from {cluster}")
        return canonical

    def _calculate_confidence(self, cluster: List[str]) -> float:
        """
        Calculate confidence score for a suggestion.
        
        Formula:
        - Base: 0.7 (conservative)
        - Bonus: +0.1 per cluster member (maxes out at 0.95)
        
        Logic:
        - More matches = higher confidence in the suggestion
        - Never reach 1.0 (reserved for user confirmation)
        
        Args:
            cluster: List of similar names in cluster
            
        Returns:
            Confidence score 0.0-1.0
        """
        confidence = min(0.95, 0.7 + (len(cluster) * 0.1))
        return confidence

    def analyze(self, request: NormalizationRequest) -> NormalizationResponse:
        """
        Main entry point: analyze messy data and generate suggestions.
        
        Process:
        1. Validate request
        2. Cluster faculty names using fuzzy matching
        3. Cluster course names using fuzzy matching
        4. Create suggestions for each cluster
        5. Return response (all suggestions start as PENDING_CONFIRMATION)
        
        Args:
            request: NormalizationRequest with faculty and course names
            
        Returns:
            NormalizationResponse with suggestions (no changes applied yet)
        """
        logger.info(f"Starting analysis: {len(request.faculty_names)} faculty, {len(request.course_names)} courses")

        # Detect faculty clusters
        faculty_clusters = self.detect_similar_names(
            request.faculty_names,
            entity_type=EntityType.FACULTY
        )
        faculty_suggestions = []

        for cluster_id, cluster in enumerate(faculty_clusters):
            canonical = self._suggest_canonical_name(cluster)
            confidence = self._calculate_confidence(cluster)

            suggestion = NormalizationSuggestion(
                cluster_id=cluster_id,
                detected_names=cluster,
                suggested_canonical=canonical,
                confidence=confidence,
                status=ConfirmationStatus.PENDING,
                entity_type=EntityType.FACULTY
            )
            faculty_suggestions.append(suggestion)
            logger.debug(f"Faculty suggestion {cluster_id}: {suggestion}")

        # Detect course clusters
        course_clusters = self.detect_similar_names(
            request.course_names,
            entity_type=EntityType.COURSE
        )
        course_suggestions = []

        for cluster_id, cluster in enumerate(course_clusters):
            canonical = self._suggest_canonical_name(cluster)
            confidence = self._calculate_confidence(cluster)

            suggestion = NormalizationSuggestion(
                cluster_id=cluster_id,
                detected_names=cluster,
                suggested_canonical=canonical,
                confidence=confidence,
                status=ConfirmationStatus.PENDING,
                entity_type=EntityType.COURSE
            )
            course_suggestions.append(suggestion)
            logger.debug(f"Course suggestion {cluster_id}: {suggestion}")

        response = NormalizationResponse(
            faculty_suggestions=faculty_suggestions,
            course_suggestions=course_suggestions
        )
        
        logger.info(
            f"Analysis complete: {len(faculty_suggestions)} faculty suggestions, "
            f"{len(course_suggestions)} course suggestions"
        )
        return response

    def apply_confirmations(
        self,
        suggestions: List[NormalizationSuggestion],
        confirmations: Dict[int, str]  # {cluster_id: "accepted"/"rejected"}
    ) -> Dict[str, str]:
        """
        Build final mapping based on user confirmations.
        
        Logic:
        - For each ACCEPTED suggestion, map all names in cluster to canonical name
        - REJECTED suggestions are ignored (no mapping created)
        - Result: {original_name: canonical_name, ...}
        
        Args:
            suggestions: List of NormalizationSuggestion objects
            confirmations: Dict mapping cluster_id to "accepted"/"rejected"
            
        Returns:
            Mapping dictionary {original_name: canonical_name}
        """
        logger.info(f"Applying confirmations: {confirmations}")
        mapping = {}

        for suggestion in suggestions:
            confirmation_status = confirmations.get(suggestion.cluster_id, "rejected")

            if confirmation_status.lower() == "accepted":
                for original_name in suggestion.detected_names:
                    mapping[original_name] = suggestion.suggested_canonical
                logger.debug(
                    f"Accepted {suggestion.entity_type.value} cluster {suggestion.cluster_id}: "
                    f"{suggestion.detected_names} → {suggestion.suggested_canonical}"
                )
            else:
                logger.debug(
                    f"Rejected {suggestion.entity_type.value} cluster {suggestion.cluster_id}"
                )

        logger.info(f"Generated mapping with {len(mapping)} entries")
        return mapping

    def finalize_mapping(
        self,
        response: NormalizationResponse,
        faculty_confirmations: Dict[int, str],
        course_confirmations: Dict[int, str],
        version: int = 1
    ) -> FinalMapping:
        """
        Complete workflow: analyze → confirm → finalize.
        
        Args:
            response: NormalizationResponse from analyze()
            faculty_confirmations: {cluster_id: "accepted"/"rejected"}
            course_confirmations: {cluster_id: "accepted"/"rejected"}
            version: Mapping version number
            
        Returns:
            FinalMapping with applied mappings
        """
        logger.info(f"Finalizing mapping v{version}")

        faculty_mapping = self.apply_confirmations(
            response.faculty_suggestions,
            faculty_confirmations
        )
        course_mapping = self.apply_confirmations(
            response.course_suggestions,
            course_confirmations
        )

        return FinalMapping(
            faculty_mapping=faculty_mapping,
            course_mapping=course_mapping,
            version=version
        )
