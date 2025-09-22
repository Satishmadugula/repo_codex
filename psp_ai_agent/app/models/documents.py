from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class DocumentExtraction(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    merchant_email: str
    document_type: str
    extracted_data: dict[str, str]
    score: float
    status: str = "pending_review"
    rejection_reason: Optional[str] = None
    processed_at: datetime = Field(default_factory=datetime.utcnow)


class RejectionFeedback(BaseModel):
    merchant_email: str
    document_type: str
    reason: str
    suggestions: list[str]
