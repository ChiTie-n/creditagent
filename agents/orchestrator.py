"""
orchestrator.py
OrchestratorAgent — coordinate all specialist agents.
"""

import sys
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.data_collection import DataCollectionAgent, InsufficientDataError
from agents.financial_scoring import FinancialScoringAgent
from agents.alternative_data import AlternativeDataAgent
from agents.risk_decision import RiskDecisionAgent
from agents.explainability import ExplainabilityAgent
from agents.bias_fairness import BiasFairnessAgent


class OrchestratorAgent:
    """Master agent coordinating the full credit assessment pipeline."""

    def __init__(self):
        self.data_agent = DataCollectionAgent()
        self.financial_agent = FinancialScoringAgent()
        self.alternative_agent = AlternativeDataAgent()
        self.risk_agent = RiskDecisionAgent()
        self.explain_agent = ExplainabilityAgent()
        self.fairness_agent = BiasFairnessAgent()

    def run(self, borrower_id: str) -> dict:
        """
        Full credit assessment pipeline.

        Returns
        -------
        CreditAssessmentResult dict
        """
        start_time = time.time()
        agent_pipeline = []

        def estimate_monthly_cashflow() -> float:
            bank_proxy = float((data.get("bank_data") or {}).get("PAY_AMT1", 0.0))
            mobile_proxy = float((data.get("mobile_data") or {}).get("monthly_volume", 0.0))
            return max(bank_proxy, mobile_proxy)

        # ── Step 1: Data Collection ──────────────────────────────────────────
        agent_pipeline.append({"agent": "DataCollectionAgent", "status": "running"})
        try:
            data = self.data_agent.run(borrower_id)
            agent_pipeline[-1]["status"] = "done"
            agent_pipeline[-1]["output"] = (
                f"Completeness: {data['data_completeness']:.0%} | "
                f"Sources: {sum(data['sources_available'].values())}/3"
            )
        except InsufficientDataError as e:
            return {"error": str(e), "borrower_id": borrower_id}

        # ── Step 2: Financial + Alternative scoring (parallel) ───────────────
        agent_pipeline.append({"agent": "FinancialScoringAgent", "status": "running"})
        agent_pipeline.append({"agent": "AlternativeDataAgent", "status": "running"})

        def run_financial():
            return self.financial_agent.run(data["bank_data"], profile=data["profile"])

        def run_alternative():
            return self.alternative_agent.run(
                data["utility_data"],
                data["mobile_data"],
                has_bank_data=data["bank_data"] is not None,
            )

        with ThreadPoolExecutor(max_workers=2) as executor:
            f_financial = executor.submit(run_financial)
            f_alternative = executor.submit(run_alternative)
            financial_result = f_financial.result()
            alternative_result = f_alternative.result()

        agent_pipeline[-2]["status"] = "done"
        agent_pipeline[-2]["output"] = f"Financial score: {financial_result['financial_score']}"
        agent_pipeline[-1]["status"] = "done"
        agent_pipeline[-1]["output"] = f"Alternative score: {alternative_result['alternative_score']}"

        # ── Step 3: Risk Decision ─────────────────────────────────────────────
        agent_pipeline.append({"agent": "RiskDecisionAgent", "status": "running"})
        risk_result = self.risk_agent.run(
            financial_score=financial_result["financial_score"],
            alternative_score=alternative_result["alternative_score"],
            is_underbanked=financial_result["is_underbanked"],
            loan_amount_requested=data.get("loan_amount_requested", 0.0),
            observed_monthly_cashflow=estimate_monthly_cashflow(),
        )
        agent_pipeline[-1]["status"] = "done"
        agent_pipeline[-1]["output"] = (
            f"Decision: {risk_result['decision']} | "
            f"Score: {risk_result['composite_score']} | "
            f"{risk_result['risk_tier']}"
        )

        # ── Step 4: Explainability + Fairness (parallel) ─────────────────────
        agent_pipeline.append({"agent": "ExplainabilityAgent", "status": "running"})
        agent_pipeline.append({"agent": "BiasFairnessAgent", "status": "running"})

        def run_explain():
            return self.explain_agent.run(
                borrower_name=data["name"],
                features=financial_result["features"],
                shap_summary=financial_result["shap_summary"],
                composite_score=risk_result["composite_score"],
                financial_score=financial_result["financial_score"],
                alternative_score=alternative_result["alternative_score"],
                decision=risk_result["decision"],
                risk_tier=risk_result["risk_tier"],
                is_underbanked=financial_result["is_underbanked"],
            )

        def run_fairness():
            return self.fairness_agent.run(
                decision=risk_result["decision"],
                composite_score=risk_result["composite_score"],
                profile=data["profile"],
            )

        with ThreadPoolExecutor(max_workers=2) as executor:
            f_explain = executor.submit(run_explain)
            f_fairness = executor.submit(run_fairness)
            explain_result = f_explain.result()
            fairness_result = f_fairness.result()

        agent_pipeline[-2]["status"] = "done"
        agent_pipeline[-2]["output"] = f"Report generated ({len(explain_result['report'])} chars)"
        agent_pipeline[-1]["status"] = "done"
        agent_pipeline[-1]["output"] = (
            f"Bias detected: {fairness_result['bias_detected']}"
        )

        # ── Step 5: Override logic ────────────────────────────────────────────
        final_decision = risk_result["decision"]
        confidence = risk_result["confidence"]

        if fairness_result["bias_detected"] or confidence < 0.70:
            if final_decision == "APPROVE":
                final_decision = "ESCALATE"
                agent_pipeline.append({
                    "agent": "OrchestratorAgent",
                    "status": "override",
                    "output": (
                        f"Decision overridden APPROVE→ESCALATE "
                        f"(bias_detected={fairness_result['bias_detected']}, "
                        f"confidence={confidence:.2f})"
                    ),
                })

        # ── Assemble result ───────────────────────────────────────────────────
        processing_time_ms = int((time.time() - start_time) * 1000)

        return {
            "borrower_id": borrower_id,
            "borrower_name": data["name"],
            "scenario": data["scenario"],
            "composite_score": risk_result["composite_score"],
            "risk_tier": risk_result["risk_tier"],
            "decision": final_decision,
            "credit_limit": risk_result["credit_limit"],
            "interest_rate_range": risk_result["interest_rate_range"],
            "financial_score": financial_result["financial_score"],
            "alternative_score": alternative_result["alternative_score"],
            "is_underbanked": financial_result["is_underbanked"],
            "key_strengths": explain_result["key_strengths"],
            "key_concerns": explain_result["key_concerns"],
            "report": explain_result["report"],
            "bias_detected": fairness_result["bias_detected"],
            "fairness_metrics": fairness_result["fairness_metrics"],
            "processing_time_ms": processing_time_ms,
            "data_completeness": data["data_completeness"],
            "shap_summary": explain_result["shap_summary"],
            "score_breakdown": risk_result["score_breakdown"],
            "alternative_signals": alternative_result["signals"],
            "agent_pipeline": agent_pipeline,
            "confidence": confidence,
        }
