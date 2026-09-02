"""
Transactions and Recovery Router for RecoverAI.
Handles listing transactions, retrieving individual transaction details,
triggering mock recovery execution, and inspecting audit trails.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any

from database import get_db, Transaction, AuditLog
from services.recovery import process_recovery_execution, analyze_transaction_lifecycle

router = APIRouter(tags=["Transactions"])

@router.get("/transactions")
def list_transactions(
    status: Optional[str] = Query(None, description="Filter by status: AT_RISK, RECOVERED, FAILED, ESCALATED, STOPPED"),
    payment_method: Optional[str] = Query(None, description="Filter by method: upi, card, netbanking, wallet"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Retrieve transactions with optional filtering and pagination."""
    query = db.query(Transaction)
    if status:
        query = query.filter(Transaction.status == status.upper())
    if payment_method:
        query = query.filter(Transaction.payment_method == payment_method.lower())

    total = query.count()
    items = query.order_by(Transaction.created_at.desc()).offset(offset).limit(limit).all()

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "transactions": [item.to_dict() for item in items]
    }

@router.get("/transactions/{transaction_id}")
def get_transaction_detail(
    transaction_id: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Retrieve transaction details along with pre-computed recovery preview."""
    tx = db.query(Transaction).filter(Transaction.transaction_id == transaction_id).first()
    if not tx:
        raise HTTPException(status_code=404, detail=f"Transaction '{transaction_id}' not found.")

    analysis = analyze_transaction_lifecycle(tx, db)
    audits = db.query(AuditLog).filter(AuditLog.transaction_id == transaction_id).order_by(AuditLog.id.asc()).all()

    return {
        "transaction": tx.to_dict(),
        "preview_analysis": analysis,
        "audit_logs": [a.to_dict() for a in audits]
    }

@router.post("/transactions/{transaction_id}/recover")
def execute_recovery_endpoint(
    transaction_id: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Executes mock recovery workflow for the transaction:
    Runs risk evaluation -> RAG policy -> AI agent -> Guardrails -> Mock execution -> Audit logs.
    """
    try:
        result = process_recovery_execution(transaction_id, db)
        return result
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recovery execution failed: {str(e)}")

@router.get("/transactions/{transaction_id}/audit")
def get_transaction_audit_trail(
    transaction_id: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Returns chronological audit trail for a transaction."""
    tx = db.query(Transaction).filter(Transaction.transaction_id == transaction_id).first()
    if not tx:
        raise HTTPException(status_code=404, detail=f"Transaction '{transaction_id}' not found.")

    logs = db.query(AuditLog).filter(AuditLog.transaction_id == transaction_id).order_by(AuditLog.id.asc()).all()
    return {
        "transaction_id": transaction_id,
        "total_events": len(logs),
        "audit_trail": [log.to_dict() for log in logs]
    }

@router.get("/audit")
def list_global_audit_logs(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    transaction_id: Optional[str] = Query(None),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Returns global audit trail across all transactions."""
    query = db.query(AuditLog)
    if transaction_id:
        query = query.filter(AuditLog.transaction_id.ilike(f"%{transaction_id}%"))
    total = query.count()
    logs = query.order_by(AuditLog.id.desc()).offset(offset).limit(limit).all()
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "audit_logs": [log.to_dict() for log in logs]
    }
