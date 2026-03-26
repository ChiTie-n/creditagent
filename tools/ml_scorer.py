"""
ml_scorer.py
Load XGBoost model and compute credit score (0-1000) + SHAP values.
"""

import pickle
import numpy as np
from pathlib import Path
from typing import Tuple

MODEL_PATH = Path(__file__).parent.parent / "models" / "xgboost_model.pkl"
FEAT_PATH = Path(__file__).parent.parent / "models" / "feature_names.pkl"

_model = None
_explainer = None
_feature_names = None


def _load():
    global _model, _explainer, _feature_names
    if _model is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Model not found at {MODEL_PATH}. "
                "Please run `python data/train_model.py` first."
            )
        with open(MODEL_PATH, "rb") as f:
            _model = pickle.load(f)
        with open(FEAT_PATH, "rb") as f:
            _feature_names = pickle.load(f)

        import shap
        _explainer = shap.TreeExplainer(_model)


def score(features: dict, is_underbanked: bool = False) -> Tuple[int, np.ndarray]:
    """
    Compute ML credit score (0-1000) and SHAP values.

    For thin-file (underbanked) borrowers, we return a neutral score of 500
    because the ML model was trained on banked customers and cannot reliably
    score someone with no banking history. The alternative data agent handles
    their assessment.

    Parameters
    ----------
    features : dict mapping feature names → float values
    is_underbanked : bool — if True, return neutral score 500

    Returns
    -------
    (score_0_1000, shap_values_array)
    """
    _load()

    from tools.feature_engine import FEATURES, to_array
    X = to_array(features)

    if is_underbanked:
        # Return neutral uncertainty score — alternative data drives decision
        # Still compute SHAP to show which factors are unknown
        shap_vals = _explainer.shap_values(X)
        if isinstance(shap_vals, list):
            shap_vals = shap_vals[1]
        shap_array = shap_vals[0]
        return 500, shap_array

    # Probability of DEFAULT (class=1)
    prob_default = _model.predict_proba(X)[0, 1]

    # Convert to credit score: high prob_default → low score
    credit_score = int(round((1.0 - prob_default) * 1000))
    credit_score = max(0, min(1000, credit_score))

    # SHAP values for class=1 (default risk contribution)
    shap_vals = _explainer.shap_values(X)
    # For XGBoost binary classification, shap_values returns array of shape (1, n_features)
    if isinstance(shap_vals, list):
        shap_vals = shap_vals[1]  # class=1
    shap_array = shap_vals[0]  # first (only) sample

    return credit_score, shap_array


def get_feature_names() -> list:
    _load()
    return _feature_names
