from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class OnboardingProgress(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    merchant_email: str
    checklist_items: dict[str, bool] = Field(
        default_factory=lambda: {
            "account_created": False,
            "kyc_submitted": False,
            "bank_verified": False,
            "business_verified": False,
            "assisted_visit": False,
        }
    )
    nudges: list[str] = Field(default_factory=list)
    last_updated_at: datetime = Field(default_factory=datetime.utcnow)


class AssistedOnboardingRequest(BaseModel):
    merchant_email: str
    assistance_mode: str
    preferred_time: Optional[str] = None
    location: Optional[str] = None
