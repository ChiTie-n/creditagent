"""
feature_engine.py
Transform raw bank_data (Taiwan Credit Card Dataset) → normalized feature vector.
"""

import numpy as np
from typing import Optional

FEATURES = [
    "LIMIT_BAL",
    "SEX",
    "EDUCATION",
    "MARRIAGE",
    "AGE",
    "PAY_0",
    "PAY_2",
    "PAY_3",
    "BILL_AMT1",
    "PAY_AMT1",
]

MEDIANS = {
    "LIMIT_BAL": 100_000.0,
    "SEX": 2.0,       # 2=Female
    "EDUCATION": 2.0, # 2=University
    "MARRIAGE": 2.0,  # 2=Single
    "AGE": 30.0,
    "PAY_0": 0.0,
    "PAY_2": 0.0,
    "PAY_3": 0.0,
    "BILL_AMT1": 50_000.0,
    "PAY_AMT1": 5_000.0,
}


def build_feature_vector(bank_data: Optional[dict], profile: dict = None) -> dict:
    """
    Convert raw bank_data to model features.
    If bank_data is None (thin-file), use median imputation with pessimistic defaults.
    """
    if profile is None:
        profile = {}

    sex = 1.0 if profile.get("gender") == "male" else 2.0
    age = 40.0 if "old" in profile.get("age_group", "") else 30.0
    
    if bank_data is None:
        # Thin-file borrower
        features = {k: float(MEDIANS[k]) for k in FEATURES}
        features["SEX"] = sex
        features["AGE"] = age
        features["PAY_0"] = 1.0  # slight pessimistic delay
        features["PAY_2"] = 1.0
        features["PAY_3"] = 1.0
        return features

    # Direct passthrough for Taiwan dataset variables
    return {
        "LIMIT_BAL": float(bank_data.get("LIMIT_BAL", MEDIANS["LIMIT_BAL"])),
        "SEX": float(bank_data.get("SEX", sex)),
        "EDUCATION": float(bank_data.get("EDUCATION", 2.0)),
        "MARRIAGE": float(bank_data.get("MARRIAGE", 2.0)),
        "AGE": float(bank_data.get("AGE", age)),
        "PAY_0": float(bank_data.get("PAY_0", 0.0)),
        "PAY_2": float(bank_data.get("PAY_2", 0.0)),
        "PAY_3": float(bank_data.get("PAY_3", 0.0)),
        "BILL_AMT1": float(bank_data.get("BILL_AMT1", MEDIANS["BILL_AMT1"])),
        "PAY_AMT1": float(bank_data.get("PAY_AMT1", MEDIANS["PAY_AMT1"])),
    }

def to_array(features: dict) -> np.ndarray:
    return np.array([[features[f] for f in FEATURES]], dtype=np.float32)
