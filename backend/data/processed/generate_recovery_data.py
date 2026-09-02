"""
Synthetic Recovery Dataset Generator for RecoverAI.
Guarantees explicit hackathon demo cases (TX001, TX003, TX004) alongside 80 realistic varied transactions.
"""
import csv
import random
from pathlib import Path

random.seed(42)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
OUTPUT_FILE = BASE_DIR / "data" / "processed" / "recovery_transactions.csv"

def generate_transactions(num_records=80):
    records = []

    # Priority Demo Scenarios requested for hackathon presentation:
    # 1. TX001: UPI Timeout, recoverable, success expected
    records.append({
        "transaction_id": "TX001",
        "customer_id": "CUST_9021",
        "amount": 4999.00,
        "payment_method": "upi",
        "failure_reason": "timeout",
        "attempt_number": 1,
        "customer_value": "HIGH",
        "fraud_probability": 0.02,
        "recovery_probability": 0.87,
        "status": "AT_RISK",
        "recovery_action": "RETRY",
        "recovered_amount": 0.0
    })

    # 2. TX002: Card Decline, alternate payment
    records.append({
        "transaction_id": "TX002",
        "customer_id": "CUST_5842",
        "amount": 3450.00,
        "payment_method": "card",
        "failure_reason": "card_declined",
        "attempt_number": 1,
        "customer_value": "MEDIUM",
        "fraud_probability": 0.04,
        "recovery_probability": 0.78,
        "status": "AT_RISK",
        "recovery_action": "ALTERNATE_PAYMENT",
        "recovered_amount": 0.0
    })

    # 3. TX003: High Value & High Fraud Risk, Escalate expected
    records.append({
        "transaction_id": "TX003",
        "customer_id": "CUST_7714",
        "amount": 75000.00,
        "payment_method": "card",
        "failure_reason": "card_declined",
        "attempt_number": 1,
        "customer_value": "VIP",
        "fraud_probability": 0.76,
        "recovery_probability": 0.81,
        "status": "AT_RISK",
        "recovery_action": "ESCALATE",
        "recovered_amount": 0.0
    })

    # 4. TX004: Retry limit reached, Stop expected
    records.append({
        "transaction_id": "TX004",
        "customer_id": "CUST_3190",
        "amount": 2500.00,
        "payment_method": "upi",
        "failure_reason": "timeout",
        "attempt_number": 2,
        "customer_value": "MEDIUM",
        "fraud_probability": 0.05,
        "recovery_probability": 0.40,
        "status": "AT_RISK",
        "recovery_action": "STOP",
        "recovered_amount": 0.0
    })

    scenarios = [
        ("upi", "timeout", 1, (200, 4500), (0.01, 0.20), (0.75, 0.95), "AT_RISK", "RETRY", 0.0),
        ("upi", "timeout", 1, (500, 8000), (0.02, 0.15), (0.80, 0.96), "RECOVERED", "RETRY", "MATCH_AMOUNT"),
        ("card", "card_declined", 1, (1200, 15000), (0.05, 0.35), (0.60, 0.85), "AT_RISK", "ALTERNATE_PAYMENT", 0.0),
        ("card", "card_declined", 1, (800, 12000), (0.04, 0.25), (0.65, 0.88), "RECOVERED", "ALTERNATE_PAYMENT", "MATCH_AMOUNT"),
        ("card", "card_declined", 1, (2500, 9000), (0.10, 0.40), (0.35, 0.55), "FAILED", "ALTERNATE_PAYMENT", 0.0),
        ("upi", "timeout", 2, (1500, 12000), (0.05, 0.30), (0.40, 0.70), "STOPPED", "STOP", 0.0),
        ("card", "insufficient_funds", 2, (3000, 20000), (0.10, 0.40), (0.30, 0.60), "STOPPED", "STOP", 0.0),
        ("upi", "timeout", 1, (55000, 180000), (0.15, 0.45), (0.65, 0.85), "ESCALATED", "ESCALATE", 0.0),
        ("card", "card_declined", 1, (75000, 250000), (0.20, 0.50), (0.50, 0.80), "ESCALATED", "ESCALATE", 0.0),
        ("netbanking", "auth_failed", 1, (10000, 48000), (0.75, 0.94), (0.20, 0.50), "ESCALATED", "ESCALATE", 0.0),
        ("wallet", "abandoned", 1, (300, 3500), (0.01, 0.10), (0.15, 0.28), "STOPPED", "STOP", 0.0),
        ("upi", "abandoned", 1, (400, 6000), (0.02, 0.18), (0.50, 0.75), "AT_RISK", "SEND_REMINDER", 0.0),
        ("card", "abandoned", 1, (1500, 8500), (0.03, 0.20), (0.55, 0.78), "RECOVERED", "SEND_REMINDER", "MATCH_AMOUNT"),
    ]
    
    cust_tiers = ["LOW", "MEDIUM", "HIGH", "VIP"]
    tx_count = 1000
    
    for i in range(num_records):
        tx_count += 1
        scenario = scenarios[i % len(scenarios)]
        method, reason, attempt, amt_range, f_range, r_range, status, action, rec_type = scenario
        
        amount = round(random.uniform(amt_range[0], amt_range[1]), 2)
        fraud_prob = round(random.uniform(f_range[0], f_range[1]), 3)
        recov_prob = round(random.uniform(r_range[0], r_range[1]), 3)
        cust_val = random.choices(cust_tiers, weights=[0.4, 0.3, 0.2, 0.1])[0]
        
        recovered_amt = amount if rec_type == "MATCH_AMOUNT" else 0.0
        
        records.append({
            "transaction_id": f"TXN_{tx_count}",
            "customer_id": f"CUST_{random.randint(1000, 9999)}",
            "amount": amount,
            "payment_method": method,
            "failure_reason": reason,
            "attempt_number": attempt,
            "customer_value": cust_val,
            "fraud_probability": fraud_prob,
            "recovery_probability": recov_prob,
            "status": status,
            "recovery_action": action,
            "recovered_amount": recovered_amt
        })
        
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(records[0].keys()))
        writer.writeheader()
        writer.writerows(records)
    print(f"Generated {len(records)} demo recovery transactions in {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_transactions(80)
