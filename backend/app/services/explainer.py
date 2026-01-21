from typing import Dict, Optional
from dataclasses import dataclass

@dataclass
class Explanation:
    message: str
    suggestion: Optional[str] = None
    severity: str = "error"

class HumanExplainer:
    """Converts technical errors to human-readable explanations."""
    
    ERROR_TEMPLATES = {
        "string_too_short": "The {field} is too short (minimum {min_length} characters required).",
        "value_error.email": "The email address for {field} is invalid. It must include an @ symbol.",
        "missing": "The {field} field is required but was not provided.",
        "type_error.integer": "The {field} must be a number, not text.",
        "value_error.number.not_gt": "The {field} must be greater than {limit_value}.",
        "value_error.const": "The {field} must be one of: {permitted}.",
    }
    
    SUGGESTIONS = {
        "string_too_short": "Please provide a complete {field} with at least {min_length} characters.",
        "value_error.email": "Use the format: name@college.edu",
        "missing": "Add the {field} column to your CSV file.",
        "type_error.integer": "Remove any text or symbols from the {field} column.",
        "value_error.number.not_gt": "Ensure {field} is a positive number greater than {limit_value}.",
        "value_error.const": "Choose one of these values: {permitted}.",
    }
    
    def explain(self, error_type: str, field: str, context: Dict = None) -> Explanation:
        """Generate human-readable explanation for an error."""
        context = context or {}
        
        template = self.ERROR_TEMPLATES.get(error_type, "Invalid value for {field}.")
        suggestion_template = self.SUGGESTIONS.get(error_type)
        
        message = template.format(field=field, **context)
        suggestion = suggestion_template.format(field=field, **context) if suggestion_template else None
        
        return Explanation(message=message, suggestion=suggestion, severity="error")
    
    def explain_pydantic_error(self, pydantic_error: Dict) -> Explanation:
        """Convert Pydantic error dict to Explanation."""
        error_type = pydantic_error.get("type", "unknown")
        field = " -> ".join(str(loc) for loc in pydantic_error.get("loc", []))
        
        context = pydantic_error.get("ctx", {})
        if "limit_value" in context:
            context["limit_value"] = context["limit_value"]
        if "min_length" in context:
            context["min_length"] = context["min_length"]
        if "permitted" in context:
            context["permitted"] = ", ".join(context["permitted"])
        
        return self.explain(error_type, field, context)
