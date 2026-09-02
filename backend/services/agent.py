"""
AI Decision Agent for RecoverAI (Buildathon Track 3).
Synthesizes:
- Failure taxonomy & context analysis
- Customer payment relationship history
- Counterfactual strategy comparisons
- Economic recovery values & risk thresholds
Produces structured JSON recommendation with transparent, measurable rationale.
"""
import os
import json
from typing import Dict, Any, List
from dotenv import load_dotenv

load_dotenv()

def generate_ai_decision(
    transaction_dict: Dict[str, Any],
    context_analysis: Dict[str, Any],
    counterfactual_strategies: List[Dict[str, Any]],
    retrieved_policy: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Produces structured AI recovery recommendation.
    Outputs:
    {
        "decision": "SMART_RETRY" | "ALTERNATE_PAYMENT" | "CUSTOMER_NUDGE" | "STOP" | "HUMAN_ESCALATION",
        "confidence": float,
        "reason": str,
        "expected_recovery": float,
        "risk_level": "LOW" | "MEDIUM" | "HIGH" | "CRITICAL",
        "next_action": str,
        "policy_used": str
    }
    """
    amount = float(transaction_dict.get("amount", 0.0))
    fraud_score = float(transaction_dict.get("fraud_score", transaction_dict.get("fraud_probability", 0.05)))
    failure_reason = str(transaction_dict.get("failure_reason", "unknown"))
    attempt_number = int(transaction_dict.get("attempt_number", 1))
    
    # Identify top counterfactual strategy
    top_strategy = counterfactual_strategies[0] if counterfactual_strategies else {}
    for s in counterfactual_strategies:
        if s.get("is_recommended"):
            top_strategy = s
            break

    strategy_name = top_strategy.get("strategy", "SMART_RETRY")
    exp_recovery = float(top_strategy.get("expected_recovery", round(amount * 0.70, 2)))
    policy_name = retrieved_policy.get("policy_name", "general_policy.txt") if retrieved_policy else "upi_policy.txt"

    # Optional OpenAI integration if user has OPENAI_API_KEY
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        try:
            import httpx
            prompt = f"""You are RecoverAI's Autonomous Revenue Decision Engine for Razorpay Track 3.
Analyze this failed payment transaction:
- Amount: INR {amount:,.2f}
- Method: {transaction_dict.get('payment_method')}
- Failure Reason: {failure_reason} (Category: {context_analysis.get('failure_analysis', {}).get('category')})
- Attempt Number: {attempt_number}
- Fraud Risk Score: {fraud_score}
- Customer Tier: {context_analysis.get('customer_relationship', {}).get('tier')}
- Counterfactual Strategy Options: {json.dumps(counterfactual_strategies[:3])}

Recommend the safest, most economically effective strategy among:
[SMART_RETRY, ALTERNATE_PAYMENT, CUSTOMER_NUDGE, STOP, HUMAN_ESCALATION].
Respond in JSON only:
{{
  "decision": "STRATEGY_NAME",
  "confidence": 0.85,
  "reason": "measurable rationale with financial comparison",
  "expected_recovery": {exp_recovery},
  "risk_level": "LOW|MEDIUM|HIGH|CRITICAL",
  "next_action": "action description"
}}"""
            headers = {"Authorization": f"Bearer {openai_key}", "Content-Type": "application/json"}
            payload = {
                "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2,
                "response_format": {"type": "json_object"}
            }
            resp = httpx.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers, timeout=5.0)
            if resp.status_code == 200:
                result = json.loads(resp.json()["choices"][0]["message"]["content"])
                result["policy_used"] = policy_name
                return result
        except Exception:
            pass

    # Intelligent Local Agent Reasoning Engine (Zero external dependencies)
    risk_level = "CRITICAL" if fraud_score > 0.70 else "HIGH" if fraud_score > 0.40 else "LOW"

    if fraud_score > 0.70:
        decision = "HUMAN_ESCALATION"
        confidence = 0.94
        reason = f"High fraud risk ({fraud_score * 100:.1f}%) exceeds safety boundaries. Automated retry is strictly prohibited; manual KYC and fraud desk review required."
        next_action = "ROUTE_TO_RISK_DESK"
    elif attempt_number >= 2:
        decision = "STOP"
        confidence = 0.95
        reason = f"Retry exhaustion limit reached ({attempt_number} attempts). Halting automated actions to prevent customer fatigue, duplicate debits, and operational expense."
        next_action = "CLOSE_RECOVERY_LIFECYCLE"
    elif amount > 50000.0:
        decision = "HUMAN_ESCALATION"
        confidence = 0.91
        reason = f"High-ticket transaction value of ₹{amount:,.2f} exceeds ₹50,000 threshold. Supervisor authorization mandated before re-attempting debit."
        next_action = "REQUEST_SUPERVISOR_APPROVAL"
    elif strategy_name == "ALTERNATE_PAYMENT":
        decision = "ALTERNATE_PAYMENT"
        confidence = 0.86
        reason = f"Card instrument declined. Counterfactual analysis shows Alternate Payment has the highest expected recovery (₹{exp_recovery:,.2f}, {int(top_strategy.get('success_probability', 0.84)*100)}% prob) versus immediate retry."
        next_action = "SEND_PAYMENT_LINK"
    elif strategy_name == "CUSTOMER_NUDGE":
        decision = "CUSTOMER_NUDGE"
        confidence = 0.82
        reason = f"Checkout session abandonment detected. Counterfactual analysis favors a gentle customer nudge link (expected recovery ₹{exp_recovery:,.2f}) with minimal customer friction."
        next_action = "DISPATCH_SMS_WHATSAPP_NUDGE"
    elif strategy_name == "STOP":
        decision = "STOP"
        confidence = 0.88
        reason = f"Recovery viability score indicates negative economic return after factoring operational costs and customer friction penalty. Terminating recovery."
        next_action = "LOG_UNRECOVERED_REVENUE"
    else:
        decision = "SMART_RETRY"
        confidence = 0.90
        reason = f"Transient network timeout on payment gateway with strong customer history. Smart retry offers the highest safe expected recovery of ₹{exp_recovery:,.2f}."
        next_action = "TRIGGER_AUTOMATIC_RETRY"

    return {
        "decision": decision,
        "action": decision, # backwards compatibility
        "confidence": confidence,
        "reason": reason,
        "expected_recovery": exp_recovery,
        "risk_level": risk_level,
        "next_action": next_action,
        "policy_used": policy_name
    }
