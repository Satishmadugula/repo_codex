from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class FieldVerificationTask(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    merchant_email: str
    location: str
    assigned_agent: Optional[str] = None
    status: str = "scheduled"
    instructions: list[str] = Field(default_factory=list)
    scheduled_for: Optional[datetime] = None


class CaseSummary(BaseModel):
    merchant_email: str
    highlights: list[str]
    risk_level: str
    next_actions: list[str]


class CaseSummaryRequest(BaseModel):
    merchant_email: str
    highlights: list[str]
    risk_level: str
