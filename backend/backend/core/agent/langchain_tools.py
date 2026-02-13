"""
AURA Agent Tools (LangChain Wrapper)
=====================================
Wraps the core agent tools into LangChain-compatible tools.
"""

from typing import Dict, Any, List, Optional
from langchain_core.tools import tool
from backend.backend.core.agent.tools import (
    inspect_metadata as core_inspect_metadata,
    run_preprocessing_step as core_run_step
)
from backend.backend.core.agent.sanitizer import extract_metadata, sanitize_tool_output
from backend.backend.core.agent.tools import get_dataset

@tool
def inspect_dataset_metadata(dataset_id: str) -> Dict[str, Any]:
    """
    Inspects the metadata of a dataset to understand its structure, columns, and data quality issues.
    Returns a safe, summarized dictionary of metadata.
    """
    return core_inspect_metadata(dataset_id)

@tool
def execute_preprocessing_step(
    dataset_id: str, 
    action: str, 
    params: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Executes a preprocessing step on the dataset.
    
    Args:
        dataset_id: The ID of the dataset.
        action: The action to perform. Options:
            - "impute": Fill missing values.
            - "encode": Encode categorical variables.
            - "scale": Scale numerical features.
            - "drop_col": Drop specific columns.
        params: Parameters for the action. 
            - For impute: {"strategy": "mean"|"median"|"mode", "columns": {"col_name": "strategy"}}
            - For encode: {"strategy": "onehot"|"label", "columns": {"col_name": "strategy"}}
            - For scale: {"strategy": "standard"|"minmax"|"robust"}
            - For drop_col: {"columns": ["col1", "col2"]}
    """
    return core_run_step(dataset_id, action, params)

@tool
def validate_dataset_state(dataset_id: str) -> Dict[str, Any]:
    """
    Validates the current state of the dataset to check if it's ready for modeling.
    Returns missing value counts and non-numeric column counts.
    """
    try:
        df = get_dataset(dataset_id)
        # Check for missing values
        missing = df.isnull().sum().sum()
        # Check for non-numeric columns
        non_numeric = df.select_dtypes(exclude=['number']).shape[1]
        
        return {
            "is_ready": (missing == 0 and non_numeric == 0),
            "total_missing_values": int(missing),
            "non_numeric_columns": int(non_numeric),
            "status": "ready" if (missing == 0 and non_numeric == 0) else "needs_processing"
        }
    except Exception as e:
        return {"error": str(e)}
