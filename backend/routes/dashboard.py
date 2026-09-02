"""
Dashboard Router for RecoverAI.
Calculates high-level revenue recovery metrics, action distributions, and status summaries.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any

from database import get_db, Transaction

router = APIRouter(tags=["Dashboard"])

@router.get("/dashboard")
def get_dashboard_metrics(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Returns high-level business intelligence metrics:
    - total_transactions
    - revenue_at_risk (amount of transactions currently in AT_RISK or FAILED status)
    - revenue_recovered (total amount successfully collected)
    - recovery_rate (percentage of recovered revenue vs total transaction volume)
    - action_counts (distribution across RETRY, ALTERNATE_PAYMENT, SEND_REMINDER, ESCALATE, STOP)
    - status_counts (distribution across AT_RISK, RECOVERED, FAILED, ESCALATED, STOPPED)
    """
    total_tx = db.query(Transaction).count()
    
    # Revenue calculations
    revenue_at_risk_val = db.query(func.sum(Transaction.amount))\
        .filter(Transaction.status.in_(["AT_RISK", "FAILED"]))\
        .scalar() or 0.0

    revenue_recovered_val = db.query(func.sum(Transaction.recovered_amount))\
        .scalar() or 0.0

    total_volume = db.query(func.sum(Transaction.amount)).scalar() or 0.0

    recovery_rate = round((revenue_recovered_val / total_volume * 100), 2) if total_volume > 0 else 0.0

    # Action counts
    action_rows = db.query(Transaction.recovery_action, func.count(Transaction.transaction_id))\
        .group_by(Transaction.recovery_action).all()
    action_counts = {action or "NONE": count for action, count in action_rows}

    # Ensure all primary actions exist in dictionary
    for act in ["RETRY", "ALTERNATE_PAYMENT", "SEND_REMINDER", "ESCALATE", "STOP"]:
        action_counts.setdefault(act, 0)

    # Status counts
    status_rows = db.query(Transaction.status, func.count(Transaction.transaction_id))\
        .group_by(Transaction.status).all()
    status_counts = {st or "UNKNOWN": count for st, count in status_rows}
    for st in ["AT_RISK", "RECOVERED", "FAILED", "ESCALATED", "STOPPED"]:
        status_counts.setdefault(st, 0)

    return {
        "total_transactions": total_tx,
        "revenue_at_risk": round(float(revenue_at_risk_val), 2),
        "revenue_recovered": round(float(revenue_recovered_val), 2),
        "recovery_rate": recovery_rate,
        "action_counts": action_counts,
        "status_counts": status_counts
    }
