"""
tool_registry.py
Dynamic tool registry — agents discover and invoke tools by name at runtime.
This is the foundation of agentic tool use: the LLM picks tools from this registry.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Any, Callable
from dataclasses import dataclass, field


@dataclass
class ToolSpec:
    name: str
    description: str
    parameters: dict          # JSON-schema style description of args
    fn: Callable
    required_params: list[str] = field(default_factory=list)


class ToolRegistry:
    """Registry of callable tools available to agents."""

    def __init__(self):
        self._tools: dict[str, ToolSpec] = {}

    def register(self, spec: ToolSpec):
        self._tools[spec.name] = spec

    def get(self, name: str) -> ToolSpec | None:
        return self._tools.get(name)

    def list_tools(self) -> list[dict]:
        return [
            {
                "name": t.name,
                "description": t.description,
                "parameters": t.parameters,
                "required": t.required_params,
            }
            for t in self._tools.values()
        ]

    def call(self, name: str, **kwargs) -> Any:
        spec = self.get(name)
        if spec is None:
            raise ValueError(f"Unknown tool: '{name}'. Available: {list(self._tools.keys())}")
        return spec.fn(**kwargs)


def build_default_registry() -> ToolRegistry:
    """Build the default tool registry with all credit assessment tools."""
    from tools.feature_engine import build_feature_vector
    from tools.ml_scorer import score as ml_score
    from tools.risk_calculator import compute_composite
    from tools.fairness_metrics import run_fairness_check
    from tools.report_generator import generate_report
    from mock_data.personas import PERSONAS

    registry = ToolRegistry()

    # ── Tool: fetch_borrower_data ─────────────────────────────────────────────
    def fetch_borrower_data(borrower_id: str) -> dict:
        if borrower_id not in PERSONAS:
            raise ValueError(f"Unknown borrower: {borrower_id}")
        p = PERSONAS[borrower_id]
        sources = {k: p.get(k) is not None for k in ("bank_data", "utility_data", "mobile_data")}
        return {
            "borrower_id": borrower_id,
            "name": p["name"],
            "scenario": p["scenario"],
            "loan_amount_requested": float(p.get("loan_amount_requested", 0.0)),
            "bank_data": p.get("bank_data"),
            "utility_data": p.get("utility_data"),
            "mobile_data": p.get("mobile_data"),
            "profile": p.get("profile", {}),
            "sources_available": sources,
            "data_completeness": sum(sources.values()) / 3.0,
        }

    registry.register(ToolSpec(
        name="fetch_borrower_data",
        description="Fetch all available data for a borrower (bank, utility, mobile). Returns completeness score.",
        parameters={"borrower_id": "string — e.g. 'borrower_001'"},
        fn=fetch_borrower_data,
        required_params=["borrower_id"],
    ))

    # ── Tool: compute_financial_score ─────────────────────────────────────────
    def compute_financial_score(bank_data: dict | None, profile: dict = None) -> dict:
        is_underbanked = bank_data is None
        features = build_feature_vector(bank_data, profile=profile)
        try:
            fin_score, shap_array = ml_score(features, is_underbanked=is_underbanked)
        except FileNotFoundError:
            from agents.financial_scoring import FinancialScoringAgent
            agent = FinancialScoringAgent()
            result = agent.run(bank_data, profile=profile)
            return result
        from tools.feature_engine import FEATURES
        shap_summary = {}
        if shap_array is not None:
            shap_summary = {f: float(v) for f, v in zip(FEATURES, shap_array)}
        return {
            "financial_score": fin_score,
            "features": features,
            "shap_summary": shap_summary,
            "is_underbanked": is_underbanked,
        }

    registry.register(ToolSpec(
        name="compute_financial_score",
        description="Run XGBoost ML model on bank data to get financial credit score (0-1000) + SHAP values. Pass None for thin-file borrowers.",
        parameters={"bank_data": "dict or null — raw bank data from fetch_borrower_data"},
        fn=compute_financial_score,
        required_params=["bank_data"],
    ))

    # ── Tool: compute_alternative_score ──────────────────────────────────────
    def compute_alternative_score(utility_data: dict | None, mobile_data: dict | None, has_bank_data: bool = True) -> dict:
        from agents.alternative_data import AlternativeDataAgent
        return AlternativeDataAgent().run(utility_data, mobile_data, has_bank_data)

    registry.register(ToolSpec(
        name="compute_alternative_score",
        description="Score borrower using utility payment history and mobile money data (0-1000). Critical for thin-file applicants.",
        parameters={
            "utility_data": "dict or null",
            "mobile_data": "dict or null",
            "has_bank_data": "bool — affects weighting",
        },
        fn=compute_alternative_score,
        required_params=["utility_data", "mobile_data"],
    ))

    # ── Tool: make_risk_decision ──────────────────────────────────────────────
    def make_risk_decision(
        financial_score: int,
        alternative_score: int,
        is_underbanked: bool,
        loan_amount_requested: float = 0.0,
        observed_monthly_cashflow: float = 0.0,
    ) -> dict:
        from agents.risk_decision import RiskDecisionAgent
        return RiskDecisionAgent().run(
            financial_score,
            alternative_score,
            is_underbanked,
            loan_amount_requested=loan_amount_requested,
            observed_monthly_cashflow=observed_monthly_cashflow,
        )

    registry.register(ToolSpec(
        name="make_risk_decision",
        description="Compute composite score and determine APPROVE/ESCALATE/DENY decision with credit terms.",
        parameters={
            "financial_score": "int 0-1000",
            "alternative_score": "int 0-1000",
            "is_underbanked": "bool",
            "loan_amount_requested": "float VND",
            "observed_monthly_cashflow": "float VND proxy from bank/mobile activity",
        },
        fn=make_risk_decision,
        required_params=["financial_score", "alternative_score", "is_underbanked"],
    ))

    # ── Tool: check_fairness ──────────────────────────────────────────────────
    def check_fairness(decision: str, composite_score: int, profile: dict) -> dict:
        fairness_metrics, bias_detected = run_fairness_check(decision, composite_score, profile)
        return {"fairness_metrics": fairness_metrics, "bias_detected": bias_detected}

    registry.register(ToolSpec(
        name="check_fairness",
        description="Run disparate impact, statistical parity, and counterfactual fairness checks. Returns bias_detected flag.",
        parameters={
            "decision": "str — APPROVE/ESCALATE/DENY",
            "composite_score": "int",
            "profile": "dict — gender, age_group, region, employment_type",
        },
        fn=check_fairness,
        required_params=["decision", "composite_score", "profile"],
    ))

    # ── Tool: generate_explanation ────────────────────────────────────────────
    def generate_explanation(borrower_name: str, composite_score: int, financial_score: int,
                              alternative_score: int, decision: str, risk_tier: str,
                              is_underbanked: bool, shap_summary: dict, features: dict) -> dict:
        from agents.explainability import ExplainabilityAgent
        return ExplainabilityAgent().run(
            borrower_name=borrower_name,
            features=features,
            shap_summary=shap_summary,
            composite_score=composite_score,
            financial_score=financial_score,
            alternative_score=alternative_score,
            decision=decision,
            risk_tier=risk_tier,
            is_underbanked=is_underbanked,
        )

    registry.register(ToolSpec(
        name="generate_explanation",
        description="Generate AI-written credit report with SHAP-based strengths/concerns using Claude/Gemini.",
        parameters={
            "borrower_name": "str",
            "composite_score": "int",
            "financial_score": "int",
            "alternative_score": "int",
            "decision": "str",
            "risk_tier": "str",
            "is_underbanked": "bool",
            "shap_summary": "dict",
            "features": "dict",
        },
        fn=generate_explanation,
        required_params=["borrower_name", "composite_score", "financial_score",
                         "alternative_score", "decision", "risk_tier", "is_underbanked",
                         "shap_summary", "features"],
    ))

    return registry
