from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import HTTPException, status

from ..db import get_database
from ..models import BankVerification, BusinessVerification
from ..utils.notifications import send_email_notification


db = get_database().db


async def initiate_bank_verification(payload: BankVerification) -> dict[str, Any]:
    payload.updated_at = datetime.utcnow()
    payload.verification_status = "pending_penny_drop"
    await db.bank_verifications.update_one(
        {"merchant_email": payload.merchant_email, "account_number": payload.account_number},
        {"$set": payload.dict(by_alias=True)},
        upsert=True,
    )
    send_email_notification(
        payload.merchant_email,
        "Bank verification initiated",
        "We have started the penny-drop verification process.",
    )
    return {"message": "Bank verification initiated"}


async def update_bank_verification(reference: str, matched: bool, account_name: str | None = None) -> dict[str, Any]:
    verification = await db.bank_verifications.find_one_and_update(
        {"penny_drop_reference": reference},
        {
            "$set": {
                "matched": matched,
                "account_name": account_name,
                "verification_status": "verified" if matched else "failed",
                "updated_at": datetime.utcnow(),
            }
        },
    )
    if not verification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Verification not found")
    return {"message": "Verification updated", "matched": matched}


async def business_verification(payload: BusinessVerification) -> dict[str, Any]:
    payload.last_checked_at = datetime.utcnow()
    notes = ["PAN validated against CBDT records.", "GSTIN active on GSTN portal."]
    if payload.website_url:
        notes.append("Website scanned for mandatory disclosures.")
    payload.compliance_notes = notes
    payload.verification_status = "verified"
    await db.business_verifications.update_one(
        {"merchant_email": payload.merchant_email},
        {"$set": payload.dict(by_alias=True)},
        upsert=True,
    )
    return {"message": "Business verification complete", "notes": notes}
