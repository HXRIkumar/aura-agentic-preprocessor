# AURA Preprocessor (Agentic Edition)

A robust, privacy-preserving machine learning preprocessing system powered by an autonomous LLM agent.

## Core Features

- **Agentic Control**: An autonomous agent inspects data metadata and decides strictly necessary preprocessing steps (Imputation, Encoding, Scaling).
- **Privacy Firewall**: Zero-Trust architecture ensures raw data rows are NEVER exposed to the LLM. Only sanitized metadata is verified.
- **Dynamic Tooling**: The agent utilizes atomic tools to manipulate the dataset statefully.
- **REST API**: Fully integrated FastAPI server for upload, execution, and result retrieval.

## Project Structure

```
.
├── api_server.py            # FastAPI Entry Point
├── backend/
│   └── backend/
│       └── core/
│           ├── agent/       # Agent Core, Tools, Sanitizer
│           └── steps/       # ML Preprocessing Logic (Sklearn)
├── tests/                   # Verification Scripts
└── README.md
```

## How to Run

1. **Setup Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configure Secrets**
   Create a `.env` file:
   ```
   GROQ_API_KEY=your_api_key_here
   ```

3. **Start Server**
   ```bash
   uvicorn api_server:app --reload
   ```

4. **Run Agent**
   Use the verify script to test end-to-end:
   ```bash
   python tests/verify_e2e.py
   ```

## License
MIT
