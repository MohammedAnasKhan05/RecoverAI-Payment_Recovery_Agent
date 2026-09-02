"""
Production REST API Router for RecoverAI (Buildathon Track 3).
Provides all /api/* endpoints specified in the architectural blueprint.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any, List, Optional

from database import (
    get_db, Transaction, Customer, RiskScore, RecoveryStrategy,
    RecoveryDecision, PolicyDecision, RecoveryAttempt, RecoveryOutcome, AuditLog
)
from services.recovery import analyze_transaction_full, execute_recovery_pipeline
from services.context_analyzer import analyze_transaction_context
from services.counterfactual import evaluate_all_strategies
from services.agent import generate_ai_decision
from services.policy_engine import evaluate_policy_safety
from services.feedback import get_strategy_performance
from services.rag import evaluate_rag_system

router = APIRouter(prefix="/api", tags=["Buildathon API"])

# ----------------------------------------------------
# 1. TRANSACTIONS
# ----------------------------------------------------
@router.get("/transactions")
def list_transactions(
    status: Optional[str] = Query(None),
    payment_method: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    query = db.query(Transaction)
    if status and status.upper() != "ALL":
        query = query.filter(Transaction.status == status.upper())
    if payment_method:
        query = query.filter(Transaction.payment_method == payment_method.lower())

    total = query.count()
    items = query.order_by(Transaction.created_at.desc()).offset(offset).limit(limit).all()

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "transactions": [t.to_dict() for t in items]
    }

@router.get("/transactions/{id}")
def get_transaction(
    id: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    tx = db.query(Transaction).filter(
        (Transaction.id == id) | (Transaction.transaction_reference == id)
    ).first()

    if not tx:
        raise HTTPException(status_code=404, detail=f"Transaction '{id}' not found.")

    analysis = analyze_transaction_full(tx, db)
    audits = db.query(AuditLog).filter(AuditLog.transaction_id == tx.id).order_by(AuditLog.id.asc()).all()

    return {
        "transaction": tx.to_dict(),
        "preview_analysis": analysis,
        "counterfactual_strategies": analysis["counterfactual_strategies"],
        "ai_decision": analysis["ai_decision"],
        "policy_decision": analysis["policy_decision"],
        "audit_logs": [a.to_dict() for a in audits]
    }

# ----------------------------------------------------
# 2. RISK ANALYSIS
# ----------------------------------------------------
@router.post("/risk/analyze")
def analyze_risk(
    payload: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    tx_id = payload.get("transaction_id")
    if tx_id:
        tx = db.query(Transaction).filter((Transaction.id == tx_id) | (Transaction.transaction_reference == tx_id)).first()
        if tx:
            return analyze_transaction_full(tx, db)

    # Ad-hoc analysis from payload
    context = analyze_transaction_context(payload)
    return {
        "context_intelligence": context,
        "fraud_score": payload.get("fraud_score", 0.05),
        "recovery_probability": payload.get("recovery_probability", 0.70)
    }

# ----------------------------------------------------
# 3. COUNTERFACTUAL EVALUATION
# ----------------------------------------------------
@router.post("/recovery/evaluate")
def evaluate_recovery(
    payload: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    amount = float(payload.get("amount", 5000.0))
    method = payload.get("payment_method", "upi")
    reason = payload.get("failure_reason", "timeout")
    category = payload.get("failure_category", "TEMPORARY_NETWORK")
    attempt = int(payload.get("attempt_number", 1))
    fraud = float(payload.get("fraud_score", 0.05))

    strategies = evaluate_all_strategies(
        amount=amount,
        payment_method=method,
        failure_reason=reason,
        failure_category=category,
        attempt_number=attempt,
        fraud_score=fraud
    )
    return {
        "transaction_amount": amount,
        "counterfactual_strategies": strategies
    }

# ----------------------------------------------------
# 4. RECOVERY DECISION (AI AGENT)
# ----------------------------------------------------
@router.post("/recovery/decide")
def decide_recovery(
    payload: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    context = analyze_transaction_context(payload)
    strategies = evaluate_all_strategies(
        amount=float(payload.get("amount", 5000.0)),
        payment_method=payload.get("payment_method", "upi"),
        failure_reason=payload.get("failure_reason", "timeout"),
        failure_category=context["failure_analysis"]["category"],
        attempt_number=int(payload.get("attempt_number", 1)),
        fraud_score=float(payload.get("fraud_score", 0.05))
    )
    ai_dec = generate_ai_decision(payload, context, strategies)
    return ai_dec

# ----------------------------------------------------
# 5. DETERMINISTIC POLICY CHECK
# ----------------------------------------------------
@router.post("/policy/check")
def check_policy(
    payload: Dict[str, Any] = Body(...)
) -> Dict[str, Any]:
    res = evaluate_policy_safety(
        ai_recommendation=payload.get("ai_recommendation", "SMART_RETRY"),
        amount=float(payload.get("amount", 5000.0)),
        fraud_score=float(payload.get("fraud_score", 0.05)),
        attempt_number=int(payload.get("attempt_number", 1)),
        recovery_probability=float(payload.get("recovery_probability", 0.70)),
        transaction_status=payload.get("status", "FAILED"),
        failure_reason=payload.get("failure_reason", "timeout")
    )
    return res.to_dict()

# ----------------------------------------------------
# 6. RECOVERY EXECUTION
# ----------------------------------------------------
@router.post("/recovery/execute")
def execute_recovery(
    payload: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    tx_id = payload.get("transaction_id") or payload.get("id")
    if not tx_id:
        raise HTTPException(status_code=400, detail="transaction_id is required.")

    try:
        result = execute_recovery_pipeline(tx_id, db)
        return result
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ----------------------------------------------------
# 7. DASHBOARD METRICS (WITH REVENUE AT RISK BREAKDOWN)
# ----------------------------------------------------
@router.get("/dashboard/metrics")
def get_dashboard_metrics(db: Session = Depends(get_db)) -> Dict[str, Any]:
    total_tx = db.query(Transaction).count()

    # Revenue Totals
    rev_at_risk_total = db.query(func.sum(Transaction.amount))\
        .filter(Transaction.status.in_(["AT_RISK", "FAILED"])).scalar() or 0.0

    rev_recovered = db.query(func.sum(Transaction.amount_recovered)).scalar() or 0.0
    total_volume = db.query(func.sum(Transaction.amount)).scalar() or 0.0
    recovery_rate = round((rev_recovered / total_volume * 100), 1) if total_volume > 0 else 0.0

    # Detailed Revenue at Risk Category Breakdown (Section 4 of prompt)
    # 1. Recoverable (AT_RISK with timeout/temporary and low fraud)
    recoverable_rev = db.query(func.sum(Transaction.amount)).filter(
        Transaction.status == "AT_RISK",
        Transaction.failure_category == "TEMPORARY_NETWORK",
        Transaction.fraud_score <= 0.70,
        Transaction.attempt_number < 2
    ).scalar() or 0.0

    # 2. Alternate Method Recommended
    alternate_rev = db.query(func.sum(Transaction.amount)).filter(
        Transaction.status == "AT_RISK",
        Transaction.failure_category.in_(["PAYMENT_METHOD_ISSUE", "INSUFFICIENT_FUNDS"]),
        Transaction.fraud_score <= 0.70
    ).scalar() or 0.0

    # 3. High Risk
    high_risk_rev = db.query(func.sum(Transaction.amount)).filter(
        Transaction.status == "AT_RISK",
        Transaction.fraud_score > 0.70
    ).scalar() or 0.0

    # 4. Unrecoverable (attempt >= 2 or stopped)
    unrecoverable_rev = db.query(func.sum(Transaction.amount)).filter(
        (Transaction.attempt_number >= 2) | (Transaction.status == "STOPPED")
    ).scalar() or 0.0

    # Fallback padding if sums don't cover total
    remaining = max(0.0, rev_at_risk_total - (recoverable_rev + alternate_rev + high_risk_rev))
    recoverable_rev += remaining * 0.6
    alternate_rev += remaining * 0.4

    # Agent Metrics
    actions_count = {
        "smart_retries": db.query(Transaction).filter(Transaction.recommended_strategy == "SMART_RETRY").count(),
        "alternate_payments": db.query(Transaction).filter(Transaction.recommended_strategy == "ALTERNATE_PAYMENT").count(),
        "customer_nudges": db.query(Transaction).filter(Transaction.recommended_strategy == "CUSTOMER_NUDGE").count(),
        "stopped_transactions": db.query(Transaction).filter(Transaction.status == "STOPPED").count(),
        "human_escalations": db.query(Transaction).filter(Transaction.status == "ESCALATED").count(),
    }

    # Risk Metrics
    risk_metrics = {
        "high_risk_transactions": db.query(Transaction).filter(Transaction.fraud_score > 0.70).count(),
        "fraud_stops_prevented": db.query(Transaction).filter(Transaction.fraud_score > 0.70, Transaction.status == "ESCALATED").count(),
        "retry_limits_enforced": db.query(Transaction).filter(Transaction.attempt_number >= 2).count(),
        "policy_violations_blocked": db.query(PolicyDecision).filter(PolicyDecision.policy_result.in_(["BLOCKED", "OVERRIDDEN"])).count(),
    }

    # Recovery Strategy Performance (Learning Loop)
    strategy_perf = get_strategy_performance(db)

    return {
        "revenue_metrics": {
            "total_revenue_at_risk": round(float(rev_at_risk_total), 2),
            "expected_recoverable_revenue": round(float(recoverable_rev + alternate_rev * 0.85), 2),
            "revenue_recovered": round(float(rev_recovered), 2),
            "recovery_rate": recovery_rate,
            "revenue_lost": round(float(unrecoverable_rev), 2),
            "recovery_cost": round(float(actions_count["smart_retries"] * 5 + actions_count["alternate_payments"] * 12 + actions_count["customer_nudges"] * 2.5), 2),
            "breakdown": {
                "recoverable": round(float(recoverable_rev), 2),
                "alternate_method_recommended": round(float(alternate_rev), 2),
                "high_risk": round(float(high_risk_rev), 2),
                "unrecoverable": round(float(unrecoverable_rev), 2)
            }
        },
        "agent_metrics": actions_count,
        "risk_metrics": risk_metrics,
        "strategy_performance": strategy_perf,
        "total_transactions": total_tx,
        # Legacy compatibility keys for existing views
        "revenue_at_risk": round(float(rev_at_risk_total), 2),
        "revenue_recovered": round(float(rev_recovered), 2),
        "action_counts": {
            "RETRY": actions_count["smart_retries"],
            "ALTERNATE_PAYMENT": actions_count["alternate_payments"],
            "SEND_REMINDER": actions_count["customer_nudges"],
            "ESCALATE": actions_count["human_escalations"],
            "STOP": actions_count["stopped_transactions"]
        }
    }

# ----------------------------------------------------
# 8. AUDIT LEDGER
# ----------------------------------------------------
@router.get("/audit")
def get_global_audit(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    transaction_id: Optional[str] = Query(None),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    query = db.query(AuditLog)
    if transaction_id:
        query = query.join(Transaction).filter(
            (Transaction.transaction_reference.ilike(f"%{transaction_id}%")) | (AuditLog.transaction_id.ilike(f"%{transaction_id}%"))
        )
    total = query.count()
    logs = query.order_by(AuditLog.id.desc()).offset(offset).limit(limit).all()

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "audit_logs": [log.to_dict() for log in logs]
    }
