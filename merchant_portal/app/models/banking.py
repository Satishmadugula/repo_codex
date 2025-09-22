from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class BankVerification(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    merchant_email: str
    account_number: str
    ifsc: str
    verification_status: str = "initiated"
    penny_drop_reference: Optional[str] = None
    account_name: Optional[str] = None
    matched: Optional[bool] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class BusinessVerification(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    merchant_email: str
    pan: Optional[str] = None
    gstin: Optional[str] = None
    website_url: Optional[str] = None
    license_document_path: Optional[str] = None
    verification_status: str = "pending"
    compliance_notes: list[str] = Field(default_factory=list)
    last_checked_at: datetime = Field(default_factory=datetime.utcnow)
