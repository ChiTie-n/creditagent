"""
risk_calculator.py
Compute composite score and map to risk tier / decision / credit terms.
"""

from dataclasses import dataclass, field
from typing import Optional


RISK_TABLE = [
    # (min_score, max_score, risk_tier, decision, max_credit_vnd, rate_range)
    (680, 1000, "Rủi ro thấp",       "APPROVE",   200_000_000, "8-12%"),
    (520,  679, "Rủi ro trung bình", "ESCALATE",  80_000_000,  "15-20%"),
    (380,  519, "Rủi ro cao",        "DENY",      0,           "N/A"),
    (0,    379, "Rủi ro rất cao",    "DENY",      0,           "N/A"),
]


@dataclass
class CompositeResult:
    composite_score: int
    risk_tier: str
    decision: str
    credit_limit: float
    interest_rate_range: str
    financial_weight: float
    alternative_weight: float


def compute_composite(
    financial_score: int,
    alternative_score: int,
    is_underbanked: bool,
    behavioral_score: int = 500,
) -> CompositeResult:
    """
    Compute weighted composite score.

    Underbanked micro-SME (no bank data) — common in Vietnam rural/informal sector:
        financial * 0.00 + alternative * 0.80 + behavioral * 0.20
    Standard SME with some banking history:
        financial * 0.50 + alternative * 0.30 + behavioral * 0.20
    """
    if is_underbanked:
        fw, aw, bw = 0.0, 0.80, 0.20
        # When underbanked, utilize alternative score as proxy for overall behavioral discipline
        behavioral_score = alternative_score
    else:
        fw, aw, bw = 0.50, 0.30, 0.20

    composite = int(round(
        financial_score * fw +
        alternative_score * aw +
        behavioral_score * bw
    ))
    composite = max(0, min(1000, composite))

    # Lookup risk tier
    for lo, hi, tier, decision, max_credit, rate in RISK_TABLE:
        if lo <= composite <= hi:
            return CompositeResult(
                composite_score=composite,
                risk_tier=tier,
                decision=decision,
                credit_limit=float(max_credit),
                interest_rate_range=rate,
                financial_weight=fw,
                alternative_weight=aw,
            )

    # Fallback
    return CompositeResult(
        composite_score=composite,
        risk_tier="Rủi ro rất cao",
        decision="DENY",
        credit_limit=0.0,
        interest_rate_range="N/A",
        financial_weight=fw,
        alternative_weight=aw,
    )
