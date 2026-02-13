"""
AURA Agent Graph
================
Implements the LangGraph-based agentic workflow.

Flow:
1. Start -> Metadata Extractor
2. Metadata -> Sensitivity Analyzer (Privacy Check)
3. Sensitivity -> Planner (Agent)
4. Planner -> Tool Execution -> Planner (Loop)
5. Planner -> Finalizer -> End
"""

import os
import json
from typing import TypedDict, Annotated, Sequence, Dict, Any, List, Union
import operator
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, ToolMessage, AIMessage
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

# Tools
from backend.backend.core.agent.langchain_tools import (
    inspect_dataset_metadata, 
    execute_preprocessing_step, 
    validate_dataset_state
)

# LLM
from backend.backend.core.llm_service import get_llm_service

# =============================================================================
# State Definition
# =============================================================================

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    dataset_id: str
    metadata: Dict[str, Any]
    sensitivity_flags: Dict[str, Any]
    steps_history: Annotated[List[str], operator.add]
    status: str
    error: Union[str, None]

# =============================================================================
# Nodes
# =============================================================================

def metadata_node(state: AgentState):
    """Refreshes dataset metadata."""
    try:
        dataset_id = state['dataset_id']
        meta = inspect_dataset_metadata.invoke(dataset_id) # Direct tool call
        return {"metadata": meta}
    except Exception as e:
        return {"error": f"Metadata extraction failed: {str(e)}"}

def sensitivity_node(state: AgentState):
    """
    Analyzes metadata for potential privacy issues (PII).
    This node acts as a safeguard before the main agent plans.
    """
    metadata = state.get("metadata", {})
    columns = metadata.get("columns", {})
    
    # Simple heuristic check for PII keywords
    pii_keywords = ["email", "phone", "ssn", "social", "address", "name", "id", "card", "billing"]
    flagged_columns = []
    
    for col_name in columns.keys():
        if any(keyword in col_name.lower() for keyword in pii_keywords):
            flagged_columns.append(col_name)
    
    sensitivity_report = {
        "has_pii": len(flagged_columns) > 0,
        "flagged_columns": flagged_columns,
        "recommendation": "Mask or Drop" if flagged_columns else "None"
    }
    
    # Inject a system message about privacy if needed
    msgs = []
    if sensitivity_report["has_pii"]:
        warning = (
            f"PRIVACY ALERT: The following columns might contain PII: {flagged_columns}. "
            f"You MUST prioritize privacy protection (e.g., dropping these columns) "
            f"before other preprocessing."
        )
        msgs.append(SystemMessage(content=warning))
        
    return {"sensitivity_flags": sensitivity_report, "messages": msgs}

def agent_node(state: AgentState):
    """
    The main decision-making node.
    It reviews the state and decides the next action calling tools.
    """
    model = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0,
        api_key=os.environ.get("GROQ_API_KEY")
    )
    
    # Bind tools
    tools = [inspect_dataset_metadata, execute_preprocessing_step, validate_dataset_state]
    model_with_tools = model.bind_tools(tools)
    
    # Prompt Construction
    metadata_str = json.dumps(state.get("metadata", {}), indent=2)
    sensitivity_str = json.dumps(state.get("sensitivity_flags", {}), indent=2)
    
    system_prompt = f"""You are AURA, an autonomous Data Engineering Agent.
Your goal is to prepare a dataset for machine learning.

CURRENT CONTEXT:
Dataset ID: {state['dataset_id']}
Metadata: {metadata_str}
Sensitivity Report: {sensitivity_str}

RULES:
1. PRIVACY FIRST: If sensitive columns exist, handle them immediately (drop or mask).
2. DATA HYGIENE: Handle missing values before encoding or scaling.
3. EFFICIENCY: Don't repeat steps.
4. VALIDATION: Check your work using 'validate_dataset_state' after major changes.
5. FINISH: When the dataset is clean (no missing values, all numeric), call 'validate_dataset_state' and if it returns 'is_ready': true, stop outputting tool calls and just reply with "DONE".

Think step-by-step.
"""
    
    messages = [SystemMessage(content=system_prompt)] + state['messages']
    
    response = model_with_tools.invoke(messages)
    
    return {"messages": [response]}

def should_continue(state: AgentState):
    """Determines the next node grounded on the LLM's response."""
    messages = state['messages']
    last_message = messages[-1]
    
    # If LLM called a tool, go to tool execution
    if last_message.tool_calls:
        return "tools"
    
    # If LLM said "DONE" or seems finished
    if "DONE" in last_message.content:
        return END
        
    # Default: Stop if no tool calls (conversation turn)
    # In a chat loop, we might return END to wait for user, but here we run autonomously.
    # If the model didn't call a tool and didn't say DONE, we treat it as END (or error).
    return END

# =============================================================================
# Graph Construction
# =============================================================================

def build_agent_graph():
    """Constructs the executable LangGraph."""
    workflow = StateGraph(AgentState)
    
    # Define Nodes
    workflow.add_node("metadata_extractor", metadata_node)
    workflow.add_node("sensitivity_analyzer", sensitivity_node)
    workflow.add_node("agent", agent_node)
    
    # Tool Node
    tool_node = ToolNode([inspect_dataset_metadata, execute_preprocessing_step, validate_dataset_state])
    workflow.add_node("tools", tool_node)
    
    # Define Edges
    workflow.set_entry_point("metadata_extractor")
    workflow.add_edge("metadata_extractor", "sensitivity_analyzer")
    workflow.add_edge("sensitivity_analyzer", "agent")
    
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            END: END
        }
    )
    
    workflow.add_edge("tools", "agent") # Loop back to agent after tool execution
    
    app = workflow.compile()
    return app

# =============================================================================
# Entry Point
# =============================================================================

def run_agentic_pipeline(dataset_id: str, verbose: bool = True):
    """
    Runs the full agentic loop for a given dataset.
    """
    app = build_agent_graph()
    
    initial_state = {
        "dataset_id": dataset_id,
        "messages": [HumanMessage(content="Please preprocess this dataset based on its metadata.")],
        "steps_history": [],
        "status": "STARTING",
        "error": None
    }
    
    logger_str = "Agent execution log:\n"
    
    # Invoke the graph
    # We use stream to capture steps
    # Invoke the graph
    final_output = app.invoke(initial_state)
    
    if verbose:
        logger_str = "Agent execution log:\n"
        for m in final_output['messages']:
            logger_str += f"{m.type}: {m.content}\n"
        print(logger_str)
        
    return final_output
