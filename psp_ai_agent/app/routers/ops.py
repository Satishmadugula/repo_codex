from fastapi import APIRouter

from ..db import get_database

router = APIRouter(prefix="/ops", tags=["Ops Dashboard"])

db = get_database().db


@router.get("/cases")
async def cases():
    low_risk = await db.risk_scores.count_documents({"risk_level": "low"})
    flagged = await db.risk_scores.count_documents({"risk_level": {"$in": ["medium", "high"]}})
    alerts = await db.alerts.count_documents({"severity": "high"})
    return {
        "low_risk_auto_approved": low_risk,
        "flagged_cases": flagged,
        "high_severity_alerts": alerts,
    }


@router.get("/analytics")
async def analytics():
    pipeline = [
        {"$group": {"_id": "$channel", "count": {"$sum": 1}}}
    ]
    alert_distribution = [row async for row in db.alerts.aggregate(pipeline)]
    return {"alert_distribution": alert_distribution}
