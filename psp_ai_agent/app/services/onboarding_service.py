from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from ..db import get_database
from ..models import CaseSummary, FieldVerificationTask


db = get_database().db


async def assign_field_verification(merchant_email: str, location: str) -> dict[str, Any]:
    task = FieldVerificationTask(
        merchant_email=merchant_email,
        location=location,
        assigned_agent=_select_agent(location),
        instructions=["Capture storefront photos", "Verify signage", "Collect geo-coordinates"],
        scheduled_for=datetime.utcnow() + timedelta(days=1),
    )
    await db.field_tasks.insert_one(task.dict(by_alias=True))
    return task.dict()


async def orchestrate_onboarding(merchant_email: str) -> dict[str, Any]:
    pending_tasks = await db.field_tasks.count_documents({"merchant_email": merchant_email, "status": {"$ne": "completed"}})
    nudges = ["Send WhatsApp onboarding link", "Share multilingual video guide"]
    return {"pending_tasks": pending_tasks, "nudges": nudges}


async def summarize_case(merchant_email: str, risk_level: str, highlights: list[str]) -> dict[str, Any]:
    summary = CaseSummary(merchant_email=merchant_email, risk_level=risk_level, highlights=highlights, next_actions=_next_actions(risk_level))
    await db.case_summaries.update_one(
        {"merchant_email": merchant_email},
        {"$set": summary.dict()},
        upsert=True,
    )
    return summary.dict()


def _select_agent(location: str) -> str:
    return f"agent_{location.lower()}"


def _next_actions(risk_level: str) -> list[str]:
    return {
        "low": ["Auto approve", "Notify merchant"],
        "medium": ["Manual review", "Confirm CPV"],
        "high": ["Escalate to compliance", "Schedule enhanced due diligence"],
    }[risk_level]
