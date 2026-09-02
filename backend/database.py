"""
Production-style Database Layer for RecoverAI (Buildathon Track 3).
Supports Supabase PostgreSQL (via DATABASE_URL or SUPABASE_DB_URL) with SQLite local fallback.
Implements the full 9-table schema required by the architecture specification.
"""
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Generator, Dict, Any, List
from dotenv import load_dotenv
from sqlalchemy import (
    create_engine, Column, Integer, Float, String, DateTime, Text, ForeignKey, Boolean, JSON
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, Session

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

# Database Connection: Supabase PostgreSQL if provided, otherwise local SQLite
DATABASE_URL = os.getenv("DATABASE_URL") or os.getenv("SUPABASE_DB_URL")
if not DATABASE_URL:
    SQLITE_PATH = BASE_DIR / "recoverai.db"
    DATABASE_URL = f"sqlite:///{SQLITE_PATH}"

# Connect args for SQLite compatibility
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ==========================================
# 1. CUSTOMERS TABLE
# ==========================================
class Customer(Base):
    __tablename__ = "customers"

    id = Column(String(64), primary_key=True, default=lambda: f"CUST_{uuid.uuid4().hex[:8]}")
    customer_reference = Column(String(64), unique=True, index=True, nullable=False)
    total_transactions = Column(Integer, default=0)
    successful_transactions = Column(Integer, default=0)
    failed_transactions = Column(Integer, default=0)
    total_spend = Column(Float, default=0.0)
    customer_tier = Column(String(16), default="MEDIUM") # VIP, HIGH, MEDIUM, LOW
    created_at = Column(DateTime, default=datetime.utcnow)

    transactions = relationship("Transaction", back_populates="customer")

    def to_dict(self):
        return {
            "id": self.id,
            "customer_reference": self.customer_reference,
            "total_transactions": self.total_transactions,
            "successful_transactions": self.successful_transactions,
            "failed_transactions": self.failed_transactions,
            "total_spend": self.total_spend,
            "customer_tier": self.customer_tier,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

# ==========================================
# 2. TRANSACTIONS TABLE
# ==========================================
class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String(64), primary_key=True, default=lambda: f"TX_{uuid.uuid4().hex[:8]}")
    transaction_reference = Column(String(64), unique=True, index=True, nullable=False)
    customer_id = Column(String(64), ForeignKey("customers.id"), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    currency = Column(String(8), default="INR")
    payment_method = Column(String(32), nullable=False) # upi, card, netbanking, wallet
    status = Column(String(32), default="FAILED")       # FAILED, AT_RISK, RECOVERED, ESCALATED, STOPPED
    failure_reason = Column(String(64), nullable=False) # timeout, card_declined, insufficient_funds, abandoned, etc.
    failure_category = Column(String(64), default="TEMPORARY_NETWORK")
    attempt_number = Column(Integer, default=1)
    fraud_score = Column(Float, default=0.05)
    recovery_probability = Column(Float, default=0.50)
    recommended_strategy = Column(String(32), default="SMART_RETRY")
    amount_recovered = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    failed_at = Column(DateTime, default=datetime.utcnow)

    # Backwards compatibility properties
    @property
    def transaction_id(self):
        return self.transaction_reference

    @property
    def customer_value(self):
        return self.customer.customer_tier if self.customer else "MEDIUM"

    @property
    def fraud_probability(self):
        return self.fraud_score

    @property
    def recovered_amount(self):
        return self.amount_recovered

    @property
    def recovery_action(self):
        return self.recommended_strategy

    customer = relationship("Customer", back_populates="transactions")
    risk_scores = relationship("RiskScore", back_populates="transaction", cascade="all, delete-orphan")
    strategies = relationship("RecoveryStrategy", back_populates="transaction", cascade="all, delete-orphan")
    decisions = relationship("RecoveryDecision", back_populates="transaction", cascade="all, delete-orphan")
    policy_decisions = relationship("PolicyDecision", back_populates="transaction", cascade="all, delete-orphan")
    attempts = relationship("RecoveryAttempt", back_populates="transaction", cascade="all, delete-orphan")
    outcomes = relationship("RecoveryOutcome", back_populates="transaction", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="transaction", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "transaction_id": self.transaction_reference,
            "transaction_reference": self.transaction_reference,
            "customer_id": self.customer_id,
            "customer_reference": self.customer.customer_reference if self.customer else self.customer_id,
            "customer_value": self.customer.customer_tier if self.customer else "MEDIUM",
            "customer_history": {
                "successful_transactions": self.customer.successful_transactions if self.customer else 0,
                "failed_transactions": self.customer.failed_transactions if self.customer else 0,
                "total_spend": self.customer.total_spend if self.customer else 0.0,
            } if self.customer else {},
            "amount": self.amount,
            "currency": self.currency,
            "payment_method": self.payment_method,
            "status": self.status,
            "failure_reason": self.failure_reason,
            "failure_category": self.failure_category,
            "attempt_number": self.attempt_number,
            "fraud_score": self.fraud_score,
            "fraud_probability": self.fraud_score,
            "recovery_probability": self.recovery_probability,
            "recommended_strategy": self.recommended_strategy,
            "recovery_action": self.recommended_strategy,
            "amount_recovered": self.amount_recovered,
            "recovered_amount": self.amount_recovered,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "failed_at": self.failed_at.isoformat() if self.failed_at else None,
        }

# ==========================================
# 3. RISK SCORES TABLE
# ==========================================
class RiskScore(Base):
    __tablename__ = "risk_scores"

    id = Column(String(64), primary_key=True, default=lambda: f"RS_{uuid.uuid4().hex[:8]}")
    transaction_id = Column(String(64), ForeignKey("transactions.id"), nullable=False, index=True)
    fraud_score = Column(Float, nullable=False)
    recovery_probability = Column(Float, nullable=False)
    revenue_at_risk = Column(Float, nullable=False)
    risk_level = Column(String(16), default="LOW") # LOW, MEDIUM, HIGH, CRITICAL
    created_at = Column(DateTime, default=datetime.utcnow)

    transaction = relationship("Transaction", back_populates="risk_scores")

    def to_dict(self):
        return {
            "id": self.id,
            "transaction_id": self.transaction_id,
            "fraud_score": self.fraud_score,
            "recovery_probability": self.recovery_probability,
            "revenue_at_risk": self.revenue_at_risk,
            "risk_level": self.risk_level,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

# ==========================================
# 4. RECOVERY STRATEGIES (COUNTERFACTUALS)
# ==========================================
class RecoveryStrategy(Base):
    __tablename__ = "recovery_strategies"

    id = Column(String(64), primary_key=True, default=lambda: f"ST_{uuid.uuid4().hex[:8]}")
    transaction_id = Column(String(64), ForeignKey("transactions.id"), nullable=False, index=True)
    strategy = Column(String(32), nullable=False) # SMART_RETRY, ALTERNATE_PAYMENT, CUSTOMER_NUDGE, STOP, HUMAN_ESCALATION
    success_probability = Column(Float, nullable=False)
    expected_recovery = Column(Float, nullable=False)
    recovery_cost = Column(Float, default=0.0)
    risk_penalty = Column(Float, default=0.0)
    friction_penalty = Column(Float, default=0.0)
    recovery_score = Column(Float, nullable=False)
    is_recommended = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    transaction = relationship("Transaction", back_populates="strategies")

    def to_dict(self):
        return {
            "id": self.id,
            "transaction_id": self.transaction_id,
            "strategy": self.strategy,
            "success_probability": self.success_probability,
            "expected_recovery": self.expected_recovery,
            "recovery_cost": self.recovery_cost,
            "risk_penalty": self.risk_penalty,
            "friction_penalty": self.friction_penalty,
            "recovery_score": self.recovery_score,
            "is_recommended": self.is_recommended,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

# ==========================================
# 5. RECOVERY DECISIONS (AI AGENT)
# ==========================================
class RecoveryDecision(Base):
    __tablename__ = "recovery_decisions"

    id = Column(String(64), primary_key=True, default=lambda: f"DEC_{uuid.uuid4().hex[:8]}")
    transaction_id = Column(String(64), ForeignKey("transactions.id"), nullable=False, index=True)
    recommended_strategy = Column(String(32), nullable=False)
    confidence = Column(Float, default=0.85)
    reason = Column(Text, nullable=False)
    expected_recovery = Column(Float, default=0.0)
    risk_level = Column(String(16), default="LOW")
    next_action = Column(String(64), default="EXECUTE")
    created_at = Column(DateTime, default=datetime.utcnow)

    transaction = relationship("Transaction", back_populates="decisions")

    def to_dict(self):
        return {
            "id": self.id,
            "transaction_id": self.transaction_id,
            "recommended_strategy": self.recommended_strategy,
            "confidence": self.confidence,
            "reason": self.reason,
            "expected_recovery": self.expected_recovery,
            "risk_level": self.risk_level,
            "next_action": self.next_action,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

# ==========================================
# 6. POLICY DECISIONS (DETERMINISTIC SAFETY)
# ==========================================
class PolicyDecision(Base):
    __tablename__ = "policy_decisions"

    id = Column(String(64), primary_key=True, default=lambda: f"POL_{uuid.uuid4().hex[:8]}")
    transaction_id = Column(String(64), ForeignKey("transactions.id"), nullable=False, index=True)
    ai_recommendation = Column(String(32), nullable=False)
    policy_result = Column(String(32), nullable=False) # APPROVED, OVERRIDDEN, BLOCKED, ESCALATED, STOPPED
    policy_reason = Column(Text, nullable=False)
    rules_triggered = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    transaction = relationship("Transaction", back_populates="policy_decisions")

    def to_dict(self):
        return {
            "id": self.id,
            "transaction_id": self.transaction_id,
            "ai_recommendation": self.ai_recommendation,
            "policy_result": self.policy_result,
            "policy_reason": self.policy_reason,
            "rules_triggered": self.rules_triggered,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

# ==========================================
# 7. RECOVERY ATTEMPTS
# ==========================================
class RecoveryAttempt(Base):
    __tablename__ = "recovery_attempts"

    id = Column(String(64), primary_key=True, default=lambda: f"ATT_{uuid.uuid4().hex[:8]}")
    transaction_id = Column(String(64), ForeignKey("transactions.id"), nullable=False, index=True)
    strategy = Column(String(32), nullable=False)
    attempt_number = Column(Integer, default=1)
    status = Column(String(32), default="SUCCESS") # SUCCESS, FAILED, ESCALATED, STOPPED
    amount_recovered = Column(Float, default=0.0)
    executed_at = Column(DateTime, default=datetime.utcnow)

    transaction = relationship("Transaction", back_populates="attempts")

    def to_dict(self):
        return {
            "id": self.id,
            "transaction_id": self.transaction_id,
            "strategy": self.strategy,
            "attempt_number": self.attempt_number,
            "status": self.status,
            "amount_recovered": self.amount_recovered,
            "executed_at": self.executed_at.isoformat() if self.executed_at else None,
        }

# ==========================================
# 8. RECOVERY OUTCOMES
# ==========================================
class RecoveryOutcome(Base):
    __tablename__ = "recovery_outcomes"

    id = Column(String(64), primary_key=True, default=lambda: f"OUT_{uuid.uuid4().hex[:8]}")
    transaction_id = Column(String(64), ForeignKey("transactions.id"), nullable=False, index=True)
    result = Column(String(32), nullable=False) # SUCCESS, FAILED, ESCALATED, STOPPED
    amount_recovered = Column(Float, default=0.0)
    recovery_cost = Column(Float, default=0.0)
    final_status = Column(String(32), default="RECOVERED")
    completed_at = Column(DateTime, default=datetime.utcnow)

    transaction = relationship("Transaction", back_populates="outcomes")

    def to_dict(self):
        return {
            "id": self.id,
            "transaction_id": self.transaction_id,
            "result": self.result,
            "amount_recovered": self.amount_recovered,
            "recovery_cost": self.recovery_cost,
            "final_status": self.final_status,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }

# ==========================================
# 9. AUDIT LOGS TABLE
# ==========================================
class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    transaction_id = Column(String(64), ForeignKey("transactions.id"), nullable=False, index=True)
    event_type = Column(String(64), nullable=False) # Failure detected, Risk Analysis, AI Decision, Policy Check, etc.
    actor = Column(String(64), default="SYSTEM")    # REVENUE_DETECTOR, AI_AGENT, POLICY_ENGINE, EXECUTOR, OPERATOR
    action = Column(String(64), nullable=False)
    decision = Column(String(64), nullable=False)
    reason = Column(Text, nullable=True)
    metadata_json = Column(Text, nullable=True)     # JSON string of contextual parameters
    amount = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Backwards compatibility properties
    @property
    def timestamp(self):
        return self.created_at

    @property
    def event(self):
        return self.event_type

    @property
    def result(self):
        return self.decision

    transaction = relationship("Transaction", back_populates="audit_logs")

    def to_dict(self):
        return {
            "id": self.id,
            "transaction_id": self.transaction.transaction_reference if self.transaction else self.transaction_id,
            "event": self.event_type,
            "event_type": self.event_type,
            "actor": self.actor,
            "action": self.action,
            "decision": self.decision,
            "result": self.decision,
            "reason": self.reason,
            "amount": self.amount,
            "timestamp": self.created_at.isoformat() if self.created_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

# ==========================================
# DATABASE HELPER FUNCTIONS
# ==========================================
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)

def seed_database_if_empty():
    """Initializes and seeds database with the 5 Buildathon Demo Scenarios plus 75 realistic records."""
    init_db()
    db = SessionLocal()
    try:
        if db.query(Transaction).count() > 0:
            print("Database already contains transaction data.")
            return

        print("Seeding database with Buildathon Track 3 Demo Scenarios...")
        
        # 1. Create Core Customers
        customers_data = [
            {"ref": "CUST_001_PREMIUM", "tier": "VIP", "total": 24, "succ": 23, "fail": 1, "spend": 145000.0},
            {"ref": "CUST_002_LOYAL", "tier": "HIGH", "total": 14, "succ": 13, "fail": 1, "spend": 48500.0},
            {"ref": "CUST_003_STANDARD", "tier": "MEDIUM", "total": 6, "succ": 5, "fail": 1, "spend": 12400.0},
            {"ref": "CUST_004_NEW", "tier": "LOW", "total": 1, "succ": 0, "fail": 1, "spend": 450.0},
            {"ref": "CUST_005_SUSPICIOUS", "tier": "LOW", "total": 2, "succ": 0, "fail": 2, "spend": 0.0},
        ]
        
        cust_map = {}
        for c in customers_data:
            cust = Customer(
                id=c["ref"],
                customer_reference=c["ref"],
                total_transactions=c["total"],
                successful_transactions=c["succ"],
                failed_transactions=c["fail"],
                total_spend=c["spend"],
                customer_tier=c["tier"],
            )
            db.add(cust)
            cust_map[c["ref"]] = cust
        db.commit()

        # 2. Buildathon Demo Scenarios
        # Scenario 1: Easy Recovery (Temporary failure + good customer history -> Smart Retry -> Success)
        s1 = Transaction(
            id="TX_S1_EASY",
            transaction_reference="TX001",
            customer_id=cust_map["CUST_002_LOYAL"].id,
            amount=4999.00,
            payment_method="upi",
            status="AT_RISK",
            failure_reason="timeout",
            failure_category="TEMPORARY_NETWORK",
            attempt_number=1,
            fraud_score=0.02,
            recovery_probability=0.87,
            recommended_strategy="SMART_RETRY",
            amount_recovered=0.0
        )
        db.add(s1)

        # Scenario 2: Alternate Payment (Repeated failure / Card decline -> Alternate Payment)
        s2 = Transaction(
            id="TX_S2_ALT",
            transaction_reference="TX002",
            customer_id=cust_map["CUST_001_PREMIUM"].id,
            amount=8499.00,
            payment_method="card",
            status="AT_RISK",
            failure_reason="card_declined",
            failure_category="PAYMENT_METHOD_ISSUE",
            attempt_number=1,
            fraud_score=0.04,
            recovery_probability=0.84,
            recommended_strategy="ALTERNATE_PAYMENT",
            amount_recovered=0.0
        )
        db.add(s2)

        # Scenario 3: Customer Nudge (Checkout abandonment / reasonable probability -> Nudge)
        s3 = Transaction(
            id="TX_S3_NUDGE",
            transaction_reference="TX_NUDGE_01",
            customer_id=cust_map["CUST_003_STANDARD"].id,
            amount=3200.00,
            payment_method="upi",
            status="AT_RISK",
            failure_reason="abandoned",
            failure_category="CUSTOMER_DROP_OFF",
            attempt_number=1,
            fraud_score=0.03,
            recovery_probability=0.68,
            recommended_strategy="CUSTOMER_NUDGE",
            amount_recovered=0.0
        )
        db.add(s3)

        # Scenario 4: High Fraud Risk (Fraud probability 76% -> Policy BLOCKED -> Escalation)
        s4 = Transaction(
            id="TX_S4_FRAUD",
            transaction_reference="TX003",
            customer_id=cust_map["CUST_005_SUSPICIOUS"].id,
            amount=75000.00,
            payment_method="card",
            status="AT_RISK",
            failure_reason="card_declined",
            failure_category="SUSPICIOUS_HIGH_RISK",
            attempt_number=1,
            fraud_score=0.76,
            recovery_probability=0.81,
            recommended_strategy="HUMAN_ESCALATION",
            amount_recovered=0.0
        )
        db.add(s4)

        # Scenario 5: Economically Unfavorable Recovery (Low value + 2 attempts -> STOP)
        s5 = Transaction(
            id="TX_S5_STOP",
            transaction_reference="TX004",
            customer_id=cust_map["CUST_004_NEW"].id,
            amount=450.00,
            payment_method="upi",
            status="AT_RISK",
            failure_reason="timeout",
            failure_category="TEMPORARY_NETWORK",
            attempt_number=2,
            fraud_score=0.05,
            recovery_probability=0.18,
            recommended_strategy="STOP",
            amount_recovered=0.0
        )
        db.add(s5)

        # Also add a variety of 50 background realistic transactions to populate metrics
        methods = ["upi", "card", "netbanking", "wallet"]
        reasons = [("timeout", "TEMPORARY_NETWORK"), ("card_declined", "PAYMENT_METHOD_ISSUE"), ("insufficient_funds", "INSUFFICIENT_FUNDS"), ("abandoned", "CUSTOMER_DROP_OFF")]
        
        import random
        random.seed(42)

        for i in range(1, 55):
            ref = f"TXN_10{i:02d}"
            cid = random.choice(list(cust_map.keys()))
            amt = round(random.choice([800, 1500, 2400, 4800, 9500, 16000, 32000, 68000]), 2)
            meth = random.choice(methods)
            r_pair = random.choice(reasons)
            f_score = round(random.uniform(0.01, 0.45), 3) if amt <= 50000 else round(random.uniform(0.15, 0.78), 3)
            rec_prob = round(random.uniform(0.35, 0.92), 3)
            
            # Distribution of already recovered vs at-risk
            st = random.choices(["AT_RISK", "RECOVERED", "ESCALATED", "STOPPED"], weights=[0.45, 0.35, 0.10, 0.10])[0]
            recovered_val = amt if st == "RECOVERED" else 0.0
            
            tx = Transaction(
                id=f"TX_AUTO_{i:03d}",
                transaction_reference=ref,
                customer_id=cid,
                amount=amt,
                payment_method=meth,
                status=st,
                failure_reason=r_pair[0],
                failure_category=r_pair[1],
                attempt_number=2 if st == "STOPPED" else 1,
                fraud_score=f_score,
                recovery_probability=rec_prob,
                recommended_strategy="SMART_RETRY" if "timeout" in r_pair[0] else "ALTERNATE_PAYMENT",
                amount_recovered=recovered_val
            )
            db.add(tx)

        db.commit()

        # Add initial audit events for all seeded transactions
        all_txs = db.query(Transaction).all()
        for t in all_txs:
            audit = AuditLog(
                transaction_id=t.id,
                event_type="Failure detected",
                actor="REVENUE_DETECTOR",
                action="INGEST",
                decision="ANALYSIS_QUEUED",
                reason=f"Transaction {t.transaction_reference} flagged for revenue recovery ({t.failure_reason} on {t.payment_method})",
                amount=t.amount
            )
            db.add(audit)
            if t.status == "RECOVERED":
                rec_audit = AuditLog(
                    transaction_id=t.id,
                    event_type="Recovery executed",
                    actor="EXECUTOR",
                    action=t.recommended_strategy,
                    decision="SUCCESS",
                    reason=f"Successfully restored revenue of ₹{t.amount:,.2f} via {t.recommended_strategy}",
                    amount=t.amount_recovered
                )
                db.add(rec_audit)

        db.commit()
        print("Buildathon database seeding completed successfully.")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database_if_empty()
