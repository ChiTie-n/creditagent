"""
bias_fairness.py
BiasFairnessAgent — run fairness metrics and flag bias.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.fairness_metrics import run_fairness_check


class BiasFairnessAgent:
    """Evaluate credit decision for fairness across protected attributes."""

    def run(
        self,
        decision: str,
        composite_score: int,
        profile: dict,
    ) -> dict:
        """
        Parameters
        ----------
        decision        : str — APPROVE / ESCALATE / DENY
        composite_score : int — 0-1000
        profile         : dict — gender, age_group, region, employment_type

        Returns
        -------
        dict with fairness_metrics (dict), bias_detected (bool)
        """
        fairness_metrics, bias_detected = run_fairness_check(
            decision=decision,
            composite_score=composite_score,
            profile=profile,
        )

        return {
            "fairness_metrics": fairness_metrics,
            "bias_detected": bias_detected,
            "profile_evaluated": profile,
        }
