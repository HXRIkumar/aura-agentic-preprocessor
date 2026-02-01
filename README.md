# Aura Preprocessor

A modular, privacy-preserving machine learning preprocessing system orchestrated by an autonomous agent.

## Overview

The **Aura Preprocessor** transforms raw datasets into machine-learning-ready formats without manual intervention. Unlike traditional static pipelines, Aura employs an **Agentic Architecture**: an LLM-powered agent reasons over dataset metadata to dynamically select and execute preprocessing steps (imputation, encoding, scaling).

Critically, this system implements a **Zero-Trust Privacy Firewall**. The agent *never* accesses raw data rows; it makes decisions solely based on sanitized statistical metadata, ensuring data privacy and security.

## Project Structure

This project follows a backend-centric architecture:

```
.
├── api_server.py                 # FastAPI Entry Point & REST API
├── backend/
│   └── backend/
│       └── core/
│           ├── agent/            # Agentic Logic
│           │   ├── core.py       # Main Observation-Reasoning-Action Loop
│           │   ├── tools.py      # Preprocessing Tool Wrappers
│           │   └── sanitizer.py  # Privacy Firewall & Output Guardrails
│           ├── steps/            # ML Preprocessing Modules (Scikit-learn)
│           ├── pipeline.py       # Pipeline Orchestration
│           └── llm_service.py    # LLM Integration (Groq)
├── tests/                        # Verification & Test Scripts
│   ├── verify_e2e.py             # End-to-End System Test
│   └── test_privacy.py           # Privacy Firewall Unit Tests
└── requirements.txt              # Project Dependencies
```

## Prerequisites

- **Python 3.10** or higher
- **pip** package manager
- A valid **Groq API Key** (for LLM reasoning)

## Setup

1. **Clone the repository** (if you haven't already):
   ```bash
   git clone https://github.com/HXRIkumar/aura-agentic-preprocessor.git
   cd aura-agentic-preprocessor
   ```

2. **Create a Virtual Environment**:
   It is recommended to use a virtual environment to keep dependencies clean.
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**:
   Create a `.env` file in the root directory. This file is excluded from git for security.
   ```env
   GROQ_API_KEY=your_actual_api_key_here
   ```

## How to Run

1. **Start the API Server**:
   The system runs as a FastAPI server.
   ```bash
   uvicorn api_server:app --reload
   ```
   The server will start at `http://localhost:8000`.

2. **Access the API Documentation**:
   Open your browser to [http://localhost:8000/docs](http://localhost:8000/docs) to see the interactive Swagger UI.

## How to Test

We include automated scripts to verify the system works as expected.

- **End-to-End Verification**:
  Simulates a full user workflow: uploading a dataset and triggering the agent to clean it.
  ```bash
  python tests/verify_e2e.py
  ```

- **Privacy Tests**:
  Verifies that the Privacy Firewall correctly blocks raw data leaks (e.g., DataFrames).
  ```bash
  python tests/test_privacy.py
  ```

## Design Notes

- **Agent Core (`backend/backend/core/agent/core.py`)**: The central brain. It maintains the conversation state, enforces step limits (Max 15), and parses LLM decisions into executable actions.
- **Privacy Firewall (`backend/backend/core/agent/sanitizer.py`)**: A security layer that sits between the Tools and the LLM. It intercepts every tool output to strip PII and raw data rows, returning only safe statistical summaries.
- **Tools Layer (`backend/backend/core/agent/tools.py`)**: Wraps standard preprocessing logic (using Pandas/Scikit-learn) into atomic tools that the agent can invoke securely.

## Repository Exclusions

To ensure best practices and security, the following are intentionally **excluded** from this repository:
- `data/`, `uploads/`, `outputs/`: User data and processing artifacts.
- `.env`: Secrets and API keys.
- `frontend/`: The User Interface code (this repo is backend-focused).
- `venv/`: Local virtual environment files.

## Current Status

**Active Development (Week 1 Milestone)**.
The core agentic architecture, privacy safeguards, and API integration are complete and verified. Future work will focus on persistent storage and advanced error recovery mechanisms.
