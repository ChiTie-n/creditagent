# CreditAgent

Agentic AI credit assessment demo for SME and thin-file borrowers.

This project combines:
- a FastAPI backend
- a React + Vite dashboard
- an XGBoost-based financial score
- alternative-data scoring from utility and mobile-money signals
- a ReAct-style orchestrator for live, step-by-step assessment traces

The app is designed as a decision-support prototype, not a production lending system.

## What It Does

CreditAgent evaluates a borrower using:
- financial features from bank-style records
- alternative behavioral signals such as utility payment history and mobile-money activity
- explainability output
- fairness checks
- an agentic workflow UI showing the reasoning/processing steps

The dashboard supports:
- selecting built-in demo borrowers
- creating custom borrowers from the UI
- saving custom borrowers to local storage on disk
- running live streamed assessments
- reviewing per-borrower saved results

## Architecture

```text
React + Vite UI
  -> FastAPI API
  -> ReAct Orchestrator / Deterministic Fallback
  -> Specialist Agents
       - DataCollectionAgent
       - FinancialScoringAgent
       - AlternativeDataAgent
       - RiskDecisionAgent
       - ExplainabilityAgent
       - BiasFairnessAgent
  -> ML + Rule-Based Decision Support
```

## Project Structure

```text
api/               FastAPI app and endpoints
agents/            orchestration and specialist agents
tools/             scoring, feature engineering, reporting, fairness utilities
mock_data/         demo personas and custom-persona persistence helpers
data/              training assets and saved custom personas
models/            trained XGBoost model artifacts
frontend/          React + Vite dashboard
```

## Requirements

- Python 3.11
- Node.js 18+
- npm

## Setup

### 1. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 2. Install frontend dependencies

```bash
cd frontend
npm install
cd ..
```

### 3. Configure environment

Edit `.env`:

```env
ANTHROPIC_API_KEY=...
DATA_PATH=...
```

Notes:
- If `ANTHROPIC_API_KEY` starts with `AIza`, the app uses Google models through `google-genai`.
- If it starts with `sk-ant`, the app uses Anthropic.
- If no LLM is available, the app can fall back to a deterministic pipeline.

## Train the Model

If `models/xgboost_model.pkl` is missing, train the model first:

```bash
python data/train_model.py
```

Expected outputs:
- `models/xgboost_model.pkl`
- `models/feature_names.pkl`

## Run Locally

### 1. Start the backend

```bash
uvicorn api.main:app --reload
```

Backend:
- http://localhost:8000

### 2. Start the frontend

```bash
cd frontend
npm run dev
```

Frontend:
- http://localhost:5173

The Vite dev server is configured with:
- `host: 0.0.0.0`
- `allowedHosts: true`

This makes sharing through tools like ngrok easier.

## API Endpoints

### Health

```http
GET /health
```

### List borrowers

```http
GET /personas
```

### Get borrower detail

```http
GET /personas/{borrower_id}
```

### Create custom borrower

```http
POST /personas
```

### Run classic assessment

```http
POST /assess
Content-Type: application/json

{
  "borrower_id": "borrower_001"
}
```

### Run agentic assessment

```http
POST /assess/agentic
Content-Type: application/json

{
  "borrower_id": "borrower_001"
}
```

### Stream live assessment events

```http
GET /assess/stream/{borrower_id}
```

### Decision history

```http
GET /history
```

## Demo Data

Built-in demo borrowers live in:

[mock_data/personas.py](./mock_data/personas.py)

Custom borrowers created from the UI are saved in:

[data/custom_personas.json](./data/custom_personas.json)

At startup, custom borrowers are loaded and merged into the in-memory persona set.

## Current UI Features

- borrower selector
- custom borrower creation form
- customer profile card
- streamed agent workflow nodes
- LLM thought log
- result sidebar with:
  - decision
  - score breakdown
  - credit terms
  - strengths / concerns
  - fairness result
  - AI report

## Decision Logic Notes

The system currently combines:
- financial score
- alternative score
- thin-file handling
- fairness override
- affordability guardrails for requested loan size

Important:
- this is still a prototype
- pricing and credit terms are rule-based bands, not real bank pricing logic
- the system is intended for decision support, not automated loan disbursement

## Sharing with ngrok

Run the backend first:

```bash
uvicorn api.main:app --reload
```

Run the frontend:

```bash
cd frontend
npm run dev
```

Then expose the frontend:

```bash
ngrok http 5173
```

Because the frontend proxies `/assess`, `/personas`, and `/health` to `localhost:8000`, sharing the frontend URL is usually enough while both local servers are running.

## Tech Stack

- Backend: FastAPI
- Frontend: React 19 + Vite
- ML: XGBoost + SHAP
- LLM orchestration: Gemini / Anthropic
- Fairness: rule-based fairness metrics
- Storage for custom personas: local JSON file

## Limitations

- mock/demo-grade data model
- some credit terms are rule-based rather than calibrated from lending economics
- no authentication
- no production database
- no deployment pipeline in this repo
- fairness logic is simplified for demo purposes

## Status

This repository is currently best understood as:
- a hackathon/demo prototype
- a UI-rich proof of concept
- a decision-support experiment for SME and thin-file credit assessment
