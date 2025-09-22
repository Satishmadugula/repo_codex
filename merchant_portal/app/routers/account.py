from fastapi import APIRouter

from ..models import DeviceRegistration, LoginRequest, OtpVerification
from ..services import account_service

router = APIRouter(prefix="/accounts", tags=["Account"])


@router.post("/signup")
async def signup(payload: LoginRequest):
    return await account_service.initiate_signup(payload)


@router.post("/verify-otp")
async def verify_otp(payload: OtpVerification):
    return await account_service.verify_otp(payload)


@router.post("/register-device")
async def register_device(payload: DeviceRegistration):
    return await account_service.register_device(payload)


@router.get("/fraud-check")
async def fraud_check(email: str, device_fingerprint: str):
    return await account_service.detect_fraudulent_login(email, device_fingerprint)
