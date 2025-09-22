from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import HTTPException, status

from pymongo import ReturnDocument

from ..db import get_database
from ..models import AssistedOnboardingRequest, OnboardingProgress
from ..utils.notifications import broadcast_nudges


db = get_database().db


async def track_progress(merchant_email: str) -> dict[str, Any]:
    progress = await db.onboarding_progress.find_one({"merchant_email": merchant_email})
    if not progress:
        progress_model = OnboardingProgress(merchant_email=merchant_email)
        await db.onboarding_progress.insert_one(progress_model.dict(by_alias=True))
        return progress_model.dict()
    return OnboardingProgress(**progress).dict()


async def update_checklist(merchant_email: str, item: str, completed: bool) -> dict[str, Any]:
    allowed = {"account_created", "kyc_submitted", "bank_verified", "business_verified", "assisted_visit"}
    if item not in allowed:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid checklist item")

    updated = await db.onboarding_progress.find_one_and_update(
        {"merchant_email": merchant_email},
        {
            "$set": {
                f"checklist_items.{item}": completed,
                "last_updated_at": datetime.utcnow(),
            }
        },
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )
    return OnboardingProgress(**updated).dict()


async def request_assistance(payload: AssistedOnboardingRequest) -> dict[str, Any]:
    assistance_record = payload.dict()
    assistance_record["status"] = "scheduled"
    await db.assisted_onboarding.insert_one(assistance_record)
    await update_checklist(payload.merchant_email, "assisted_visit", False)
    broadcast_nudges(
        [payload.merchant_email],
        f"Your {payload.assistance_mode} onboarding is scheduled. Our team will contact you shortly.",
    )
    return {"message": "Assistance scheduled", "details": assistance_record}


async def generate_nudges() -> dict[str, Any]:
    cursor = db.onboarding_progress.find({})
    pending = []
    async for record in cursor:
        model = OnboardingProgress(**record)
        incomplete = [item for item, done in model.checklist_items.items() if not done]
        if incomplete:
            nudge_message = f"Pending steps: {', '.join(incomplete)}"
            pending.append({"merchant_email": model.merchant_email, "nudge": nudge_message})
    broadcast_nudges([p["merchant_email"] for p in pending], "Please complete your onboarding steps.")
    return {"nudges": pending}
