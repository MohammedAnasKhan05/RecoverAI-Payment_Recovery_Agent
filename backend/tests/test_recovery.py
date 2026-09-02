"""
Comprehensive Test Suite for RecoverAI Backend (Buildathon Track 3).
Tests:
- Deterministic Guardrails & Policy Engine
- Counterfactual Strategy Evaluator
- RAG Policy Retrieval and Dynamic Evaluation
- Production API Endpoints (/api/dashboard/metrics, /api/recovery/evaluate, /api/recovery/execute, etc.)
- 5 Core Buildathon Demo Scenarios
"""
import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from main import app
from database import SessionLocal, Transaction, AuditLog, seed_database_if_empty
from guardrails.rules import evaluate_guardrails
from services.counterfactual import evaluate_all_strategies
from services.policy_engine import evaluate_policy_safety
from services.rag import get_policy_store, evaluate_rag_system

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    seed_database_if_empty()

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

# ----------------------------------------------------
# 1. COUNTERFACTUAL EVALUATION TESTS
# ----------------------------------------------------
def test_counterfactual_strategies_generation():
    """Verifies that all 5 strategies are computed and compared."""
    strategies = evaluate_all_strategies(
        amount=12500.0,
        payment_method="card",
        failure_reason="card_declined",
        failure_category="PAYMENT_METHOD_ISSUE",
        attempt_number=1,
        fraud_score=0.08
    )
    assert len(strategies) == 5
    names = [s["strategy"] for s in strategies]
    assert "SMART_RETRY" in names
    assert "ALTERNATE_PAYMENT" in names
    assert "CUSTOMER_NUDGE" in names
    assert "STOP" in names
    assert "HUMAN_ESCALATION" in names

    # For card declines, Alternate Payment should have high expected recovery score
    alt = next(s for s in strategies if s["strategy"] == "ALTERNATE_PAYMENT")
    assert alt["success_probability"] >= 0.70
    assert alt["recovery_score"] > 0

# ----------------------------------------------------
# 2. DETERMINISTIC POLICY ENGINE TESTS
# ----------------------------------------------------
def test_policy_engine_fraud_override():
    """Policy must strictly BLOCK and override AI if fraud_score > 0.70."""
    res = evaluate_policy_safety(
        ai_recommendation="SMART_RETRY",
        amount=5000.0,
        fraud_score=0.78,
        attempt_number=1,
        recovery_probability=0.85,
        transaction_status="FAILED",
        failure_reason="timeout"
    )
    assert res.allowed is False
    assert res.enforced_action == "HUMAN_ESCALATION"
    assert res.policy_result == "BLOCKED"
    assert res.ai_overridden is True
    assert "HIGH_FRAUD_RISK_HARD_STOP" in res.rules_triggered

def test_policy_engine_retry_limit():
    """Policy must STOP when attempt_number >= 2."""
    res = evaluate_policy_safety(
        ai_recommendation="SMART_RETRY",
        amount=2500.0,
        fraud_score=0.05,
        attempt_number=2,
        recovery_probability=0.50,
        transaction_status="FAILED",
        failure_reason="timeout"
    )
    assert res.allowed is False
    assert res.enforced_action == "STOP"
    assert res.policy_result == "STOPPED"

def test_policy_engine_duplicate_debit():
    """Policy must HARD STOP if transaction status is already RECOVERED/SUCCESS."""
    res = evaluate_policy_safety(
        ai_recommendation="SMART_RETRY",
        amount=5000.0,
        fraud_score=0.02,
        attempt_number=1,
        recovery_probability=0.90,
        transaction_status="RECOVERED",
        failure_reason="timeout"
    )
    assert res.allowed is False
    assert res.enforced_action == "STOP"
    assert "DUPLICATE_DEBIT_PREVENTION" in res.rules_triggered

# ----------------------------------------------------
# 3. FASTAPI /API/* ENDPOINTS TESTS
# ----------------------------------------------------
def test_api_dashboard_metrics(client):
    res = client.get("/api/dashboard/metrics")
    assert res.status_code == 200
    data = res.json()
    assert "revenue_metrics" in data
    assert "breakdown" in data["revenue_metrics"]
    assert "recoverable" in data["revenue_metrics"]["breakdown"]
    assert "alternate_method_recommended" in data["revenue_metrics"]["breakdown"]
    assert "high_risk" in data["revenue_metrics"]["breakdown"]
    assert "unrecoverable" in data["revenue_metrics"]["breakdown"]
    assert "agent_metrics" in data
    assert "risk_metrics" in data
    assert "strategy_performance" in data

