from __future__ import annotations

from typing import Any

from ..db import get_database
from ..models import RiskScore, TransactionLimit


db = get_database().db


CATEGORY_WEIGHTS = {
    "electronics": 0.8,
    "gaming": 0.6,
    "pharma": 0.4,
    "education": 0.9,
}

LOCATION_WEIGHTS = {
    "tier1": 1.0,
    "tier2": 0.9,
    "tier3": 0.8,
}

CREDIT_WEIGHTS = {
    "excellent": 1.0,
    "good": 0.9,
    "fair": 0.7,
    "poor": 0.4,
}


async def generate_risk_score(merchant_email: str, category: str, location: str, credit_score: str, fraud_flags: list[str]) -> dict[str, Any]:
    base_score = 70.0
    category_modifier = CATEGORY_WEIGHTS.get(category.lower(), 0.7)
    location_modifier = LOCATION_WEIGHTS.get(location.lower(), 0.85)
    credit_modifier = CREDIT_WEIGHTS.get(credit_score.lower(), 0.6)
    fraud_penalty = max(0, len(fraud_flags) * 5)

    final_score = max(0.0, min(100.0, base_score * category_modifier * location_modifier * credit_modifier - fraud_penalty))
    risk_level = _risk_level(final_score)
    actions = _recommendations(risk_level, fraud_flags)

    record = RiskScore(
        merchant_email=merchant_email,
        base_score=base_score,
        category_modifier=category_modifier,
        location_modifier=location_modifier,
        credit_modifier=credit_modifier,
        fraud_signals=fraud_flags,
        final_score=final_score,
        risk_level=risk_level,
        recommended_actions=actions,
    )
    await db.risk_scores.insert_one(record.dict(by_alias=True))
    limits = _dynamic_limits(record)
    await db.transaction_limits.update_one(
        {"merchant_email": merchant_email},
        {"$set": limits.dict()},
        upsert=True,
    )
    return {"risk": record.dict(), "limits": limits.dict()}


async def risk_dashboard() -> dict[str, Any]:
    pipeline = [
        {
            "$group": {
                "_id": "$risk_level",
                "count": {"$sum": 1},
                "avg_score": {"$avg": "$final_score"},
            }
        }
    ]
    cursor = db.risk_scores.aggregate(pipeline)
    summary = [entry async for entry in cursor]
    return {"summary": summary}


def _risk_level(score: float) -> str:
    if score >= 75:
        return "low"
    if score >= 50:
        return "medium"
    return "high"


def _recommendations(risk_level: str, fraud_flags: list[str]) -> list[str]:
    recommendations = {
        "low": ["auto_approve", "enable_standard_limits"],
        "medium": ["manual_review", "monitor_transactions"],
        "high": ["hold_settlements", "enhanced_due_diligence"],
    }[risk_level]
    if fraud_flags:
        recommendations.append("trigger_fraud_investigation")
    return recommendations


def _dynamic_limits(risk: RiskScore) -> TransactionLimit:
    base_daily = 500000
    multiplier = {"low": 1.2, "medium": 0.8, "high": 0.5}[risk.risk_level]
    reserve = {"low": 0.02, "medium": 0.05, "high": 0.1}[risk.risk_level]
    settlement = {"low": "T+1", "medium": "T+2", "high": "T+4"}[risk.risk_level]
    return TransactionLimit(
        merchant_email=risk.merchant_email,
        daily_limit=base_daily * multiplier,
        monthly_limit=base_daily * multiplier * 30,
        reserve_percentage=reserve,
        settlement_tier=settlement,
    )
