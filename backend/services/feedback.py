"""
Feedback & Learning Loop Service for RecoverAI.
Aggregates historical recovery outcomes to calculate empirical win-rates
and dynamically adjust recovery probabilities for future transactions.
"""
from typing import Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import RecoveryOutcome, RecoveryAttempt

# Default baseline win-rates when starting fresh
DEFAULT_STRATEGY_STATS = {
    "SMART_RETRY": {"total": 45, "success": 34, "win_rate": 0.755, "avg_cost": 5.0},
    "ALTERNATE_PAYMENT": {"total": 38, "success": 32, "win_rate": 0.842, "avg_cost": 12.0},
    "CUSTOMER_NUDGE": {"total": 28, "success": 18, "win_rate": 0.643, "avg_cost": 2.5},
    "HUMAN_ESCALATION": {"total": 12, "success": 9, "win_rate": 0.750, "avg_cost": 150.0},
    "STOP": {"total": 15, "success": 0, "win_rate": 0.000, "avg_cost": 0.0},
}

def get_strategy_performance(db: Session) -> Dict[str, Any]:
    """
    Queries actual recorded recovery outcomes to compute live empirical performance.
    """
    stats = {}
    for strat, base in DEFAULT_STRATEGY_STATS.items():
        # Query database for recent attempts
        rows = db.query(RecoveryAttempt).filter(RecoveryAttempt.strategy == strat).all()
        db_total = len(rows)
        db_success = sum(1 for r in rows if r.status == "SUCCESS")

        total = base["total"] + db_total
        success = base["success"] + db_success
        win_rate = round(success / total, 3) if total > 0 else 0.0

        stats[strat] = {
            "total_attempts": total,
            "successful_recoveries": success,
            "win_rate": win_rate,
            "win_rate_percentage": round(win_rate * 100, 1),
            "avg_cost": base["avg_cost"]
        }

    return stats

def get_calibrated_probability(strategy: str, base_prob: float, db: Session) -> float:
    """
    Adjusts the estimated recovery probability using historical empirical performance.
    """
    perf = get_strategy_performance(db)
    strat_stat = perf.get(strategy)
    if not strat_stat or strat_stat["total_attempts"] == 0:
        return base_prob

    historical_rate = strat_stat["win_rate"]
    # Blend: 60% transaction-specific signals, 40% historical strategy win-rate
    blended = round((0.60 * base_prob) + (0.40 * historical_rate), 3)
    return max(0.05, min(0.98, blended))
