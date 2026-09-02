"""
Deterministic Guardrails for RecoverAI.
Enforces safety rules that strictly override any automated or AI recommendations.
"""
from typing import Dict, Any, Optional

class GuardrailResult:
    def __init__(self, action: str, passed: bool, reason: str, rule_name: str, overridden: bool = False):
        self.action = action
        self.passed = passed
        self.reason = reason
        self.rule_name = rule_name
        self.overridden = overridden

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action,
            "passed": self.passed,
            "reason": self.reason,
            "rule_name": self.rule_name,
            "overridden": self.overridden
        }

def evaluate_guardrails(
    fraud_probability: float,
    attempt_number: int,
    amount: float,
    recovery_probability: float,
    failure_reason: str,
    ai_recommendation: Optional[str] = None
) -> GuardrailResult:
    """
    Evaluates deterministic safety rules in priority order:
    1. IF fraud_probability > 0.70 -> ESCALATE
    2. IF attempt_number >= 2 -> STOP
    3. IF amount > 50000 -> ESCALATE
    4. IF recovery_probability < 0.30 -> STOP
    5. IF failure_reason == "timeout" -> RETRY
    6. IF failure_reason == "card_declined" -> ALTERNATE_PAYMENT
    7. Otherwise -> SEND_REMINDER
    """
    reason_norm = (failure_reason or "").strip().lower()
    
    # Rule 1: High fraud risk threshold
    if fraud_probability > 0.70:
        target_action = "ESCALATE"
        rule = "HIGH_FRAUD_RISK_ESCALATION"
        msg = f"Fraud probability ({fraud_probability:.2f}) exceeds safety threshold of 0.70. Escalate for human review."
    
    # Rule 2: Max attempt limit
    elif attempt_number >= 2:
        target_action = "STOP"
        rule = "MAX_ATTEMPT_LIMIT_STOP"
        msg = "Retry limit reached. Automatic recovery must stop."
    
    # Rule 3: High transaction amount threshold
    elif amount > 50000.0:
        target_action = "ESCALATE"
        rule = "HIGH_VALUE_TRANSACTION_ESCALATION"
        msg = f"Transaction amount (₹{amount:,.2f}) exceeds ₹50,000 threshold. Escalate for manual verification."
    
    # Rule 4: Low recovery probability threshold
    elif recovery_probability < 0.30:
        target_action = "STOP"
        rule = "LOW_RECOVERY_PROBABILITY_STOP"
        msg = f"Estimated recovery probability ({recovery_probability:.2f}) is below viability threshold of 0.30. Stopping outreach."
    
    # Rule 5: Timeout failure
    elif reason_norm in ["timeout", "upi_timeout", "gateway_timeout"]:
        target_action = "RETRY"
        rule = "TIMEOUT_FAILURE_RETRY"
        msg = "Transaction failed due to network timeout. Eligible for automatic retry."
    
    # Rule 6: Card decline
    elif reason_norm in ["card_declined", "card_decline", "issuer_declined"]:
        target_action = "ALTERNATE_PAYMENT"
        rule = "CARD_DECLINE_ALTERNATE_PAYMENT"
        msg = "Card declined by issuing bank. Recommend customer switch to alternate payment method (UPI / Netbanking)."
    
    # Rule 7: Fallback / Abandonment / Other
    else:
        target_action = "SEND_REMINDER"
        rule = "DEFAULT_RECOVERY_SEND_REMINDER"
        msg = f"Transaction failure '{failure_reason}' eligible for automated recovery reminder notification."

    # Compare with AI recommendation if provided
    overridden = False
    passed = True
    if ai_recommendation:
        ai_norm = ai_recommendation.strip().upper()
        if ai_norm != target_action:
            overridden = True
            passed = False
            msg = f"Guardrail override: AI recommended '{ai_norm}', but safety policy '{rule}' strictly mandates '{target_action}'. Reason: {msg}"

    return GuardrailResult(
        action=target_action,
        passed=passed,
        reason=msg,
        rule_name=rule,
        overridden=overridden
    )
