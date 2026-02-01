# How to Run AURA Preprocessor (CLI + API + Frontend)

This project can be run in **three ways**:

- **CLI only** (runs the pipeline on a CSV and writes files into `outputs/`)
- **Backend API** (FastAPI server used by the frontend)
- **Full-stack UI** (React frontend + FastAPI backend)

---

## Prerequisites

- **macOS** (your repo is already set up on macOS; other OSes should also work)
- **Python 3.11.x** (recommended: **3.11.13**)
- **Node.js 18+** and npm (for the frontend)

> Note: On some machines `python3` may be Python 3.14+, which can break `pydantic-core` installs.
> Use `python3.11` explicitly for this repo.

---

## 1) Backend Setup (Python)

From the repo root:

```bash
cd "/Users/hari/Downloads/aura_preprocessor(Haris)"
python3.11 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Optional: Enable LLM features (Groq)

Set your Groq API key:

```bash
export GROQ_API_KEY="YOUR_KEY_HERE"
```

If you prefer `.env`, create a file named `.env` in the repo root:

```env
GROQ_API_KEY=YOUR_KEY_HERE
```

---

## 2) Run the Pipeline (CLI mode)

With the venv activated:

```bash
python main.py
```

Run on your own CSV:

```bash
python main.py data/your_dataset.csv
```

Interactive step mode:

```bash
python main.py data/your_dataset.csv step
```

Specify target column:

```bash
python main.py data/your_dataset.csv auto target_column_name
```

### CLI Outputs

Pipeline outputs are written to `outputs/`, typically:

- `outputs/<dataset>_processed.csv`
- `outputs/report.json`
- `outputs/aura_explanations.json`

---

## 3) Run the Backend API (FastAPI)

With the venv activated (from repo root):

```bash
python api_server.py
```

API will start on:

- `http://localhost:8000`

Quick checks:

```bash
curl http://127.0.0.1:8000/api/v1/health
curl http://127.0.0.1:8000/
```

---

## 4) Run the Frontend (React)

In a separate terminal:

```bash
cd "/Users/hari/Downloads/aura_preprocessor(Haris)/frontend"
npm install
npm run dev
```

Vite will print the actual URL. If `3000` is busy, it will use `3001`, `3002`, etc.

### Frontend environment config

Create `frontend/.env` (or copy from `frontend/.env.example` if present):

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_API_VERSION=v1
```

---

## 5) Full-Stack (Frontend + Backend)

Terminal A (backend):

```bash
cd "/Users/hari/Downloads/aura_preprocessor(Haris)"
source venv/bin/activate
python api_server.py
```

Terminal B (frontend):

```bash
cd "/Users/hari/Downloads/aura_preprocessor(Haris)/frontend"
npm run dev
```

Then open the Vite URL shown in the terminal and upload a CSV.

---

## Troubleshooting

### Issue: `ModuleNotFoundError: No module named 'fastapi'`

You’re not in the venv or dependencies aren’t installed:

```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: `pydantic-core` build fails and mentions Python 3.14

This repo requires Python **3.11**:

```bash
rm -rf venv
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: NumPy import fails / “library load disallowed by system policy”

Recreate the venv (recommended):

```bash
rm -rf venv
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: Frontend says “Port 3000 is in use”

That’s fine—Vite will automatically choose another port and print it (e.g. `3001`, `3002`).

