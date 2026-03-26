"""
risk_decision.py
RiskDecisionAgent - compute composite score and determine risk tier + decision.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.risk_calculator import compute_composite


class RiskDecisionAgent:
    """Combine financial and alternative scores into a credit decision."""

    @staticmethod
    def _capacity_adjustment(
        decision: str,
        risk_tier: str,
        credit_limit: float,
        loan_amount_requested: float,
        observed_monthly_cashflow: float,
    ) -> tuple[str, str, dict]:
        adjustment = {
            "loan_amount_requested": round(loan_amount_requested, 2),
            "observed_monthly_cashflow": round(observed_monthly_cashflow, 2),
            "requested_to_limit_ratio": None,
            "requested_to_annual_cashflow_ratio": None,
            "affordability_flag": "normal",
            "override_reason": None,
        }

        if loan_amount_requested <= 0:
            return decision, risk_tier, adjustment

        if credit_limit > 0:
            ratio_to_limit = loan_amount_requested / credit_limit
            adjustment["requested_to_limit_ratio"] = round(ratio_to_limit, 3)
        else:
            ratio_to_limit = float("inf")

        annual_cashflow = observed_monthly_cashflow * 12 if observed_monthly_cashflow > 0 else 0.0
        ratio_to_cashflow = None
        if annual_cashflow > 0:
            ratio_to_cashflow = loan_amount_requested / annual_cashflow
            adjustment["requested_to_annual_cashflow_ratio"] = round(ratio_to_cashflow, 3)

        if ratio_to_limit > 5 or (ratio_to_cashflow is not None and ratio_to_cashflow > 5):
            adjustment["affordability_flag"] = "severely_overstretched"
            adjustment["override_reason"] = (
                "Requested loan materially exceeds the recommended limit or observed cashflow capacity."
            )
            return "DENY", "Rui ro cao", adjustment

        if ratio_to_limit > 1 or (ratio_to_cashflow is not None and ratio_to_cashflow > 2):
            adjustment["affordability_flag"] = "overstretched"
            adjustment["override_reason"] = (
                "Requested loan is above the recommended limit or elevated relative to observed annual cashflow."
            )
            if decision == "DENY":
                return decision, risk_tier, adjustment
            return "ESCALATE", "Rui ro trung binh", adjustment

        return decision, risk_tier, adjustment

    def run(
        self,
        financial_score: int,
        alternative_score: int,
        is_underbanked: bool,
        behavioral_score: int = 500,
        loan_amount_requested: float = 0.0,
        observed_monthly_cashflow: float = 0.0,
    ) -> dict:
        """
        Parameters
        ----------
        financial_score : int 0-1000
        alternative_score : int 0-1000
        is_underbanked : bool
        behavioral_score : int 0-1000
        loan_amount_requested : float VND
        observed_monthly_cashflow : float VND proxy from bank/mobile signals

        Returns
        -------
        dict with composite_score, risk_tier, decision, credit terms
        """
        result = compute_composite(
            financial_score=financial_score,
            alternative_score=alternative_score,
            is_underbanked=is_underbanked,
            behavioral_score=behavioral_score,
        )

        adjusted_decision, adjusted_risk_tier, affordability = self._capacity_adjustment(
            decision=result.decision,
            risk_tier=result.risk_tier,
            credit_limit=result.credit_limit,
            loan_amount_requested=loan_amount_requested,
            observed_monthly_cashflow=observed_monthly_cashflow,
        )

        confidence = result.composite_score / 1000.0

        return {
            "composite_score": result.composite_score,
            "risk_tier": adjusted_risk_tier,
            "decision": adjusted_decision,
            "credit_limit": result.credit_limit,
            "interest_rate_range": result.interest_rate_range,
            "financial_weight": result.financial_weight,
            "alternative_weight": result.alternative_weight,
            "confidence": round(confidence, 3),
            "score_breakdown": {
                "financial_score": financial_score,
                "alternative_score": alternative_score,
                "behavioral_score": behavioral_score,
                "is_underbanked": is_underbanked,
                **affordability,
            },
        }
