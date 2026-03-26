# CreditAgent 🏦

> AI Multi-Agent Credit Assessment System for SMEs — Hackathon Demo

## Architecture

```
React + Vite UI  →  FastAPI Backend  →  ReAct Orchestrator (Agentic Loop)
                                           ↓
                            6 Specialist Agents (parallel execution)
                                           ↓
                            MCP Tools (XGBoost, SHAP, Gemini, Fairness)
```

## Quick Start

### 1. Install dependencies
```bash
cd D:/SWIN/SWIN/creditagent
pip install -r requirements.txt
```

### 2. Configure environment
Edit `.env` and add your Anthropic API key:
```
ANTHROPIC_API_KEY=sk-ant-...
DATA_PATH=D:/SWIN/SWIN/accepted_2007_to_2018Q4.csv.gz
```

### 3. Train the model
```bash
python data/train_model.py
```
Output: `models/xgboost_model.pkl` + AUC score

### 4. Start API server
```bash
uvicorn api.main:app --reload
```
API runs at http://localhost:8000

### 5. Start React Dashboard
```bash
cd frontend
npm install
npm run dev
```
Dashboard opens at http://localhost:5173

## Demo Personas

| ID | Name | Scenario | Expected |
|----|------|----------|----------|
| borrower_001 | Nguyen Van A | Strong traditional profile | ✅ APPROVE |
| **borrower_002** | **Tran Thi B** | **Thin-file, no bank account** | **✅ APPROVE** |
| borrower_003 | Le Van C | Borderline case | ⚠️ ESCALATE |
| borrower_004 | Pham Van D | High risk | ❌ DENY |

## Key Demo Insight

**borrower_002 (Tran Thi B)** has NO bank account but gets **APPROVED** via:
- Utility bill payment history (48 months, 95% on-time)
- Mobile money consistency (0.89 score)
- Alternative data weighting: 60% (vs 30% for banked borrowers)

## API Endpoints

```bash
# Health check
GET  http://localhost:8000/health

# List personas
GET  http://localhost:8000/personas

# Run assessment
POST http://localhost:8000/assess
Body: {"borrower_id": "borrower_002"}
```

## Tech Stack

- **ML**: XGBoost + SHAP (feature importance)
- **LLM**: Gemini / Claude (ReAct Orchestrator & report generation)
- **Backend**: Python 3.11 + FastAPI (with SSE Server-Sent Events)
- **Frontend**: React 19 + Vite + Vanilla CSS
- **Fairness**: Disparate Impact, Statistical Parity, Counterfactual
