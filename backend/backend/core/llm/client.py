import json
import logging
import os
from typing import Any, Dict, List, Optional
import pandas as pd
from backend.backend.core.llm_service import get_llm_service

logger = logging.getLogger(__name__)

class LLMHelper:
    """
    Helper class for LLM interactions within the pipeline.
    Manages explanations and step-by-step reasoning.
    """
    
    def __init__(self):
        """Initialize LLMHelper."""
        self.llm_service = get_llm_service()
        self.explanations = []
        
    def explain_step(self, step_description: str, data_sample: Optional[pd.DataFrame] = None, 
                     additional_info: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate an explanation for a preprocessing step.
        
        Args:
            step_description: Description of what was done
            data_sample: Sample of the data after the step
            additional_info: Any extra details about the step
            
        Returns:
            Generated explanation string
        """
        try:
            # Prepare context
            context = f"Step: {step_description}\n"
            if additional_info:
                context += f"Details: {json.dumps(additional_info, indent=2)}\n"
            
            if data_sample is not None:
                context += f"Data Sample:\n{data_sample.to_string()}\n"
                
            prompt = f"Explain the following preprocessing step clearly and concisely:\n{context}"
            
            explanation = self.llm_service.chat(prompt)
            
            # Store explanation
            self.explanations.append({
                "step": step_description,
                "explanation": explanation,
                "timestamp": pd.Timestamp.now().isoformat()
            })
            
            logger.info(f"Generated explanation for: {step_description}")
            return explanation
            
        except Exception as e:
            logger.error(f"Error generating explanation: {e}")
            return f"Could not generate explanation for {step_description}."

    def save_explanations(self, filename: str) -> None:
        """
        Save accumulated explanations to a JSON file.
        
        Args:
            filename: Output filename
        """
        try:
            with open(filename, 'w') as f:
                json.dump({"explanations": self.explanations}, f, indent=2)
            logger.info(f"Saved explanations to {filename}")
        except Exception as e:
            logger.error(f"Error saving explanations: {e}")
