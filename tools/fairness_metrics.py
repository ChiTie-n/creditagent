"""
fairness_metrics.py
Compute Disparate Impact, Statistical Parity, and Counterfactual Fairness.
"""

import numpy as np
from typing import Callable, Optional


def compute_disparate_impact(
    group_a_approval_rate: float,
    group_b_approval_rate: float,
) -> float:
    """
    DIR = min_group_rate / max_group_rate.
    Threshold: >= 0.80 (4/5 rule).
    """
    if group_b_approval_rate == 0:
        return 0.0
    return group_a_approval_rate / group_b_approval_rate


def compute_statistical_parity(
    group_a_approval_rate: float,
    group_b_approval_rate: float,
) -> float:
    """
    |P(approve|A) - P(approve|B)|
    Threshold: <= 0.10
    """
    return abs(group_a_approval_rate - group_b_approval_rate)


def compute_counterfactual_fairness(
    original_score: int,
    counterfactual_score: int,
    threshold_pct: float = 5.0,
) -> dict:
    """
    Flip a protected attribute, recompute score, measure change.
    Fair if abs(score_change) / original_score * 100 <= threshold_pct
    """
    if original_score == 0:
        pct_change = 0.0
    else:
        pct_change = abs(original_score - counterfactual_score) / original_score * 100

    return {
        "original_score": original_score,
        "counterfactual_score": counterfactual_score,
        "score_change_pct": round(pct_change, 2),
        "is_fair": pct_change <= threshold_pct,
    }


def simulate_counterfactual_score(
    base_score: int,
    profile: dict,
) -> int:
    """
    Simulate what the score would be if we flipped the gender attribute.
    In a truly fair model, this should not change.
    We add a small random perturbation to simulate real-world variance.
    """
    # In our mock system, the score is deterministic on non-protected attributes.
    # We add ±2% noise to simulate minor model sensitivity.
    np.random.seed(hash(str(profile)) % (2**31))  # deterministic per profile
    noise = np.random.uniform(-0.02, 0.02)
    cf_score = int(round(base_score * (1 + noise)))
    return max(0, min(1000, cf_score))


def run_fairness_check(
    decision: str,
    composite_score: int,
    profile: dict,
) -> dict:
    """
    Run all fairness checks for a borrower.

    Returns fairness_metrics dict and bias_detected bool.
    """
    gender = profile.get("gender", "unknown")
    age_group = profile.get("age_group", "unknown")
    region = profile.get("region", "unknown")
    employment = profile.get("employment_type", "unknown")

    # ── Simulated group approval rates (based on historical demo data) ───────
    # In a real system these would be computed over the full population.
    # Here we use plausible illustrative values.
    DEMO_APPROVAL_RATES = {
        "gender": {"male": 0.72, "female": 0.68},
        "age_group": {"18-25": 0.55, "25-35": 0.69, "35-45": 0.78, "45+": 0.74},
        "region": {"urban": 0.78, "suburban": 0.68, "rural": 0.65},  # Rural vs Urban
        "employment_type": {
            "business_owner": 0.82,
            "employee": 0.75,
            "self_employed": 0.60,
            "street_vendor": 0.50,
            "farmer": 0.48,
            "food_stall_owner": 0.62,
            "household_business": 0.70
        },
    }

    metrics = {}
    bias_flags = []

    # Gender fairness
    if gender in DEMO_APPROVAL_RATES["gender"]:
        ref_gender = "male" if gender == "female" else "female"
        dir_gender = compute_disparate_impact(
            DEMO_APPROVAL_RATES["gender"][gender],
            DEMO_APPROVAL_RATES["gender"][ref_gender],
        )
        sp_gender = compute_statistical_parity(
            DEMO_APPROVAL_RATES["gender"][gender],
            DEMO_APPROVAL_RATES["gender"][ref_gender],
        )
        metrics["gender_disparate_impact"] = round(dir_gender, 3)
        metrics["gender_statistical_parity"] = round(sp_gender, 3)
        if dir_gender < 0.80:
            bias_flags.append("gender_disparate_impact")
        if sp_gender > 0.10:
            bias_flags.append("gender_statistical_parity")

    # Regional fairness
    if region in DEMO_APPROVAL_RATES["region"]:
        ref_region = "urban"
        dir_region = compute_disparate_impact(
            DEMO_APPROVAL_RATES["region"][region],
            DEMO_APPROVAL_RATES["region"][ref_region],
        )
        metrics["regional_disparate_impact"] = round(dir_region, 3)
        if dir_region < 0.80:
            bias_flags.append("regional_disparate_impact")

    # Employment fairness (e.g. farmer vs formal employee)
    if employment in DEMO_APPROVAL_RATES["employment_type"]:
        ref_emp = "employee"
        dir_emp = compute_disparate_impact(
            DEMO_APPROVAL_RATES["employment_type"][employment],
            DEMO_APPROVAL_RATES["employment_type"][ref_emp],
        )
        metrics["employment_disparate_impact"] = round(dir_emp, 3)
        if dir_emp < 0.80:
            bias_flags.append("employment_disparate_impact")

    # Counterfactual fairness (gender flip)
    cf_score = simulate_counterfactual_score(composite_score, profile)
    cf_result = compute_counterfactual_fairness(composite_score, cf_score)
    metrics["counterfactual_fairness"] = cf_result
    if not cf_result["is_fair"]:
        bias_flags.append("counterfactual_score_change")

    bias_detected = len(bias_flags) > 0

    metrics["bias_flags"] = bias_flags
    metrics["overall_fair"] = not bias_detected

    return metrics, bias_detected
