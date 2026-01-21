import unittest
from app.services.explainer import HumanExplainer, Explanation

class TestHumanExplainer(unittest.TestCase):
    
    def setUp(self):
        self.explainer = HumanExplainer()
    
    def test_email_error(self):
        error = {
            "type": "value_error.email",
            "loc": ["email"],
            "msg": "value is not a valid email address",
            "ctx": {}
        }
        result = self.explainer.explain_pydantic_error(error)
        
        self.assertIn("email address", result.message.lower())
        self.assertIn("@", result.suggestion)
    
    def test_missing_field(self):
        error = {
            "type": "missing",
            "loc": ["name"],
            "msg": "field required",
            "ctx": {}
        }
        result = self.explainer.explain_pydantic_error(error)
        
        self.assertIn("required", result.message.lower())
        self.assertIn("CSV", result.suggestion)
    
    def test_number_constraint(self):
        error = {
            "type": "value_error.number.not_gt",
            "loc": ["capacity"],
            "msg": "ensure this value is greater than 0",
            "ctx": {"limit_value": 0}
        }
        result = self.explainer.explain_pydantic_error(error)
        
        self.assertIn("greater than", result.message.lower())
        self.assertIn("positive", result.suggestion.lower())

if __name__ == "__main__":
    unittest.main()
