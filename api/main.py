"""
api/main.py — FastAPI credit assessment API.
"""

import sys
import os
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, model_validator
from typing import Optional, List, Dict, Any
import time

from agents.orchestrator import OrchestratorAgent
from agents.react_orchestrator import ReActOrchestrator
from agents.agent_memory import get_session_history
from mock_data.personas import PERSONAS
from mock_data.persona_store import (
    delete_custom_persona,
    hydrate_personas,
    list_custom_personas,
    next_custom_borrower_id,
    save_custom_personas,
)

app = FastAPI(
    title="CreditAgent API",
    description="AI Multi-Agent Credit Assessment System for SMEs",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Singleton orchestrator instances (models loaded once)
_orchestrator = None
_react_orchestrator = None

hydrate_personas()


def get_orchestrator() -> OrchestratorAgent:
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = OrchestratorAgent()
    return _orchestrator


def get_react_orchestrator() -> ReActOrchestrator:
    global _react_orchestrator
    if _react_orchestrator is None:
        _react_orchestrator = ReActOrchestrator()
    return _react_orchestrator


# ── Request / Response models ────────────────────────────────────────────────

class AssessRequest(BaseModel):
    borrower_id: str


class CreditAssessmentResult(BaseModel):
    borrower_id: str
    borrower_name: str
    scenario: Optional[str] = None
    composite_score: int
    risk_tier: str
    decision: str
    credit_limit: float
    interest_rate_range: str
    financial_score: int
    alternative_score: int
    is_underbanked: bool
    key_strengths: List[str]
    key_concerns: List[str]
    report: str
    bias_detected: bool
    fairness_metrics: Dict[str, Any]
    processing_time_ms: int
    data_completeness: float
    shap_summary: Dict[str, float]
    score_breakdown: Dict[str, Any]
    alternative_signals: Dict[str, Any]
    agent_pipeline: List[Dict[str, Any]]
    confidence: float
    # Agentic AI fields
    reasoning_trace: Optional[List[Dict[str, Any]]] = None
    agentic_mode: Optional[str] = None
    reasoning_summary: Optional[str] = None


class PersonaInfo(BaseModel):
    borrower_id: str
    name: str
    scenario: str
    expected_decision: str
    has_bank_data: bool


class PersonaDetail(BaseModel):
    borrower_id: str
    name: str
    business_name: str
    business_type: str
    scenario: str
    loan_purpose: str
    loan_amount_requested: float
    expected_decision: str
    has_bank_data: bool
    profile: Dict[str, Any]
    sources_available: Dict[str, bool]
    data_completeness: float


class ProfileInput(BaseModel):
    gender: str
    age_group: str
    employment_type: str
    region: str
    province: str


class UtilityDataInput(BaseModel):
    provider: str = "EVN"
    months_history: int = Field(ge=0, le=72)
    on_time_rate: float = Field(ge=0, le=1)


class MobileDataInput(BaseModel):
    platform: str
    consistency_score: float = Field(ge=0, le=1)
    monthly_volume: float = Field(ge=0)


class BankDataInput(BaseModel):
    LIMIT_BAL: float = Field(ge=0)
    SEX: int = Field(ge=1, le=2)
    EDUCATION: int = Field(ge=1, le=4)
    MARRIAGE: int = Field(ge=1, le=3)
    AGE: int = Field(ge=18, le=100)
    PAY_0: int = Field(ge=-2, le=8)
    PAY_2: int = Field(ge=-2, le=8)
    PAY_3: int = Field(ge=-2, le=8)
    BILL_AMT1: float = Field(ge=0)
    PAY_AMT1: float = Field(ge=0)


class CreatePersonaRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    business_name: str = Field(min_length=2, max_length=120)
    business_type: str = Field(min_length=2, max_length=60)
    scenario: str = Field(min_length=4, max_length=200)
    loan_purpose: str = Field(min_length=4, max_length=200)
    loan_amount_requested: float = Field(ge=0)
    expected_decision: str = "UNKNOWN"
    profile: ProfileInput
    utility_data: Optional[UtilityDataInput] = None
    mobile_data: Optional[MobileDataInput] = None
    bank_data: Optional[BankDataInput] = None

    @model_validator(mode="after")
    def validate_data_sources(self):
        if not any([self.utility_data, self.mobile_data, self.bank_data]):
            raise ValueError("At least one data source is required")
        return self


def _to_persona_info(borrower_id: str, persona: Dict[str, Any]) -> PersonaInfo:
    return PersonaInfo(
        borrower_id=borrower_id,
        name=persona.get("name", f"Unknown Name ({borrower_id})"),
        scenario=persona.get("scenario", "Custom Scenario"),
        expected_decision=persona.get("expected_decision", "UNKNOWN"),
        has_bank_data=persona.get("bank_data") is not None,
    )


# ── Endpoints ────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "service": "CreditAgent API"}


@app.get("/personas", response_model=List[PersonaInfo])
def list_personas():
    """List all available demo personas."""
    return [
        _to_persona_info(bid, p)
        for bid, p in PERSONAS.items()
    ]


@app.get("/personas/{borrower_id}", response_model=PersonaDetail)
def get_persona_detail(borrower_id: str):
    if borrower_id not in PERSONAS:
        raise HTTPException(status_code=404, detail=f"Borrower '{borrower_id}' not found")

    persona = PERSONAS[borrower_id]
    sources = {
        "bank_data": persona.get("bank_data") is not None,
        "utility_data": persona.get("utility_data") is not None,
        "mobile_data": persona.get("mobile_data") is not None,
    }

    return PersonaDetail(
        borrower_id=borrower_id,
        name=persona.get("name", f"Unknown Name ({borrower_id})"),
        business_name=persona.get("business_name", "Unknown Business"),
        business_type=persona.get("business_type", "unknown"),
        scenario=persona.get("scenario", "Custom Scenario"),
        loan_purpose=persona.get("loan_purpose", "Working capital"),
        loan_amount_requested=float(persona.get("loan_amount_requested", 0.0)),
        expected_decision=persona.get("expected_decision", "UNKNOWN"),
        has_bank_data=persona.get("bank_data") is not None,
        profile=persona.get("profile", {}),
        sources_available=sources,
        data_completeness=sum(sources.values()) / 3.0,
    )


@app.post("/personas", response_model=PersonaInfo)
def create_persona(request: CreatePersonaRequest):
    borrower_id = next_custom_borrower_id()
    persona = {
        "name": request.name,
        "business_name": request.business_name,
        "business_type": request.business_type,
        "scenario": request.scenario,
        "loan_purpose": request.loan_purpose,
        "loan_amount_requested": request.loan_amount_requested,
        "expected_decision": request.expected_decision,
        "profile": request.profile.model_dump(),
        "utility_data": request.utility_data.model_dump() if request.utility_data else None,
        "mobile_data": request.mobile_data.model_dump() if request.mobile_data else None,
        "bank_data": request.bank_data.model_dump() if request.bank_data else None,
    }

    PERSONAS[borrower_id] = persona
    custom_personas = list_custom_personas()
    custom_personas[borrower_id] = persona
    save_custom_personas(custom_personas)

    return _to_persona_info(borrower_id, persona)


@app.delete("/personas/{borrower_id}", status_code=204)
def delete_persona(borrower_id: str):
    if borrower_id not in PERSONAS:
        raise HTTPException(status_code=404, detail=f"Borrower '{borrower_id}' not found")
    if not borrower_id.startswith("custom_"):
        raise HTTPException(status_code=403, detail="Only custom borrower profiles can be deleted")
    if not delete_custom_persona(borrower_id):
        raise HTTPException(status_code=404, detail=f"Custom borrower '{borrower_id}' not found")
    return Response(status_code=204)


@app.post("/assess", response_model=CreditAssessmentResult)
def assess(request: AssessRequest):
    """
    Run full credit assessment for a borrower (classic pipeline).

    Body: {"borrower_id": "borrower_001"}
    """
    if request.borrower_id not in PERSONAS:
        raise HTTPException(
            status_code=404,
            detail=f"Borrower '{request.borrower_id}' not found. "
                   f"Available: {list(PERSONAS.keys())}",
        )

    orchestrator = get_orchestrator()

    try:
        result = orchestrator.run(request.borrower_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if "error" in result:
        raise HTTPException(status_code=422, detail=result["error"])

    return result


@app.post("/assess/agentic", response_model=CreditAssessmentResult)
def assess_agentic(request: AssessRequest):
    """
    Run credit assessment using the ReAct agentic loop.
    The LLM autonomously reasons about which tools to call and adapts
    its strategy based on available data. Falls back to deterministic
    pipeline if LLM is unavailable.

    Body: {"borrower_id": "borrower_001"}
    """
    if request.borrower_id not in PERSONAS:
        raise HTTPException(
            status_code=404,
            detail=f"Borrower '{request.borrower_id}' not found. "
                   f"Available: {list(PERSONAS.keys())}",
        )

    orchestrator = get_react_orchestrator()

    try:
        result = orchestrator.run(request.borrower_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if "error" in result:
        raise HTTPException(status_code=422, detail=result["error"])

    return result


@app.get("/history")
def decision_history():
    """Return session-level decision history across all assessments."""
    return {"history": get_session_history()}


# ── SSE Streaming Endpoint ───────────────────────────────────────────────────

from fastapi.responses import StreamingResponse
import asyncio
import json


@app.get("/assess/stream/{borrower_id}")
async def assess_stream(borrower_id: str):
    """
    SSE endpoint — streams ReAct agent steps (thought, tool_call, tool_result, llm_status, result)
    as they happen in real-time.
    """
    if borrower_id not in PERSONAS:
        async def error_gen():
            yield f"data: {json.dumps({'type': 'error', 'message': 'Borrower not found'})}\n\n"
        return StreamingResponse(error_gen(), media_type="text/event-stream")

    import queue
    import threading
    from agents.react_orchestrator import ReActOrchestrator

    # Thread-safe queue to bridge sync ReAct generator to async SSE response
    q = queue.Queue()

    def run_sync_orchestrator():
        try:
            # We must use a fresh orchestrator per request to avoid state bleed
            orchestrator = ReActOrchestrator()
            for event in orchestrator.run_streaming(borrower_id):
                q.put(event)
                if event.get("type") in ("result", "error"):
                    break
        except Exception as e:
            q.put({"type": "error", "message": str(e)})
        finally:
            q.put(None)  # Sentinel to end stream

    # Start the LLM ReAct loop in a background thread so it doesn't block FastAPI
    threading.Thread(target=run_sync_orchestrator, daemon=True).start()

    async def event_generator():
        while True:
            try:
                # Non-blocking get with a small sleep allows async event loop to breathe
                event = q.get_nowait()
                if event is None:  # Sentinel
                    break
                yield f"data: {json.dumps(event)}\n\n"
            except queue.Empty:
                await asyncio.sleep(0.05)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Access-Control-Allow-Origin": "*",
        }
    )

