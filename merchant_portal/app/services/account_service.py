from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import HTTPException, status
from pymongo import ReturnDocument

from ..db import get_database
from ..models import DeviceRegistration, LoginRequest, MerchantAccount, OtpVerification
from ..utils import notifications, security


db = get_database().db


async def initiate_signup(payload: LoginRequest) -> dict[str, Any]:
    otp = security.generate_otp()
    expiry = security.otp_expiry_time()
    account_data = payload.dict()
    account_data.update({"otp": otp, "otp_expires_at": expiry, "is_verified": False})

    existing = await db.accounts.find_one({"email": payload.email})
    if existing:
        await db.accounts.update_one(
            {"email": payload.email},
            {"$set": {"otp": otp, "otp_expires_at": expiry, "preferred_language": payload.preferred_language}},
        )
    else:
        await db.accounts.insert_one(account_data)

    notifications.send_otp_via_sms(payload.phone_number, otp)
    notifications.send_email_notification(
        payload.email,
        "Complete your onboarding",
        f"Your verification code is {otp}.",
    )

    return {"message": "OTP sent to registered contact methods"}


async def verify_otp(payload: OtpVerification) -> dict[str, Any]:
    account = await db.accounts.find_one({"email": payload.email})
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")

    merchant = MerchantAccount(**account)
    if merchant.otp != payload.otp or not merchant.otp_expires_at or merchant.otp_expires_at < datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired OTP")

    await db.accounts.update_one(
        {"email": payload.email},
        {
            "$set": {
                "is_verified": True,
                "otp": None,
                "otp_expires_at": None,
                "last_login_at": datetime.utcnow(),
            }
        },
    )
    return {"message": "Account verified"}


async def register_device(payload: DeviceRegistration) -> dict[str, Any]:
    fingerprint = security.compute_device_fingerprint(payload.device_fingerprint)
    mfa_token = payload.mfa_token or security.generate_mfa_token()
    merchant = await db.accounts.find_one_and_update(
        {"email": payload.email},
        {
            "$set": {
                "device_fingerprint": fingerprint,
                "last_login_at": datetime.utcnow(),
                "mfa_token": mfa_token,
            }
        },
        return_document=ReturnDocument.AFTER,
    )
    if not merchant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    return {"mfa_token": mfa_token, "message": "Device registered with MFA"}


async def detect_fraudulent_login(email: str, device_fingerprint: str) -> dict[str, Any]:
    merchant = await db.accounts.find_one({"email": email})
    if not merchant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")

    hashed = security.compute_device_fingerprint(device_fingerprint)
    suspicious = merchant.get("device_fingerprint") not in (None, hashed)
    response = {
        "device_trusted": merchant.get("device_fingerprint") == hashed,
        "suspicious_activity": suspicious,
    }
    if suspicious:
        response["actions"] = ["trigger_additional_verification", "notify_fraud_team"]
    return response
