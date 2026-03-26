"""
Train XGBoost model on the external Taiwan Credit Card dataset (xls).
Saves model to models/xgboost_model.pkl
"""

import os
import sys
import pickle
import numpy as np
import pandas as pd
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from aws_integration import upload_model_to_s3
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
import xgboost as xgb

# ── Paths ────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent.parent
DATA_PATH = os.getenv("DATA_PATH", str(ROOT / "data" / "default of credit card clients.xls"))
MODEL_DIR = ROOT / "models"
MODEL_DIR.mkdir(exist_ok=True)

# We select the top 10 most informative features from the Taiwan dataset
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
TARGET = "default payment next month"
RANDOM_STATE = 42

def load_and_prepare(path: str) -> pd.DataFrame:
    print(f"Loading data from Excel: {path}")
    # The Taiwan dataset usually has its header on the second row (index 1)
    df = pd.read_excel(path, header=1)
    print(f"Total rows: {len(df):,}")

    df["label"] = df[TARGET]

    # Keep only needed columns
    keep_cols = FEATURES + ["label"]
    df = df[keep_cols].copy()

    # Fill missing values with median just in case
    for col in FEATURES:
        df[col] = df[col].fillna(df[col].median())

    print(f"Label distribution:\n{df['label'].value_counts()}")
    return df

def train(df: pd.DataFrame):
    X = df[FEATURES].values
    y = df["label"].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y
    )

    print("\nTraining XGBoost on Taiwan Dataset…")
    model = xgb.XGBClassifier(
        n_estimators=150,
        max_depth=5,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        scale_pos_weight=(y_train == 0).sum() / (y_train == 1).sum(),
        eval_metric="auc",
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )
    model.fit(
        X_train,
        y_train,
        eval_set=[(X_test, y_test)],
        verbose=10,
    )

    y_pred_proba = model.predict_proba(X_test)[:, 1]
    auc = roc_auc_score(y_test, y_pred_proba)
    print(f"\n✅  Test AUC: {auc:.4f}")

    # Feature importance
    print("\nFeature Importances:")
    for feat, imp in sorted(zip(FEATURES, model.feature_importances_), key=lambda x: -x[1]):
        print(f"  {feat:<25} {imp:.4f}")

    return model

def save(model):
    model_path = MODEL_DIR / "xgboost_model.pkl"
    feat_path = MODEL_DIR / "feature_names.pkl"
    with open(model_path, "wb") as f:
        pickle.dump(model, f)
    with open(feat_path, "wb") as f:
        pickle.dump(FEATURES, f)
    print(f"\n✅  Model saved → {model_path}")
    print(f"✅  Feature names saved → {feat_path}")

if __name__ == "__main__":
    try:
        from dotenv import load_dotenv
        load_dotenv(ROOT / ".env")
        DATA_PATH = os.getenv("DATA_PATH", DATA_PATH)
    except ImportError:
        pass

    try:
        df = load_and_prepare(DATA_PATH)
        model = train(df)
        save(model)
        upload_model_to_s3(str(MODEL_DIR / "xgboost_model.pkl"))
        print("\n🎉  Training complete!")
    except Exception as e:
        print(f"ERROR: {e}")
