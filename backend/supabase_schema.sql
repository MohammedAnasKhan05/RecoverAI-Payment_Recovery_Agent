-- ====================================================================
-- RecoverAI — Full 9-Table Supabase PostgreSQL Schema & Seed Script
-- Razorpay Buildathon Track 3: Context-Aware Autonomous Revenue Recovery
-- ====================================================================

-- 1. CUSTOMERS TABLE
CREATE TABLE IF NOT EXISTS customers (
    id VARCHAR(64) PRIMARY KEY,
    customer_reference VARCHAR(64) UNIQUE NOT NULL,
    total_transactions INTEGER DEFAULT 0,
    successful_transactions INTEGER DEFAULT 0,
    failed_transactions INTEGER DEFAULT 0,
    total_spend NUMERIC(12, 2) DEFAULT 0.00,
    customer_tier VARCHAR(16) DEFAULT 'MEDIUM',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_customers_reference ON customers(customer_reference);

-- 2. TRANSACTIONS TABLE
CREATE TABLE IF NOT EXISTS transactions (
    id VARCHAR(64) PRIMARY KEY,
    transaction_reference VARCHAR(64) UNIQUE NOT NULL,
    customer_id VARCHAR(64) REFERENCES customers(id) ON DELETE CASCADE,
    amount NUMERIC(12, 2) NOT NULL,
    currency VARCHAR(8) DEFAULT 'INR',
    payment_method VARCHAR(32) NOT NULL,
    status VARCHAR(32) DEFAULT 'FAILED',
    failure_reason VARCHAR(64) NOT NULL,
    failure_category VARCHAR(64) DEFAULT 'TEMPORARY_NETWORK',
    attempt_number INTEGER DEFAULT 1,
    fraud_score NUMERIC(5, 4) DEFAULT 0.0500,
    recovery_probability NUMERIC(5, 4) DEFAULT 0.5000,
    recommended_strategy VARCHAR(32) DEFAULT 'SMART_RETRY',
    amount_recovered NUMERIC(12, 2) DEFAULT 0.00,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    failed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_transactions_reference ON transactions(transaction_reference);
CREATE INDEX IF NOT EXISTS idx_transactions_customer ON transactions(customer_id);
CREATE INDEX IF NOT EXISTS idx_transactions_status ON transactions(status);

-- 3. RISK SCORES TABLE
CREATE TABLE IF NOT EXISTS risk_scores (
    id VARCHAR(64) PRIMARY KEY,
    transaction_id VARCHAR(64) REFERENCES transactions(id) ON DELETE CASCADE,
    fraud_score NUMERIC(5, 4) NOT NULL,
    recovery_probability NUMERIC(5, 4) NOT NULL,
    revenue_at_risk NUMERIC(12, 2) NOT NULL,
    risk_level VARCHAR(16) DEFAULT 'LOW',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_risk_scores_tx ON risk_scores(transaction_id);

-- 4. RECOVERY STRATEGIES TABLE (COUNTERFACTUAL EVALUATION)
CREATE TABLE IF NOT EXISTS recovery_strategies (
    id VARCHAR(64) PRIMARY KEY,
    transaction_id VARCHAR(64) REFERENCES transactions(id) ON DELETE CASCADE,
    strategy VARCHAR(32) NOT NULL,
    success_probability NUMERIC(5, 4) NOT NULL,
    expected_recovery NUMERIC(12, 2) NOT NULL,
    recovery_cost NUMERIC(12, 2) DEFAULT 0.00,
    risk_penalty NUMERIC(12, 2) DEFAULT 0.00,
    friction_penalty NUMERIC(12, 2) DEFAULT 0.00,
    recovery_score NUMERIC(12, 2) NOT NULL,
    is_recommended BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_recovery_strategies_tx ON recovery_strategies(transaction_id);

-- 5. RECOVERY DECISIONS TABLE (AI AGENT)
CREATE TABLE IF NOT EXISTS recovery_decisions (
    id VARCHAR(64) PRIMARY KEY,
    transaction_id VARCHAR(64) REFERENCES transactions(id) ON DELETE CASCADE,
    recommended_strategy VARCHAR(32) NOT NULL,
    confidence NUMERIC(5, 4) DEFAULT 0.8500,
    reason TEXT NOT NULL,
    expected_recovery NUMERIC(12, 2) DEFAULT 0.00,
    risk_level VARCHAR(16) DEFAULT 'LOW',
    next_action VARCHAR(64) DEFAULT 'EXECUTE',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_recovery_decisions_tx ON recovery_decisions(transaction_id);

-- 6. POLICY DECISIONS TABLE (DETERMINISTIC SAFETY ENGINE)
CREATE TABLE IF NOT EXISTS policy_decisions (
    id VARCHAR(64) PRIMARY KEY,
    transaction_id VARCHAR(64) REFERENCES transactions(id) ON DELETE CASCADE,
    ai_recommendation VARCHAR(32) NOT NULL,
    policy_result VARCHAR(32) NOT NULL,
    policy_reason TEXT NOT NULL,
    rules_triggered TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_policy_decisions_tx ON policy_decisions(transaction_id);

-- 7. RECOVERY ATTEMPTS TABLE
CREATE TABLE IF NOT EXISTS recovery_attempts (
    id VARCHAR(64) PRIMARY KEY,
    transaction_id VARCHAR(64) REFERENCES transactions(id) ON DELETE CASCADE,
    strategy VARCHAR(32) NOT NULL,
    attempt_number INTEGER DEFAULT 1,
    status VARCHAR(32) DEFAULT 'SUCCESS',
    amount_recovered NUMERIC(12, 2) DEFAULT 0.00,
    executed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_recovery_attempts_tx ON recovery_attempts(transaction_id);

-- 8. RECOVERY OUTCOMES TABLE
CREATE TABLE IF NOT EXISTS recovery_outcomes (
    id VARCHAR(64) PRIMARY KEY,
    transaction_id VARCHAR(64) REFERENCES transactions(id) ON DELETE CASCADE,
    result VARCHAR(32) NOT NULL,
    amount_recovered NUMERIC(12, 2) DEFAULT 0.00,
    recovery_cost NUMERIC(12, 2) DEFAULT 0.00,
    final_status VARCHAR(32) DEFAULT 'RECOVERED',
    completed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_recovery_outcomes_tx ON recovery_outcomes(transaction_id);

-- 9. AUDIT LOGS TABLE
CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    transaction_id VARCHAR(64) REFERENCES transactions(id) ON DELETE CASCADE,
    event_type VARCHAR(64) NOT NULL,
    actor VARCHAR(64) DEFAULT 'SYSTEM',
    action VARCHAR(64) NOT NULL,
    decision VARCHAR(64) NOT NULL,
    reason TEXT,
    metadata_json TEXT,
    amount NUMERIC(12, 2) DEFAULT 0.00,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_audit_logs_tx ON audit_logs(transaction_id);

-- ====================================================================
-- SEED INITIAL BUILDATHON CUSTOMERS & CORE DEMO SCENARIOS
-- ====================================================================
INSERT INTO customers (id, customer_reference, total_transactions, successful_transactions, failed_transactions, total_spend, customer_tier)
VALUES
    ('CUST_001_PREMIUM', 'CUST_001_PREMIUM', 24, 23, 1, 145000.00, 'VIP'),
    ('CUST_002_LOYAL', 'CUST_002_LOYAL', 14, 13, 1, 48500.00, 'HIGH'),
    ('CUST_003_STANDARD', 'CUST_003_STANDARD', 6, 5, 1, 12400.00, 'MEDIUM'),
    ('CUST_004_NEW', 'CUST_004_NEW', 1, 0, 1, 450.00, 'LOW'),
    ('CUST_005_SUSPICIOUS', 'CUST_005_SUSPICIOUS', 2, 0, 2, 0.00, 'LOW')
ON CONFLICT (id) DO NOTHING;

-- Seed 5 Core Demo Scenarios
INSERT INTO transactions (id, transaction_reference, customer_id, amount, payment_method, status, failure_reason, failure_category, attempt_number, fraud_score, recovery_probability, recommended_strategy, amount_recovered)
VALUES
    ('TX_S1_EASY', 'TX001', 'CUST_002_LOYAL', 4999.00, 'upi', 'AT_RISK', 'timeout', 'TEMPORARY_NETWORK', 1, 0.0200, 0.8700, 'SMART_RETRY', 0.00),
    ('TX_S2_ALT', 'TX002', 'CUST_001_PREMIUM', 8499.00, 'card', 'AT_RISK', 'card_declined', 'PAYMENT_METHOD_ISSUE', 1, 0.0400, 0.8400, 'ALTERNATE_PAYMENT', 0.00),
    ('TX_S3_NUDGE', 'TX_NUDGE_01', 'CUST_003_STANDARD', 3200.00, 'upi', 'AT_RISK', 'abandoned', 'CUSTOMER_DROP_OFF', 1, 0.0300, 0.6800, 'CUSTOMER_NUDGE', 0.00),
    ('TX_S4_FRAUD', 'TX003', 'CUST_005_SUSPICIOUS', 75000.00, 'card', 'AT_RISK', 'card_declined', 'SUSPICIOUS_HIGH_RISK', 1, 0.7600, 0.8100, 'HUMAN_ESCALATION', 0.00),
    ('TX_S5_STOP', 'TX004', 'CUST_004_NEW', 450.00, 'upi', 'AT_RISK', 'timeout', 'TEMPORARY_NETWORK', 2, 0.0500, 0.1800, 'STOP', 0.00)
ON CONFLICT (id) DO NOTHING;

-- Initial audit trail entries
INSERT INTO audit_logs (transaction_id, event_type, actor, action, decision, reason, amount)
SELECT id, 'Failure detected', 'REVENUE_DETECTOR', 'INGEST', 'ANALYSIS_QUEUED', 'Transaction queued for autonomous revenue recovery analysis', amount
FROM transactions
WHERE transaction_reference IN ('TX001', 'TX002', 'TX_NUDGE_01', 'TX003', 'TX004');
