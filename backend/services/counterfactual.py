"""
Counterfactual Strategy Evaluator for RecoverAI (Key Buildathon Differentiator).
Evaluates all 5 recovery strategies simultaneously:
- SMART_RETRY
- ALTERNATE_PAYMENT
- CUSTOMER_NUDGE
- STOP
- HUMAN_ESCALATION

Formula:
Recovery Score = Expected Recovery Value - Recovery Cost - Risk Penalty - Friction Penalty
where Expected Recovery Value = Transaction Amount * Success Probability
"""
from typing import Dict, Any, List

def evaluate_all_strategies(
    amount: float,
    payment_method: str,
    failure_reason: str,
    failure_category: str,
    attempt_number: int,
    fraud_score: float,
    customer_history: Dict[str, Any] = None
) -> List[Dict[str, Any]]:
    """
    Computes side-by-side counterfactual metrics across all 5 strategies.
    Returns sorted list of strategy options, identifying the highest safe expected value option.
    """
    history = customer_history or {}
    succ_txs = history.get("successful_transactions", 3)
    cust_loyalty_boost = min(0.12, succ_txs * 0.01)

    strategies = []

    # ----------------------------------------------------
    # STRATEGY 1: SMART_RETRY
    # ----------------------------------------------------
    # Best for transient network timeouts on UPI or Card (attempt < 2)
    if fraud_score > 0.70 or attempt_number >= 2:
        retry_prob = 0.05
    elif failure_category == "TEMPORARY_NETWORK":
        retry_prob = min(0.95, 0.78 + cust_loyalty_boost)
    elif failure_category == "AUTHENTICATION_FAILURE":
        retry_prob = 0.55
    elif failure_category == "INSUFFICIENT_FUNDS":
        retry_prob = 0.20
    else:
        retry_prob = 0.25

    retry_cost = 5.00  # Gateway transaction fee / API cost
    retry_risk_penalty = round(amount * (fraud_score * 0.5), 2)
    retry_friction_penalty = 10.00 if attempt_number == 1 else 150.00  # Customer annoyance on repeated debits
    expected_retry = round(amount * retry_prob, 2)
    retry_score = round(expected_retry - retry_cost - retry_risk_penalty - retry_friction_penalty, 2)

    strategies.append({
        "strategy": "SMART_RETRY",
        "title": "Smart Retry",
        "success_probability": round(retry_prob, 2),
        "expected_recovery": expected_retry,
        "recovery_cost": retry_cost,
        "risk_penalty": retry_risk_penalty,
        "friction_penalty": retry_friction_penalty,
        "recovery_score": retry_score,
        "rationale": "Automated immediate or short-delay retry across payment network."
    })

    # ----------------------------------------------------
    # STRATEGY 2: ALTERNATE_PAYMENT
    # ----------------------------------------------------
    # Best for card declines, blocked instruments, or repeated timeouts
    if fraud_score > 0.70:
        alt_prob = 0.08
    elif failure_category in ["PAYMENT_METHOD_ISSUE", "INSUFFICIENT_FUNDS"]:
        alt_prob = min(0.92, 0.80 + cust_loyalty_boost)
    elif failure_category == "TEMPORARY_NETWORK" and attempt_number > 1:
        alt_prob = 0.75
    else:
        alt_prob = 0.65

    alt_cost = 12.00  # Dynamic checkout link routing cost
    alt_risk_penalty = round(amount * (fraud_score * 0.25), 2)  # Lower risk as payer must re-authenticate on new method
    alt_friction_penalty = 25.00  # Payer must choose another instrument
    expected_alt = round(amount * alt_prob, 2)
    alt_score = round(expected_alt - alt_cost - alt_risk_penalty - alt_friction_penalty, 2)

    strategies.append({
        "strategy": "ALTERNATE_PAYMENT",
        "title": "Alternate Payment Method",
        "success_probability": round(alt_prob, 2),
        "expected_recovery": expected_alt,
        "recovery_cost": alt_cost,
        "risk_penalty": alt_risk_penalty,
        "friction_penalty": alt_friction_penalty,
        "recovery_score": alt_score,
        "rationale": "Prompt payer to complete transaction using UPI QR, Netbanking, or alternate card."
    })

    # ----------------------------------------------------
    # STRATEGY 3: CUSTOMER_NUDGE
    # ----------------------------------------------------
    # Best for checkout abandonment, dropped carts, or pending authorizations
    if fraud_score > 0.70:
        nudge_prob = 0.05
    elif failure_category == "CUSTOMER_DROP_OFF":
        nudge_prob = min(0.85, 0.68 + cust_loyalty_boost)
    elif failure_category == "INSUFFICIENT_FUNDS":
        nudge_prob = 0.60
    else:
        nudge_prob = 0.45

    nudge_cost = 2.50  # SMS / WhatsApp notification cost
    nudge_risk_penalty = round(amount * (fraud_score * 0.15), 2)
    nudge_friction_penalty = 15.00  # Light notification friction
    expected_nudge = round(amount * nudge_prob, 2)
    nudge_score = round(expected_nudge - nudge_cost - nudge_risk_penalty - nudge_friction_penalty, 2)

    strategies.append({
        "strategy": "CUSTOMER_NUDGE",
        "title": "Customer Nudge",
        "success_probability": round(nudge_prob, 2),
        "expected_recovery": expected_nudge,
        "recovery_cost": nudge_cost,
        "risk_penalty": nudge_risk_penalty,
        "friction_penalty": nudge_friction_penalty,
        "recovery_score": nudge_score,
        "rationale": "Personalized WhatsApp/SMS recovery link with pre-filled cart details."
    })

    # ----------------------------------------------------
    # STRATEGY 4: STOP
    # ----------------------------------------------------
    # Best when recovery is economically unviable, retry limit reached, or low probability
    stop_score = 0.00  # Safe zero-cost preservation
    strategies.append({
        "strategy": "STOP",
        "title": "Stop Recovery",
        "success_probability": 0.00,
        "expected_recovery": 0.00,
        "recovery_cost": 0.00,
        "risk_penalty": 0.00,
        "friction_penalty": 0.00,
        "recovery_score": stop_score,
        "rationale": "Terminate recovery outreach to eliminate operational cost and prevent customer churn."
    })

    # ----------------------------------------------------
    # STRATEGY 5: HUMAN_ESCALATION
    # ----------------------------------------------------
    # Best for high-value transactions (> ₹50k) or suspicious fraud indicators (> 0.70)
    if fraud_score > 0.70 or amount > 50000:
        escalate_prob = 0.75  # Human risk analyst resolution rate
        escalate_score = round((amount * escalate_prob) - 150.00, 2)
    else:
        escalate_prob = 0.30
        escalate_score = round((amount * escalate_prob) - 300.00, 2)

    escalate_cost = 150.00  # Human analyst review time allocation
    escalate_risk_penalty = 0.00  # Mitigated through manual KYC/verification
    escalate_friction_penalty = 50.00
    expected_escalate = round(amount * escalate_prob, 2)

    strategies.append({
        "strategy": "HUMAN_ESCALATION",
        "title": "Human Escalation",
        "success_probability": round(escalate_prob, 2),
        "expected_recovery": expected_escalate,
        "recovery_cost": escalate_cost,
        "risk_penalty": escalate_risk_penalty,
        "friction_penalty": escalate_friction_penalty,
        "recovery_score": escalate_score,
        "rationale": "Route to fraud operations or white-glove support desk for manual verification."
    })

    # Determine optimal recommendation
    # Priority: Safety constraints take precedence
    if fraud_score > 0.70:
        recommended = "HUMAN_ESCALATION"
    elif attempt_number >= 2:
        recommended = "STOP"
    elif amount > 50000.0:
        recommended = "HUMAN_ESCALATION"
    else:
        # Pick strategy with highest recovery_score among non-STOP options
        eligible = [s for s in strategies if s["strategy"] not in ["HUMAN_ESCALATION"]]
        top_opt = max(eligible, key=lambda s: s["recovery_score"])
        # If even top option has negative recovery score or very low probability (< 0.25), choose STOP
        if top_opt["recovery_score"] <= 0 or top_opt["success_probability"] < 0.25:
            recommended = "STOP"
        else:
            recommended = top_opt["strategy"]

    for s in strategies:
        s["is_recommended"] = (s["strategy"] == recommended)

    return sorted(strategies, key=lambda s: s["recovery_score"], reverse=True)
