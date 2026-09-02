"""
RecoverAI Fraud Risk Model Training Script
Trains a lightweight, fast RandomForestClassifier on PaySim-style fraud data.
Uses chunked sampling to avoid excessive memory usage.
"""
import os
import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_FRAUD_PATH = BASE_DIR / "data" / "raw" / "Fraud.csv"
MODEL_SAVE_PATH = BASE_DIR / "ml" / "fraud_model.pkl"

def load_sampled_data(csv_path: Path, max_non_fraud: int = 25000, max_fraud: int = 5000) -> pd.DataFrame:
    """Load a balanced sample from the large Fraud.csv dataset using chunked reading."""
    print(f"Loading sampled data from {csv_path}...")
    fraud_records = []
    non_fraud_records = []
    
    chunk_size = 100000
    for chunk in pd.read_csv(csv_path, chunksize=chunk_size):
        frauds = chunk[chunk["isFraud"] == 1]
        non_frauds = chunk[chunk["isFraud"] == 0]
        
        if len(frauds) > 0:
            fraud_records.append(frauds)
        
        # Sample non-frauds proportionally to avoid memory bloat
        if sum(len(nf) for nf in non_fraud_records) < max_non_fraud:
            sample_nf = non_frauds.sample(n=min(len(non_frauds), 5000), random_state=42)
            non_fraud_records.append(sample_nf)
            
        total_frauds = sum(len(f) for f in fraud_records)
        if total_frauds >= max_fraud:
            break

    df_fraud = pd.concat(fraud_records, ignore_index=True).iloc[:max_fraud]
    df_non_fraud = pd.concat(non_fraud_records, ignore_index=True).iloc[:max_non_fraud]
    
    combined = pd.concat([df_fraud, df_non_fraud], ignore_index=True).sample(frac=1.0, random_state=42)
    print(f"Loaded {len(combined)} samples ({len(df_fraud)} fraud, {len(df_non_fraud)} non-fraud).")
    return combined

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Engineer critical transaction and balance delta features."""
    df = df.copy()
    df["balance_change_orig"] = df["oldbalanceOrg"] - df["newbalanceOrig"]
    df["balance_change_dest"] = df["newbalanceDest"] - df["oldbalanceDest"]
    df["amount_to_balance_ratio"] = df["amount"] / (df["oldbalanceOrg"] + 1.0)
    df["origin_zero_balance"] = (df["newbalanceOrig"] == 0).astype(int)
    df["destination_zero_balance"] = (df["oldbalanceDest"] == 0).astype(int)
    return df

def train_and_save_model():
    if not RAW_FRAUD_PATH.exists():
        raise FileNotFoundError(f"Fraud dataset not found at {RAW_FRAUD_PATH}")
        
    raw_df = load_sampled_data(RAW_FRAUD_PATH)
    df = engineer_features(raw_df)
    
    numeric_features = [
        "amount",
        "oldbalanceOrg",
        "newbalanceOrig",
        "oldbalanceDest",
        "newbalanceDest",
        "balance_change_orig",
        "balance_change_dest",
        "amount_to_balance_ratio",
        "origin_zero_balance",
        "destination_zero_balance"
    ]
    categorical_features = ["type"]
    
    X = df[numeric_features + categorical_features]
    y = df["isFraud"]
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", "passthrough", numeric_features),
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features)
        ]
    )
    
    clf = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("classifier", RandomForestClassifier(n_estimators=60, max_depth=10, random_state=42, n_jobs=-1))
    ])
    
    print("Training RandomForest model...")
    clf.fit(X_train, y_train)
    
    y_pred = clf.predict(X_test)
    y_prob = clf.predict_proba(X_test)[:, 1]
    
    print("\n--- Model Evaluation ---")
    print(classification_report(y_test, y_pred))
    auc = roc_auc_score(y_test, y_prob)
    print(f"ROC-AUC Score: {auc:.4f}")
    
    MODEL_SAVE_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(clf, MODEL_SAVE_PATH)
    print(f"\nModel successfully saved to {MODEL_SAVE_PATH}")

if __name__ == "__main__":
    train_and_save_model()
