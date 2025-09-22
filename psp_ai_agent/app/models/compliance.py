from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ComplianceTask(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    merchant_email: str
    task_type: str
    status: str = "pending"
    assigned_to: Optional[str] = None
    due_date: Optional[datetime] = None
    metadata: dict[str, str] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class RekycSchedule(BaseModel):
    merchant_email: str
    next_due_date: datetime
    last_completed_at: Optional[datetime]
    regulatory_reference: str


class RekycCompletion(BaseModel):
    merchant_email: str
    completed_at: datetime
