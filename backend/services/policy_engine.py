"""
Deterministic Safety & Policy Engine for RecoverAI (Buildathon Track 3).
Operates as the independent safety gatekeeper between AI recommendation and action execution.
Guarantees: POLICY ALWAYS WINS OVER AI.
"""
from typing import Dict, Any, List

class PolicyEvaluationResult:
    def __init__(
        self,
        allowed: bool,
        enforced_action: str,
        policy_result: str,
        policy_reason: str,
        rules_triggered: List[str],
        ai_overridden: bool = False
    ):
        self.allowed = allowed
        self.enforced_action = enforced_action
        self.policy_result = policy_result
        self.policy_reason = policy_reason
        self.rules_triggered = rules_triggered
        self.ai_overridden = ai_overridden

    def to_dict(self) -> Dict[str, Any]:
        return {
            "allowed": self.allowed,
            "enforced_action": self.enforced_action,
            "policy_result": self.policy_result,
            "policy_reason": self.policy_reason,
            "rules_triggered": ", ".join(self.rules_triggered),
            "ai_overridden": self.ai_overridden
        }

def evaluate_policy_safety(
    ai_recommendation: str,
    amount: float,
    fraud_score: float,
    attempt_number: int,
    recovery_probability: float,
    transaction_status: str,
    failure_reason: str
) -> PolicyEvaluationResult:
    """
    Evaluates universal safety policies in deterministic priority order.
    Returns whether the AI recommendation is approved, overridden, or blocked.
    """
    ai_act = (ai_recommendation or "").upper().strip()
    status_upper = (transaction_status or "").upper().strip()
    rules = []

    # Priority 1: Already Successful / Debited transaction -> HARD STOP
    if status_upper == "RECOVERED" or status_upper == "SUCCESS":
        rules.append("DUPLICATE_DEBIT_PREVENTION")
        return PolicyEvaluationResult(
            allowed=False,
            enforced_action="STOP",
            policy_result="STOPPED",
            policy_reason="Transaction has already been successfully recovered/debited. Automatic recovery permanently halted.",
            rules_triggered=rules,
            ai_overridden=(ai_act != "STOP")
        )

    # Priority 2: Fraud Risk Threshold > 70% -> HARD STOP / ESCALATE
    if fraud_score > 0.70:
        rules.append("HIGH_FRAUD_RISK_HARD_STOP")
        # Under no circumstance is automated retry allowed on fraud > 70%
        overridden = (ai_act not in ["HUMAN_ESCALATION", "ESCALATE", "STOP"])
        return PolicyEvaluationResult(
            allowed=False,
            enforced_action="HUMAN_ESCALATION",
            policy_result="BLOCKED",
            policy_reason=f"Fraud probability ({fraud_score * 100:.1f}%) exceeds safety threshold of 70%. Automated recovery strictly BLOCKED. Escalated to risk operations.",
            rules_triggered=rules,
            ai_overridden=overridden
        )

    # Priority 3: Retry Limit Exhaustion >= 2 -> STOP
    if attempt_number >= 2:
        rules.append("RETRY_LIMIT_EXHAUSTION_STOP")
        overridden = (ai_act != "STOP")
        return PolicyEvaluationResult(
            allowed=False,
            enforced_action="STOP",
            policy_result="STOPPED",
            policy_reason=f"Attempt limit reached ({attempt_number} attempts). Automatic recovery must STOP to protect customer trust and prevent duplicate charges.",
            rules_triggered=rules,
            ai_overridden=overridden
        )

    # Priority 4: High Value Controls > ₹50,000 -> ESCALATE
    if amount > 50000.0:
        rules.append("HIGH_VALUE_THRESHOLD_ESCALATE")
        overridden = (ai_act not in ["HUMAN_ESCALATION", "ESCALATE"])
        return PolicyEvaluationResult(
            allowed=False,
            enforced_action="HUMAN_ESCALATION",
            policy_result="ESCALATED",
            policy_reason=f"Transaction value (₹{amount:,.2f}) exceeds ₹50,000 threshold. Automated action halted. Requires supervisor clearance.",
            rules_triggered=rules,
            ai_overridden=overridden
        )

    # Priority 5: Economically Unviable / Low Recovery Probability < 30% -> STOP
    if recovery_probability < 0.30:
        rules.append("LOW_VIABILITY_PRESERVATION_STOP")
        overridden = (ai_act != "STOP")
        return PolicyEvaluationResult(
            allowed=False,
            enforced_action="STOP",
            policy_result="STOPPED",
            policy_reason=f"Estimated recovery probability ({recovery_probability * 100:.1f}%) falls below viable threshold (30%). Preserving customer relationship from futile outreach.",
            rules_triggered=rules,
            ai_overridden=overridden
        )

    # Priority 6: Valid Action Approval
    # If AI recommended an permitted action within safe bounds:
    rules.append("SAFETY_BOUNDS_SATISFIED")
    valid_actions = ["SMART_RETRY", "RETRY", "ALTERNATE_PAYMENT", "CUSTOMER_NUDGE", "SEND_REMINDER", "STOP", "HUMAN_ESCALATION", "ESCALATE"]
    
    if ai_act in valid_actions:
        return PolicyEvaluationResult(
            allowed=True,
            enforced_action=ai_act,
            policy_result="APPROVED",
            policy_reason=f"AI recommendation '{ai_act}' complies with all safety policies, fraud thresholds, and attempt limits.",
            rules_triggered=rules,
            ai_overridden=False
        )

    # Fallback if unknown action
    rules.append("UNRECOGNIZED_ACTION_FALLBACK")
    return PolicyEvaluationResult(
        allowed=False,
        enforced_action="STOP",
        policy_result="OVERRIDDEN",
        policy_reason=f"Unrecognized AI recommendation '{ai_act}'. Safety policy defaulted to STOP.",
        rules_triggered=rules,
        ai_overridden=True
    )
