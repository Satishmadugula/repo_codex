from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class KycChecklistRequest(BaseModel):
    entity_type: str


class KycDocument(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    merchant_email: str
    document_type: str
    file_path: Optional[str] = None
    file_format: str
    status: str = "pending"
    rejection_reason: Optional[str] = None
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated_at: datetime = Field(default_factory=datetime.utcnow)


class KycStatusResponse(BaseModel):
    document_type: str
    status: str
    rejection_reason: Optional[str] = None
