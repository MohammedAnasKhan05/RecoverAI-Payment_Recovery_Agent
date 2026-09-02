# RecoverAI Dashboard — Frontend Application

> Modern fintech revenue recovery interface built with **React 19**, **Vite**, **Tailwind CSS**, and **Recharts** for Razorpay Buildathon Track 3.

---

## Overview

The RecoverAI Dashboard gives finance, risk, and merchant operations teams an interactive, real-time command center for autonomous revenue recovery:

1. **Executive Dashboard (`/`)**: High-level financial KPIs (Revenue at Risk, Recoverable Volume, Operational Savings), strategy performance distributions, and 1-click Buildathon quick-launch demo scenario buttons.
2. **Transactions Ledger (`/transactions`)**: Live-filtered, paginated ledger tracking transaction statuses (`AT_RISK`, `RECOVERED`, `FAILED`, `ESCALATED`, `STOPPED`) and payment methods (UPI, Cards, Netbanking).
3. **Deep-Dive Transaction View (`/transactions/:id`)**:
   - Complete failure context, customer relationship tier, and spend intelligence.
   - Side-by-side **5-Strategy Counterfactual Analysis Matrix** with expected recovery economics and penalty breakdowns.
   - Transparent AI structured reasoning and deterministic safety policy validation badges.
   - 1-click **Execute Recovery** pipeline triggering action simulation.
   - Immutable audit trail timeline.
4. **Agent Activity & Audit Trail (`/audit`)**: Real-time stream of all automated agent decisions, policy evaluations, and recovery dispatches.
5. **RAG Policy Evaluation Suite (`/rag-evaluation`)**: Interactive benchmark viewer displaying 15 dynamic queries across UPI, Card, Abandonment, and Escalation policies with live retrieval accuracy, context grounding, and faithfulness scores.

---

## Tech Stack

- **Framework**: React 19
- **Tooling & Bundler**: Vite 6
- **Styling**: Tailwind CSS 3.4 (Razorpay Fintech theme: `#0C6BF5`, `#0C2340`)
- **Visualizations**: Recharts
- **Icons**: Lucide React
- **Linter**: Oxlint

---

## Local Setup

### 1. Install Dependencies
```bash
npm install
```

### 2. Environment Configuration (Optional)
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Default configuration:
```env
VITE_API_URL=http://localhost:8000
```

### 3. Start Development Server
```bash
npm run dev -- --port 5173
```
Open [http://localhost:5173](http://localhost:5173) in your browser.

### 4. Build for Production
```bash
npm run build
```
