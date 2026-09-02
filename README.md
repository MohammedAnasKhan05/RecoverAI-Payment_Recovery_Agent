# RecoverAI — Context-Aware Autonomous Revenue Recovery Agent

```
========================================================================================
  RAZORPAY BUILDATHON TRACK 3: AI REVENUE RECOVERY
  Project Name   : RecoverAI
  Tagline        : "Recover revenue before it's lost."
  Architecture   : 9-Table Supabase PostgreSQL + FastAPI + React 19 + PaySim ML + RAG
  Core Question  : "What is the safest and most economically effective way to recover 
                   this revenue — and should we recover it at all?"
========================================================================================
```

[![Python 3.11](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React 19](https://img.shields.io/badge/React-19.0-61DAFB?logo=react&logoColor=black)](https://react.dev)
[![Vite](https://img.shields.io/badge/Vite-6.0-646CFF?logo=vite&logoColor=white)](https://vitejs.dev)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.4-38B2AC?logo=tailwind-css&logoColor=white)](https://tailwindcss.com)
[![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-3ECF8E?logo=supabase&logoColor=white)](https://supabase.com)
[![SQLite](https://img.shields.io/badge/SQLite-Zero--Config_Fallback-003B57?logo=sqlite&logoColor=white)](https://sqlite.org)
[![PaySim ML](https://img.shields.io/badge/PaySim_ML-0.9993_ROC--AUC-FF6F00?logo=scikit-learn&logoColor=white)](https://scikit-learn.org)
[![RAG Benchmark](https://img.shields.io/badge/RAG_Benchmark-92.8%25_Faithfulness-blueviolet)](#4-automated-rag-policy-knowledge-store)
[![Tests Passing](https://img.shields.io/badge/Tests-14%2F14_Passing-brightgreen)](tests/test_recovery.py)

---

## 1. Executive Summary & Problem Statement

In digital commerce and fintech ecosystems, payment failure is one of the leading drivers of involuntary customer churn and lost revenue. Traditional payment gateways and merchants handle failures through **naive retry scripts** that blindly trigger automated debits on the exact same rail without regard for the underlying failure cause, customer relationship value, or fraud exposure.

### The Problem with Naive Retries

| Traditional Payment Retry Failure | Real-World Impact | How RecoverAI Solves It |
| :--- | :--- | :--- |
| **Customer Alienation & Churn** | Customers receive surprise debits, spam OTPs, or duplicate charges, destroying trust. | **Friction-Aware Penalties**: Analyzes customer tiers (`VIP`, `HIGH`, `MEDIUM`, `LOW`) and penalizes high-friction actions mathematically. |
| **Fraud & Chargeback Exposure** | Retrying compromised cards flags merchant accounts, incurring chargeback fees and fines. | **PaySim ML + Policy Hard Stop**: Scans every transaction with ML. If fraud probability $> 70\%$, automated retries are **strictly blocked**. |
| **Operational Fee Bleed** | Merchants pay ₹5–₹15 per attempt on transactions that have near-zero mathematical probability of recovering. | **Knowing When to STOP**: If retry limits ($\ge 2$) or viability floors ($< 30\%$) are hit, RecoverAI executes a **zero-cost STOP**. |
| **Zero Context Awareness** | A card decline is repeatedly retried on the same card instead of offering the customer an alternate instrument. | **Counterfactual Switching**: Evaluates 5 recovery strategies simultaneously, recommending **Alternate Payment Links** or **Customer Nudges**. |

---

## 2. End-to-End System Architecture

```
Failed / At-Risk Transaction Ingested
                 │
                 ▼
    [1. Failure & Context Analyzer]
    ├── Failure Classification (Network, Card Decline, Balance, Abandoned, Auth)
    ├── Customer Relationship Intel (VIP, High, Medium, Low Tier)
    └── Historical Spend & Lifetime Value
                 │
                 ▼
    [2. PaySim ML Fraud Risk Engine]
    └── Scikit-Learn RandomForestClassifier (0.9993 ROC-AUC)
                 │
                 ▼
    [3. Counterfactual Strategy Evaluator] (Key Differentiator)
    ├── Strategy A: Smart Retry
    ├── Strategy B: Alternate Payment Method
    ├── Strategy C: Customer Nudge (SMS / WhatsApp)
    ├── Strategy D: Stop Recovery (Zero-Cost Preservation)
    └── Strategy E: Human Escalation (White-Glove Review)
        Formula: Net Score = (Amount × Prob) − Cost − Risk − Friction
                 │
                 ▼
    [4. Automated RAG Policy Knowledge Store]
    └── Vectorized Policy Corpus (UPI, Card, Abandonment, Escalation)
                 │
                 ▼
    [5. Structured AI Decision Agent]
    └── Synthesizes context & economics into structured JSON with measurable rationale
                 │
                 ▼
    [6. Deterministic Safety & Policy Engine]
    └── STRICT RULE: POLICY ALWAYS OVERRIDES AI
        ├── Duplicate Debit Prevention (Already RECOVERED? ➔ STOP)
        ├── Fraud Risk Hard Stop (Fraud Score > 70% ➔ BLOCKED / ESCALATE)
        ├── Attempt Limit Cap (Attempts ≥ 2 ➔ STOP)
        ├── High-Ticket Authorization (Amount > ₹50,000 ➔ ESCALATE)
        └── Economic Viability Floor (Recovery Prob < 30% ➔ STOP)
                 │
        ┌────────┴────────┐
     ALLOWED           BLOCKED
        │                 │
        ▼                 ▼
[7. Mock Action]   [Safe Termination]
 State Machine      (STOP / ESCALATE)
        │                 │
        └────────┬────────┘
                 ▼
    [8. Outcome Tracker & Feedback Loop]
    ├── Live Empirical Win-Rate Calibration
    └── Blend: 60% Transaction Context + 40% Historical Win-Rate
                 │
                 ▼
    [9. Persistent 9-Table Database & Immutable Audit Ledger]
    └── Cloud Supabase PostgreSQL / Local SQLite with Full Event Traceability
```

---

## 3. The 8 Core Engineering Engines

### 1. Failure & Context Analyzer
Categorizes failures beyond naive gateway error strings into rich actionable context:
- `TEMPORARY_NETWORK`: Transient timeouts, gateway drop-offs. High retry viability.
- `PAYMENT_METHOD_ISSUE`: Expired card, blocked instrument. Candidate for alternate payment method.
- `INSUFFICIENT_FUNDS`: Low balance. Candidate for payment link or scheduled reminder.
- `CUSTOMER_DROP_OFF`: Cart abandonment during 3DS auth. Candidate for customer nudge.
- `SUSPICIOUS_HIGH_RISK`: Elevated risk signals. Immediate escalation.

### 2. PaySim ML Fraud Risk Engine
- **Model**: `RandomForestClassifier` trained on the PaySim transaction distribution.
- **Features**: Balance deltas (`oldbalanceOrg - newbalanceOrig`), transfer-to-cashout transaction ratios, recipient balance movement, transaction velocity flags.
- **Validation ROC-AUC**: **0.9993**
- **Model Binary**: `backend/ml/fraud_model.pkl`

### 3. Counterfactual Strategy Evaluator *(Key Innovation)*
Evaluates **all 5 strategies simultaneously** before dispatching any recovery action:

$$\text{Recovery Score} = (\text{Amount} \times \text{Success Probability}) - \text{Recovery Cost} - \text{Risk Penalty} - \text{Customer Friction Penalty}$$

| Strategy | Success Prob | Operational Cost | Risk Penalty | Friction Penalty | Optimal Application |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Smart Retry** | 78% – 95% | ₹5.00 | $\text{Amount} \times \frac{\text{Fraud}}{2}$ | ₹10 (Low) / ₹150 (Repeat) | Transient network timeout on attempt 1 |
| **Alternate Payment** | 65% – 92% | ₹12.00 | $\text{Amount} \times \frac{\text{Fraud}}{4}$ | ₹25 (Medium) | Card decline, blocked card, repeat timeout |
| **Customer Nudge** | 45% – 85% | ₹2.50 | $\text{Amount} \times \frac{\text{Fraud}}{6}$ | ₹15 (Low) | Dropped cart, checkout abandonment |
| **Stop Recovery** | 0.0% | ₹0.00 | ₹0.00 | ₹0.00 | Retry limit reached ($\ge 2$), viability $< 30\%$ |
| **Human Escalation**| 30% – 75% | ₹150.00 | ₹0.00 (Mitigated) | ₹50 (Medium) | Fraud score $> 70\%$ or amount $> ₹50,000$ |

### 4. Automated RAG Policy Knowledge Store
- **Corpus**: 4 operational policy documents in `backend/data/policies/`:
  1. `upi_policy.txt` (16 rules: backoff retry intervals, reversal verification, PSP transient failures)
  2. `card_policy.txt` (6 sections: decline codes, alternate checkout links, retry caps)
  3. `abandonment_policy.txt` (Drop-off timing: 30m / 24h, reminder caps)
  4. `escalation_policy.txt` (Fraud triggers, high-value supervisory review, priority orders)
- **RAG Benchmark Evaluation (15 dynamic queries)**:
  - **Retrieval Accuracy**: **100.0%**
  - **Context Grounding**: **100.0%**
  - **Faithfulness Score**: **92.8%**
  - **Overall RAG Score**: **92.7%**

### 5. Structured AI Decision Agent
Produces clean, structured recommendations with transparent economic reasoning:
```json
{
  "decision": "ALTERNATE_PAYMENT",
  "confidence": 0.86,
  "reason": "Card instrument declined. Counterfactual analysis shows Alternate Payment has the highest expected recovery (₹7,139.16, 84% prob) versus immediate retry.",
  "expected_recovery": 7139.16,
  "risk_level": "LOW",
  "next_action": "SEND_PAYMENT_LINK",
  "policy_used": "card_policy.txt"
}
```

### 6. Deterministic Safety & Policy Engine
Acts as the independent security gatekeeper between the AI agent and the payment rails.
**Rule Priority Order (Policy Always Overrides AI):**
1. **Duplicate Debit Prevention**: If status is already `RECOVERED` or `SUCCESS` $\rightarrow$ Hard `STOP`.
2. **Fraud Risk Hard Stop**: If fraud score $> 0.70$ $\rightarrow$ Hard `BLOCKED` $\rightarrow$ `HUMAN_ESCALATION`.
3. **Retry Limit Exhaustion**: If attempt number $\ge 2$ $\rightarrow$ `STOP`.
4. **High-Value Supervisory Control**: If amount $> ₹50,000.00$ $\rightarrow$ `HUMAN_ESCALATION`.
5. **Economic Viability Floor**: If recovery probability $< 0.30$ $\rightarrow$ `STOP`.

### 7. Action State Machine & Outcome Tracker
Simulates action execution across payment channels:
- `SMART_RETRY` $\rightarrow$ Simulates network gateway retry.
- `ALTERNATE_PAYMENT` $\rightarrow$ Generates dynamic checkout URL for UPI QR / Netbanking.
- `CUSTOMER_NUDGE` $\rightarrow$ Dispatches pre-filled cart SMS/WhatsApp link.
- `HUMAN_ESCALATION` $\rightarrow$ Queues case to fraud analyst worklist.
- `STOP` $\rightarrow$ Closes recovery lifecycle; prevents fee bleed.

### 8. Continuous Feedback & Learning Loop
Stores execution outcomes to build live empirical win-rates:
- Smart Retry: **~75.5%** baseline
- Alternate Payment: **~84.2%** baseline
- Customer Nudge: **~64.3%** baseline
- Human Escalation: **~75.0%** baseline

Dynamically calibrates future recovery probability estimates:
$$\text{Calibrated Probability} = (0.60 \times P_{\text{transaction}}) + (0.40 \times \text{WinRate}_{\text{strategy}})$$

---

## 4. 9-Table Database Architecture

The persistence layer is configured on **Supabase PostgreSQL** (`DATABASE_URL` or `SUPABASE_DB_URL`) with graceful fallback to zero-config local **SQLite** (`recoverai.db`):

1. **`customers`**: Customer reference, tier (`VIP`, `HIGH`, `MEDIUM`, `LOW`), transaction history, lifetime spend.
2. **`transactions`**: Financial details, payment method, failure reason, failure category, attempts, status, amount recovered.
3. **`risk_scores`**: ML fraud score, recovery probability, revenue at risk, risk classification.
4. **`recovery_strategies`**: Complete 5-strategy counterfactual matrix records for every transaction.
5. **`recovery_decisions`**: AI recommendation, confidence score, financial rationale, next action directive.
6. **`policy_decisions`**: Deterministic policy result (`APPROVED`, `BLOCKED`, `OVERRIDDEN`, `ESCALATED`, `STOPPED`).
7. **`recovery_attempts`**: Action dispatched, attempt counter, execution status.
8. **`recovery_outcomes`**: Result (`SUCCESS`, `FAILED`, `ESCALATED`, `STOPPED`), amount recovered, operational cost.
9. **`audit_logs`**: Immutable compliance ledger capturing timestamp, actor, action, decision, and metadata.

---

## 5. The 5 Core Buildathon Demo Scenarios

These 5 scenarios represent the full decision spectrum of RecoverAI and are accessible via 1-click quick-launch buttons on the Dashboard hero:

### Scenario 1: Easy Recovery (`TX001`)
- **Transaction**: ₹4,999.00 via UPI
- **Customer**: Loyal Tier (14 transactions, ₹48.5k historical spend)
- **Failure**: Transient network timeout (`TEMPORARY_NETWORK`, attempt 1)
- **AI Recommendation**: `SMART_RETRY` (Expected recovery ₹4,349.13, 87% prob)
- **Policy Engine**: `APPROVED` (Passes all 5 deterministic safety checks)
- **Execution**: **SUCCESS** $\rightarrow$ Restores **₹4,999.00** directly to merchant.

### Scenario 2: Alternate Payment Method (`TX002`)
- **Transaction**: ₹8,499.00 via Credit Card
- **Customer**: VIP Tier (24 transactions, ₹1.45L historical spend)
- **Failure**: Card declined by issuing bank (`PAYMENT_METHOD_ISSUE`)
- **AI Recommendation**: `ALTERNATE_PAYMENT` (Counterfactual score ₹7,102.16 vs negative score on retry)
- **Policy Engine**: `APPROVED`
- **Execution**: **SUCCESS** $\rightarrow$ Customer completes checkout via dynamic payment link; recovers **₹8,499.00**.

### Scenario 3: Customer Nudge (`TX_NUDGE_01`)
- **Transaction**: ₹3,200.00 via UPI
- **Customer**: Standard Tier (6 transactions)
- **Failure**: Checkout session abandoned prior to authorization (`CUSTOMER_DROP_OFF`)
- **AI Recommendation**: `CUSTOMER_NUDGE` (Expected recovery ₹2,176.00, low friction)
- **Policy Engine**: `APPROVED`
- **Execution**: **SUCCESS** $\rightarrow$ Pre-filled cart reminder link recovers **₹3,200.00**.

### Scenario 4: High Fraud Risk (`TX003`)
- **Transaction**: ₹75,000.00 via Credit Card
- **Customer**: Low/Suspicious Tier (0 historical spend)
- **Failure**: Card decline with ML fraud score = **76.0%** (`SUSPICIOUS_HIGH_RISK`)
- **AI Recommendation**: `SMART_RETRY` or `ESCALATE`
- **Policy Engine**: **STRICTLY BLOCKED** (`HIGH_FRAUD_RISK_HARD_STOP` triggered; automated retry forbidden)
- **Execution**: **ESCALATED** $\rightarrow$ Routed to human risk desk; saves merchant from chargeback penalties.

### Scenario 5: Economically Unfavorable Recovery (`TX004`)
- **Transaction**: ₹450.00 via UPI
- **Customer**: New Customer (1 failed transaction)
- **Failure**: Second gateway timeout (attempt 2 of 2, 18% viability)
- **AI Recommendation**: `STOP` (Net recovery score is negative after fees and friction)
- **Policy Engine**: **STOPPED** (`RETRY_LIMIT_EXHAUSTION_STOP` triggered)
- **Execution**: **STOPPED** $\rightarrow$ Recovery halted; zero fee bleed, customer churn prevented.

---

## 6. Interactive Frontend Dashboard

Built with **React 19**, **Vite**, **Tailwind CSS**, **Recharts**, and **Lucide React** with a Razorpay-inspired fintech aesthetic:

- **Executive Dashboard (`/`)**: Metric cards for Revenue at Risk breakdown, Recovered Revenue, Recovery Rate, Operational Costs Saved, Strategy Performance charts, and 1-Click Buildathon Scenario Triggers.
- **Transactions Ledger (`/transactions`)**: Searchable, paginated transaction ledger with real-time status and payment method filters.
- **Deep-Dive Transaction View (`/transactions/:id`)**:
  - Full financial details & customer profile.
  - Side-by-side **5-Strategy Counterfactual Evaluation Matrix** with interactive visual recovery scores.
  - Transparent AI reasoning & deterministic policy validation badges.
  - 1-click **Execute Recovery** pipeline trigger.
  - Immutable audit history timeline.
- **Agent Activity & Audit Trail (`/audit`)**: Real-time event ledger tracking every automated decision, policy evaluation, and recovery dispatch.
- **RAG Policy Evaluation Suite (`/rag-evaluation`)**: Interactive benchmark dashboard displaying 15 dynamic queries, retrieval accuracy, context grounding, and faithfulness scores.

---

## 7. REST API Endpoints (`/api/*` & `/rag/*`)

| Method | Route | Purpose |
| :--- | :--- | :--- |
| `GET` | `/health` | Health check confirming database, guardrails, and RAG status. |
| `GET` | `/api/dashboard/metrics` | Revenue at risk decomposition, agent stats, risk metrics, and strategy win-rates. |
| `GET` | `/api/transactions` | Paginated transaction ledger with status and payment method filters. |
| `GET` | `/api/transactions/{id}` | Detailed transaction view with 5 counterfactual strategy comparisons and audit trail. |
| `POST`| `/api/risk/analyze` | Evaluates transaction context intelligence, fraud score, and recovery probability. |
| `POST`| `/api/recovery/evaluate` | Evaluates all 5 counterfactual recovery options and returns side-by-side economics. |
| `POST`| `/api/recovery/decide` | AI structured recovery recommendation with confidence, reason, and next action. |
| `POST`| `/api/policy/check` | Deterministic safety policy validation check (policy overrides AI). |
| `POST`| `/api/recovery/execute` | Executes state machine recovery action, logs audit events, and updates outcomes. |
| `GET` | `/api/audit` | Global immutable audit ledger with search and pagination. |
| `GET` | `/rag/evaluation` | Real-time RAG evaluation benchmark scores (Accuracy, Grounding, Faithfulness). |

---

## 8. Automated Test Suite & Verification

The test suite thoroughly exercises counterfactual strategy scoring, deterministic policy overrides, all API endpoints, and all 5 Buildathon demo scenarios:

```powershell
cd backend
uv run pytest tests/test_recovery.py -v
```

**Results (14 / 14 Tests Passing in 2.99s):**
```
tests/test_recovery.py::test_counterfactual_strategies_generation PASSED [  7%]
tests/test_recovery.py::test_policy_engine_fraud_override PASSED         [ 14%]
tests/test_recovery.py::test_policy_engine_retry_limit PASSED            [ 21%]
tests/test_recovery.py::test_policy_engine_duplicate_debit PASSED        [ 28%]
tests/test_recovery.py::test_api_dashboard_metrics PASSED                [ 35%]
tests/test_recovery.py::test_api_transactions_list PASSED                [ 42%]
tests/test_recovery.py::test_api_transaction_detail PASSED               [ 50%]
tests/test_recovery.py::test_api_recovery_evaluate PASSED                [ 57%]
tests/test_recovery.py::test_api_policy_check PASSED                     [ 64%]
tests/test_recovery.py::test_demo_scenario_1_easy_recovery PASSED        [ 71%]
tests/test_recovery.py::test_demo_scenario_2_alternate_payment PASSED    [ 78%]
tests/test_recovery.py::test_demo_scenario_3_customer_nudge PASSED       [ 85%]
tests/test_recovery.py::test_demo_scenario_4_high_fraud_risk PASSED      [ 92%]
tests/test_recovery.py::test_demo_scenario_5_unfavorable_recovery PASSED [100%]

======================== 14 passed in 2.99s ========================
```

---

## 9. Quick Start Guide

### Prerequisites
- Python 3.11+
- Node.js 18+
- [uv](https://github.com/astral-sh/uv) (recommended Python package manager)

### 1. Backend Setup
```powershell
cd backend
uv sync
uv run python database.py
uv run python -m uvicorn main:app --reload --port 8000
# Or if your .venv is already activated:
# python -m uvicorn main:app --reload --port 8000
```
- API Health Check: [http://localhost:8000/health](http://localhost:8000/health)
- Interactive OpenAPI Swagger Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

### 2. Frontend Setup
```powershell
cd frontend/recoverai-dashboard
npm install
npm run dev -- --port 5173
```
- Web Application Dashboard: [http://localhost:5173](http://localhost:5173)

---

## 10. Hackathon Pitch Script (For Judges)

When demonstrating RecoverAI to Razorpay hackathon judges:

1. **The Hook**:  
   *"Every payment gateway has a retry script. But retry scripts are blind — they don't know who the customer is, they don't know the fraud risk, and they don't know when to stop. RecoverAI is not a retry script; it is an autonomous, context-aware decision engine."*
2. **Show Scenario 2 (`TX002`) — The Counterfactual Matrix**:  
   *"Look at this declined card. A traditional system retries it and fails. RecoverAI evaluates all 5 strategies side-by-side, proves that Alternate Payment has an 84% probability of recovery and a net score of ₹7,102, and generates an alternate checkout link."*
3. **Show Scenario 4 (`TX003`) — Deterministic Safety**:  
   *"Here is a ₹75,000 transaction with 76% fraud risk. The AI might see a big ticket, but our deterministic Policy Engine triggers a hard block. Policy ALWAYS wins over AI."*
4. **Show Scenario 5 (`TX004`) — Knowing When to Stop**:  
   *"This transaction has failed twice. RecoverAI executes a STOP. Knowing when NOT to retry is an economic superpower that saves merchants from fee bleed and customer churn."*
5. **Show Live Database & Learning Loop**:  
   *"Every single decision is logged to our 9-table Supabase database, and empirical win-rates continuously refine future recovery probability estimates."*

---

## 11. Project Directory Layout

```
recoverai/
├── README.md                          # Comprehensive project documentation
├── PROJECT_OVERVIEW.md                # Architectural specification & pitch script
├── backend/
│   ├── data/policies/                 # 4 Operational RAG policy documents
│   │   ├── abandonment_policy.txt
│   │   ├── card_policy.txt
│   │   ├── escalation_policy.txt
│   │   └── upi_policy.txt
│   ├── database.py                    # 9-Table SQLAlchemy ORM (Supabase PostgreSQL + SQLite)
│   ├── guardrails/rules.py            # Safety policy rules & priority checks
│   ├── main.py                        # FastAPI entry point, CORS, lifespan seeding
│   ├── ml/
│   │   ├── evaluate_model.py          # PaySim ML inference & feature extraction logic
│   │   ├── fraud_model.pkl            # Pre-trained PaySim RandomForestClassifier
│   │   └── train_model.py             # Model training & ROC-AUC verification script
│   ├── routes/
│   │   ├── api.py                     # Primary /api/* REST router
│   │   ├── dashboard.py               # Dashboard metrics router
│   │   ├── evaluation.py              # RAG benchmark evaluation router
│   │   └── transactions.py            # Transactions router
│   ├── services/
│   │   ├── agent.py                   # Structured AI decision agent
│   │   ├── context_analyzer.py        # Failure taxonomy & customer profiling
│   │   ├── counterfactual.py          # 5-Strategy counterfactual evaluation matrix
│   │   ├── feedback.py                # Empirical win-rate calibration loop
│   │   ├── policy_engine.py           # Deterministic safety gatekeeper
│   │   ├── rag.py                     # RAG policy retrieval & benchmark engine
│   │   └── recovery.py                # Pipeline execution & transaction analysis
│   ├── supabase_schema.sql            # PostgreSQL schema script for Supabase
│   └── tests/
│       └── test_recovery.py           # 14 unit & integration tests
└── frontend/
    └── recoverai-dashboard/           # React 19 + Vite + Tailwind CSS dashboard
        ├── src/
        │   ├── components/            # Navbar, ActionBadge, StatusBadge
        │   ├── pages/
        │   │   ├── Dashboard.jsx      # Executive metrics & 1-click scenario triggers
        │   │   ├── Transactions.jsx   # Paginated transaction ledger
        │   │   ├── TransactionDetails.jsx # 5-way counterfactual matrix & execution
        │   │   ├── AuditLogs.jsx      # Immutable compliance audit stream
        │   │   ├── AgentActivity.jsx  # Real-time recovery activity view
        │   │   └── RagEvaluation.jsx  # Live RAG benchmark scorecards
        │   ├── services/api.js        # Axios API client
        │   ├── App.jsx                # Router & navigation
        │   └── index.css              # Custom styling tokens
        ├── package.json
        └── vite.config.js
```
