from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class RiskScore(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    merchant_email: str
    base_score: float
    category_modifier: float
    location_modifier: float
    credit_modifier: float
    fraud_signals: list[str] = Field(default_factory=list)
    final_score: float
    risk_level: str
    recommended_actions: list[str]
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TransactionLimit(BaseModel):
    merchant_email: str
    daily_limit: float
    monthly_limit: float
    reserve_percentage: float
    settlement_tier: str


class RiskScoreRequest(BaseModel):
    merchant_email: str
    category: str
    location: str
    credit_score: str
    fraud_flags: list[str] = Field(default_factory=list)
