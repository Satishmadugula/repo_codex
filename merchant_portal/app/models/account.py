from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class MerchantAccount(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    email: EmailStr
    phone_number: str
    preferred_language: str = "en"
    otp: Optional[str] = None
    otp_expires_at: Optional[datetime] = None
    is_verified: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login_at: Optional[datetime] = None
    device_fingerprint: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    phone_number: str
    preferred_language: str = "en"


class OtpVerification(BaseModel):
    email: EmailStr
    otp: str


class DeviceRegistration(BaseModel):
    email: EmailStr
    device_fingerprint: str
    mfa_token: Optional[str] = None
