from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class Alert(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    merchant_email: str
    channel: str
    message: str
    audience: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    severity: str = "info"
    acknowledged: bool = False
