# AURA Agentic Controller (LangGraph Implementation)

## 🏗️ Architecture Overview

The new Agentic Controller replaces the manual heuristic pipeline with an **autonomous LLM-driven graph**.

It follows the **Observe-Reason-Act** pattern using LangGraph.

### Files Added:
- `backend/backend/core/agent/graph.py`: The Main Brain (LangGraph workflow).
- `backend/backend/core/agent/langchain_tools.py`: Tool definitions (LangChain wrappers).
- `backend/backend/core/agent/tools.py`: Core tool logic (existing + modified).
- `backend/backend/api/routes/pipeline.py`: Updated to support `mode="agentic"`.

## 🧠 Agent State Schema

The agent maintains a state throughout execution:

```python
class AgentState(TypedDict):
    messages: List[BaseMessage]        # Full conversation history
    dataset_id: str                    # Current dataset being processed
    metadata: Dict[str, Any]           # Latest metadata snapshot
    sensitivity_flags: Dict[str, Any]  # Privacy analysis report
    steps_history: List[str]           # Log of actions taken
    status: str                        # "STARTING", "RUNNING", "DONE", "ERROR"
    error: Union[str, None]            # Last error message
```

## 🔄 Execution Flow

1.  **Start**: Preprocessing request received (API).
2.  **Metadata Extractor**:
    -   Reads dataset.
    -   Extracts safe metadata (no raw data).
3.  **Sensitivity Analyzer** (Privacy Node):
    -   Checks column names for PII (keywords).
    -   Flags sensitive columns.
    -   If PII found, injects strict SYSTEM PROMPT warning.
4.  **Agent (Planner)**:
    -   Receives Metadata + Privacy Report.
    -   Decides next step (Impute, Encode, Scale, Drop).
    -   Can call tools.
5.  **Tool Execution**:
    -   `execute_preprocessing_step`: Modifies data in memory.
    -   `inspect_dataset_metadata`: Re-checks data state.
    -   `validate_dataset_state`: Checks completeness.
6.  **Loop**: Agent receiving new tool output -> Decides next step -> ...
7.  **End**: Agent decides "DONE".

## 🛠️ Tools Available

1.  **`inspect_dataset_metadata(dataset_id)`**:
    -   Returns column types, missing counts, basic stats.
2.  **`execute_preprocessing_step(dataset_id, action, params)`**:
    -   Actions: `impute`, `encode`, `scale`, `drop_col`.
    -   Params: Strategy (mean/median/etc), Columns.
3.  **`validate_dataset_state(dataset_id)`**:
    -   Returns `is_ready` (bool), missing count, non-numeric count.

## 🔌 API Integration

### Triggering the Agent

The frontend triggers the agent by setting `mode="agentic"` in the existing pipeline endpoint:

```http
POST /api/v1/pipeline/run
Content-Type: multipart/form-data

file: (binary csv)
mode: "agentic"
target_col: "Survived"
```

### Response

The response mimics the standard pipeline but includes agent reasoning logs:

```json
{
  "success": true,
  "preprocessing_steps": [
    "Tool Call: inspect_dataset_metadata",
    "I see missing values in Age. I will impute them with median.",
    "Tool Call: execute_preprocessing_step (impute)",
    ...
  ],
  "processed_data_path": "...",
  "model_results": { "accuracy": "N/A (Agentic Mode)" }
}
```

## 🚀 Future Improvements (TODOs)

1.  **Frontend Streaming**: Currently, the API waits for full completion. We should stream the intermediate agent thoughts via WebSocket or SSE for better UX.
2.  **Advanced Privacy**: Replace keyword-based PII detection with a dedicated NER model or LLM call.
3.  **Human-in-the-loop**: Add a `interrupt_before` check in LangGraph to ask user for confirmation before dropping columns or deleting data.
4.  **Persistent Memory**: Save agent history to a database, not just in-memory.
5.  **Replayability**: Store the full LangGraph trace (LangSmith is enabled via env vars).

## 🛡️ Safety & Constraints

-   **No Raw Data**: The Agent NEVER sees the CSV content (rows). Only metadata.
-   **Local Execution**: Code execution happens in `backend.core.agent.tools`, not on the LLM side.
-   **Privacy First**: The graph enforces a privacy check node before the agent can plan.
