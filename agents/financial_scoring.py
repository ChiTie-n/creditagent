"""
financial_scoring.py
FinancialScoringAgent — XGBoost-based financial credit scoring.
"""

import sys
import os
from typing import Optional
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class FinancialScoringAgent:
    """Score borrower using ML model on financial features."""

    def run(self, bank_data: Optional[dict], profile: dict = None) -> dict:
        """
        Parameters
        ----------
        bank_data : dict or None — raw bank data from DataCollectionAgent
        profile : dict — demographic user profile

        Returns
        -------
        dict with keys: financial_score, features, shap_values, shap_summary, is_underbanked
        """
        from tools.feature_engine import build_feature_vector, FEATURES
        from tools.ml_scorer import score, get_feature_names

        is_underbanked = bank_data is None
        features = build_feature_vector(bank_data, profile=profile)

        try:
            financial_score, shap_array = score(features, is_underbanked=is_underbanked)
        except FileNotFoundError as e:
            # Model not trained yet — return a simulated score
            print(f"[FinancialScoringAgent] WARNING: {e}")
            financial_score = 350 if is_underbanked else self._heuristic_score(bank_data)
            shap_array = None

        feature_names = FEATURES
        shap_summary = {}
        if shap_array is not None:
            shap_summary = {
                feat: float(val)
                for feat, val in zip(feature_names, shap_array)
            }

        return {
            "financial_score": financial_score,
            "features": features,
            "shap_values": shap_array.tolist() if shap_array is not None else [],
            "shap_summary": shap_summary,
            "is_underbanked": is_underbanked,
            "feature_names": feature_names,
        }

    def _heuristic_score(self, bank_data: dict) -> int:
        """Fallback score if model not available."""
        dti = bank_data.get("dti", 0.5)
        on_time = bank_data.get("on_time_rate", 0.7)
        pub_rec = bank_data.get("pub_rec", 0)
        delinq = bank_data.get("delinq_2yrs", 0)

        score = 500
        score -= int(dti * 300)           # High DTI → lower score
        score += int(on_time * 300)       # Payment history matters
        score -= pub_rec * 50             # Derogatory records hurt
        score -= delinq * 30
        return max(100, min(950, score))
