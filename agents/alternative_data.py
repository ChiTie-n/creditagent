"""
alternative_data.py
AlternativeDataAgent — score based on utility and mobile money data.
"""

import sys
import os
from typing import Optional
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class AlternativeDataAgent:
    """Compute alternative credit score from non-bank data sources."""

    # Score component weights (sum = 1000 max)
    UTILITY_WEIGHT = 400
    CONSISTENCY_WEIGHT = 350
    MOBILE_WEIGHT = 250

    # Normalization reference for mobile volume (VND)
    MOBILE_VOL_REFERENCE = 50_000_000  # 50M VND/month = full score

    def run(
        self,
        utility_data: Optional[dict],
        mobile_data: Optional[dict],
        has_bank_data: bool = True,
    ) -> dict:
        """
        Parameters
        ----------
        utility_data : dict or None
        mobile_data  : dict or None
        has_bank_data : bool — changes weighting in composite

        Returns
        -------
        dict with alternative_score (0-1000), component breakdown, signals
        """
        signals = {}
        score_components = {}

        # ── Utility payments ────────────────────────────────────────────────
        if utility_data:
            on_time = utility_data.get("on_time_rate", 0.0)
            months = min(utility_data.get("months_history", 0), 72)  # cap at 6 years
            history_factor = months / 72.0
            # Full weight at 72 months; 48 months = 0.667 history_factor
            utility_component = (
                on_time * self.UTILITY_WEIGHT * (0.5 + 0.5 * history_factor)
            )
            signals["utility_on_time_rate"] = on_time
            signals["utility_months_history"] = months
        else:
            utility_component = self.UTILITY_WEIGHT * 0.3  # default penalty

        score_components["utility"] = round(utility_component, 1)

        # ── Mobile money consistency ────────────────────────────────────────
        if mobile_data:
            consistency = mobile_data.get("consistency_score", 0.0)
            monthly_vol = mobile_data.get("monthly_volume", 0)
            vol_normalized = min(monthly_vol / self.MOBILE_VOL_REFERENCE, 1.0)

            consistency_component = consistency * self.CONSISTENCY_WEIGHT
            mobile_component = vol_normalized * self.MOBILE_WEIGHT

            signals["mobile_consistency_score"] = consistency
            signals["mobile_monthly_volume"] = monthly_vol
            signals["mobile_volume_normalized"] = round(vol_normalized, 3)
        else:
            consistency_component = self.CONSISTENCY_WEIGHT * 0.2
            mobile_component = self.MOBILE_WEIGHT * 0.2

        score_components["consistency"] = round(consistency_component, 1)
        score_components["mobile_volume"] = round(mobile_component, 1)

        # ── Total alternative score ─────────────────────────────────────────
        alternative_score = int(round(
            utility_component + consistency_component + mobile_component
        ))
        alternative_score = max(0, min(1000, alternative_score))

        # Weight to use in composite calculation
        alt_weight = 0.60 if not has_bank_data else 0.30

        return {
            "alternative_score": alternative_score,
            "score_components": score_components,
            "signals": signals,
            "alternative_weight": alt_weight,
            "data_sources_used": {
                "utility": utility_data is not None,
                "mobile": mobile_data is not None,
            },
        }

if __name__ == "__main__":
    # Sample usage to run and test the AlternativeDataAgent directly
    agent = AlternativeDataAgent()
    
    sample_utility_data = {
        "on_time_rate": 0.95,
        "months_history": 24
    }
    
    sample_mobile_data = {
        "consistency_score": 0.8,
        "monthly_volume": 20_000_000
    }
    
    print("Running AlternativeDataAgent with sample data...")
    result = agent.run(
        utility_data=sample_utility_data,
        mobile_data=sample_mobile_data,
        has_bank_data=False
    )
    
    import json
    print(json.dumps(result, indent=2))
