from __future__ import annotations

from typing import Any

from ..db import get_database
from ..models import Alert


db = get_database().db


async def notify_merchant(merchant_email: str, message: str, channel: str = "email") -> dict[str, Any]:
    alert = Alert(merchant_email=merchant_email, message=message, channel=channel, audience="merchant")
    await db.alerts.insert_one(alert.dict(by_alias=True))
    return alert.dict()


async def alert_internal_team(message: str, severity: str = "info") -> dict[str, Any]:
    alert = Alert(merchant_email="psp", message=message, channel="internal", audience="ops", severity=severity)
    await db.alerts.insert_one(alert.dict(by_alias=True))
    return alert.dict()


async def anomaly_detection(merchant_email: str, transaction_amount: float) -> dict[str, Any]:
    if transaction_amount > 100000:
        await notify_merchant(merchant_email, "High value transaction detected. Settlements paused pending review.")
        await alert_internal_team(f"High value transaction for {merchant_email}", severity="high")
        return {"status": "flagged", "actions": ["settlement_paused", "ops_notified"]}
    return {"status": "ok"}
