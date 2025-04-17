from langchain.llms.base import LLM
from typing import Any, List, Mapping, Optional
import random

class DummyLLM(LLM):
    """
    A dummy LLM implementation for demonstration purposes.
    This simulates responses for data description quality evaluation.
    """
    
    @property
    def _llm_type(self) -> str:
        return "dummy_llm"

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        """
        Generate a dummy response based on the input prompt.
        Analyzes the description and returns a simulated evaluation.
        """
        # Extract the description from the prompt
        try:
            description = prompt.split('"{description}"')[1].split('Provide your evaluation')[0].strip()
            description = description.lower()
        except:
            description = prompt.lower()
        
        # Simple heuristics to determine quality
        good_indicators = [
            "date", "revenue", "customer", "product", "classification", 
            "calculated", "updated", "generated", "measured", "yyyy-mm-dd",
            "usd", "status", "category", "format", "unit", "source"
        ]
        
        bad_indicators = [
            "field", "the data", "thing", "stuff", "items", "values", "codes",
            "added by", "john", "jane", "bob", "alice"
        ]
        
        # Count indicators
        good_count = sum(1 for indicator in good_indicators if indicator in description)
        bad_count = sum(1 for indicator in bad_indicators if indicator in description)
        
        # Determine if the description is good based on indicators and length
        is_good = (good_count > bad_count) and (len(description) > 30)
        
        # Generate reasoning based on the decision
        if is_good:
            decision = "PASS"
            reasoning_options = [
                f"The description is clear and provides sufficient context. It includes {good_count} quality indicators such as specific details about the data's purpose, format, or business context.",
                f"This description meets quality standards. It provides adequate information about what the data represents and includes important details that help users understand its meaning and usage.",
                f"The description is well-formed and contains necessary information. It has sufficient length ({len(description)} characters) and includes specific terminology that clarifies its purpose."
            ]
        else:
            decision = "FAIL"
            reasoning_options = [
                f"The description lacks clarity and sufficient detail. It only has {good_count} quality indicators but {bad_count} poor quality indicators. It needs more specific information about the data's purpose and context.",
                f"This description is too vague and doesn't provide enough context for users to understand the data. It's missing important details about format, units, or business relevance.",
                f"The description is inadequate. It's too short ({len(description)} characters) or uses generic terms that don't convey meaningful information about what the data represents."
            ]
        
        # Randomly select a reasoning
        reasoning = random.choice(reasoning_options)
        
        # Format the response
        response = f"""
Decision: {decision}
Reasoning: {reasoning}
"""
        return response

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Get the identifying parameters."""
        return {"name": "DummyLLM"}
