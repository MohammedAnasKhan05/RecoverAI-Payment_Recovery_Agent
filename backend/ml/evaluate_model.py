"""
Model Evaluation and Inference Utility for RecoverAI.
Loads the trained fraud model and provides risk scoring for arbitrary transactions.
"""
import joblib
import pandas as pd
from pathlib import Path
from typing import Dict, Any

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "ml" / "fraud_model.pkl"

_model = None

def get_fraud_model():
    global _model
    if _model is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(f"Fraud model not found at {MODEL_PATH}. Run train_model.py first.")
        _model = joblib.load(MODEL_PATH)
    return _model

def predict_transaction_fraud_risk(tx_data: Dict[str, Any]) -> float:
    """
    Given a transaction dict, calculate fraud risk probability between 0.0 and 1.0.
    Falls back gracefully if specific PaySim balance fields are omitted.
    """
    model = get_fraud_model()
    
    amount = float(tx_data.get("amount", 0.0))
    tx_type = str(tx_data.get("type", "PAYMENT")).upper()
    oldbalance_org = float(tx_data.get("oldbalanceOrg", tx_data.get("customer_balance", amount * 2.5)))
    newbalance_orig = float(tx_data.get("newbalanceOrig", max(0.0, oldbalance_org - amount)))
    oldbalance_dest = float(tx_data.get("oldbalanceDest", 0.0))
    newbalance_dest = float(tx_data.get("newbalanceDest", oldbalance_dest + amount))
    
    row = {
        "amount": amount,
        "oldbalanceOrg": oldbalance_org,
        "newbalanceOrig": newbalance_orig,
        "oldbalanceDest": oldbalance_dest,
        "newbalanceDest": newbalance_dest,
        "type": tx_type,
        "balance_change_orig": oldbalance_org - newbalance_orig,
        "balance_change_dest": newbalance_dest - oldbalance_dest,
        "amount_to_balance_ratio": amount / (oldbalance_org + 1.0),
        "origin_zero_balance": 1 if newbalance_orig == 0 else 0,
        "destination_zero_balance": 1 if oldbalance_dest == 0 else 0,
    }
    
    df = pd.DataFrame([row])
    prob = float(model.predict_proba(df)[0, 1])
    return round(prob, 4)

if __name__ == "__main__":
    test_cases = [
        {"amount": 500.0, "type": "PAYMENT", "oldbalanceOrg": 5000.0, "newbalanceOrig": 4500.0, "oldbalanceDest": 1000.0, "newbalanceDest": 1500.0},
        {"amount": 120000.0, "type": "TRANSFER", "oldbalanceOrg": 120000.0, "newbalanceOrig": 0.0, "oldbalanceDest": 0.0, "newbalanceDest": 0.0},
    ]
    for i, tc in enumerate(test_cases, 1):
        score = predict_transaction_fraud_risk(tc)
        print(f"Test case {i} ({tc['type']} of INR {tc['amount']}): Fraud Risk = {score:.4f}")
