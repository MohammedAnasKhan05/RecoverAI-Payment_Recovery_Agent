"""
Failure & Context Analyzer Service for RecoverAI.
Synthesizes transaction signals, failure taxonomy, and customer relationship history
to produce deep contextual intelligence rather than naive error code mapping.
"""
from typing import Dict, Any

def classify_failure(failure_reason: str, fraud_score: float, attempt_number: int) -> Dict[str, Any]:
    reason = (failure_reason or "").lower().strip()

    if fraud_score > 0.70:
        category = "SUSPICIOUS_HIGH_RISK"
        is_retryable = False
        urgency = "HIGH"
        desc = "High-risk fraud signals detected. Requires manual risk desk inspection."
    elif attempt_number >= 2:
        category = "REPEATED_FAILURE"
        is_retryable = False
        urgency = "LOW"
        desc = f"Transaction has failed across {attempt_number} attempts. Exceeded automatic retry cap."
    elif any(kw in reason for kw in ["timeout", "gateway", "latency", "bank_drop", "network"]):
        category = "TEMPORARY_NETWORK"
        is_retryable = True
        urgency = "IMMEDIATE"
        desc = "Transient bank PSP network or gateway timeout. High probability of recovery via smart retry."
    elif any(kw in reason for kw in ["insufficient", "low_balance", "balance"]):
        category = "INSUFFICIENT_FUNDS"
        is_retryable = False
        urgency = "MEDIUM"
        desc = "Declined due to insufficient balance. Best addressed via alternate payment or customer reminder link."
    elif any(kw in reason for kw in ["expired", "card_blocked", "blocked", "invalid"]):
        category = "PAYMENT_METHOD_ISSUE"
        is_retryable = False
        urgency = "HIGH"
        desc = "Payment instrument blocked or expired. Customer must select an alternate payment method."
    elif any(kw in reason for kw in ["3ds", "otp", "auth", "authentication"]):
        category = "AUTHENTICATION_FAILURE"
        is_retryable = True
        urgency = "MEDIUM"
        desc = "Authentication session expired or dropped during 3DS OTP verification."
    elif any(kw in reason for kw in ["abandoned", "drop", "pending"]):
        category = "CUSTOMER_DROP_OFF"
        is_retryable = False
        urgency = "SCHEDULED"
        desc = "Checkout abandoned prior to authorization. Candidate for personalized payment reminder nudge."
    else:
        category = "UNKNOWN_FAILURE"
        is_retryable = False
        urgency = "MEDIUM"
        desc = f"Unclassified gateway decline: {failure_reason}."

    return {
        "category": category,
        "is_retryable": is_retryable,
        "urgency": urgency,
        "description": desc
    }

def analyze_transaction_context(transaction_dict: Dict[str, Any], customer_dict: Dict[str, Any] = None) -> Dict[str, Any]:
    """Combines transaction fields with customer historical behavior."""
    amount = float(transaction_dict.get("amount", 0.0))
    fraud_score = float(transaction_dict.get("fraud_score", transaction_dict.get("fraud_probability", 0.05)))
    attempt_number = int(transaction_dict.get("attempt_number", 1))
    failure_reason = str(transaction_dict.get("failure_reason", "unknown"))

    failure_info = classify_failure(failure_reason, fraud_score, attempt_number)

    # Customer Context Intelligence
    cust_data = customer_dict or transaction_dict.get("customer_history", {})
    successful_txs = int(cust_data.get("successful_transactions", 0))
    failed_txs = int(cust_data.get("failed_transactions", 0))
    total_spend = float(cust_data.get("total_spend", 0.0))
    
    # Calculate relationship strength
    if successful_txs >= 10 or total_spend >= 50000:
        relationship_score = "STRONG_VIP"
        friction_tolerance = "LOW"
    elif successful_txs >= 3:
        relationship_score = "GOOD_RETURNING"
        friction_tolerance = "MEDIUM"
    else:
        relationship_score = "NEW_CUSTOMER"
        friction_tolerance = "HIGH"

    return {
        "failure_analysis": failure_info,
        "customer_relationship": {
            "tier": transaction_dict.get("customer_value", "MEDIUM"),
            "relationship_score": relationship_score,
            "friction_tolerance": friction_tolerance,
            "successful_history": successful_txs,
            "failed_history": failed_txs,
            "historical_spend": total_spend
        },
        "financial_exposure": {
            "amount": amount,
            "is_high_value": amount > 50000.0,
            "fraud_risk_level": "CRITICAL" if fraud_score > 0.70 else "HIGH" if fraud_score > 0.40 else "LOW"
        }
    }