def test_api_transactions_list(client):
    res = client.get("/api/transactions?limit=10")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] > 0
    assert len(data["transactions"]) <= 10

def test_api_transaction_detail(client):
    res = client.get("/api/transactions/TX001")
    assert res.status_code == 200
    data = res.json()
    assert data["transaction"]["transaction_reference"] == "TX001"
    assert "counterfactual_strategies" in data
    assert len(data["counterfactual_strategies"]) == 5
    assert "ai_decision" in data
    assert "policy_decision" in data

def test_api_recovery_evaluate(client):
    payload = {
        "amount": 7500.0,
        "payment_method": "upi",
        "failure_reason": "timeout",
        "attempt_number": 1,
        "fraud_score": 0.04
    }
    res = client.post("/api/recovery/evaluate", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "counterfactual_strategies" in data
    assert len(data["counterfactual_strategies"]) == 5

def test_api_policy_check(client):
    payload = {
        "ai_recommendation": "SMART_RETRY",
        "amount": 75000.0,
        "fraud_score": 0.80,
        "attempt_number": 1,
        "recovery_probability": 0.85,
        "status": "AT_RISK",
        "failure_reason": "card_declined"
    }
    res = client.post("/api/policy/check", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["allowed"] is False
    assert data["enforced_action"] == "HUMAN_ESCALATION"

# ----------------------------------------------------
# 4. 5 BUILDATHON DEMO SCENARIOS TESTS
# ----------------------------------------------------
def test_demo_scenario_1_easy_recovery(client):
    """Scenario 1: Timeout -> Smart Retry -> Success -> Recovered ₹4,999"""
    res = client.post("/api/recovery/execute", json={"transaction_id": "TX001"})
    assert res.status_code == 200
    data = res.json()
    assert data["execution_result"] == "SUCCESS"
    assert data["final_action"] in ["SMART_RETRY", "RETRY"]
    assert data["transaction"]["status"] == "RECOVERED"
    assert data["transaction"]["amount_recovered"] == 4999.0

def test_demo_scenario_2_alternate_payment(client):
    """Scenario 2: Card decline -> Alternate Payment -> Success"""
    res = client.post("/api/recovery/execute", json={"transaction_id": "TX002"})
    assert res.status_code == 200
    data = res.json()
    assert data["execution_result"] == "SUCCESS"
    assert data["final_action"] == "ALTERNATE_PAYMENT"
    assert data["transaction"]["status"] == "RECOVERED"

def test_demo_scenario_3_customer_nudge(client):
    """Scenario 3: Abandoned -> Customer Nudge -> Success"""
    res = client.post("/api/recovery/execute", json={"transaction_id": "TX_NUDGE_01"})
    assert res.status_code == 200
    data = res.json()
    assert data["execution_result"] == "SUCCESS"
    assert data["final_action"] == "CUSTOMER_NUDGE"
    assert data["transaction"]["status"] == "RECOVERED"

def test_demo_scenario_4_high_fraud_risk(client):
    """Scenario 4: 76% Fraud Risk -> Policy Blocks -> Escalation"""
    res = client.post("/api/recovery/execute", json={"transaction_id": "TX003"})
    assert res.status_code == 200
    data = res.json()
    assert data["execution_result"] == "ESCALATED"
    assert data["transaction"]["status"] == "ESCALATED"

def test_demo_scenario_5_unfavorable_recovery(client):
    """Scenario 5: Low value + Attempt 2 -> Stop"""
    res = client.post("/api/recovery/execute", json={"transaction_id": "TX004"})
    assert res.status_code == 200
    data = res.json()
    assert data["execution_result"] == "STOPPED"
    assert data["transaction"]["status"] == "STOPPED"

def test_health_endpoint(client):
    """Verifies that the /health endpoint returns 200 with operational status."""
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["guardrails"] == "Active"
    assert data["rag_engine"] == "Operational"
    assert "database" in data

