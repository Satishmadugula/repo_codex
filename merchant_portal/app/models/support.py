from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class SupportTicket(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    merchant_email: str
    question: str
    language: str = "en"
    status: str = "open"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    escalation_requested: bool = False
    resolution_notes: list[str] = Field(default_factory=list)


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatSession(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    merchant_email: str
    language: str
    messages: list[ChatMessage] = Field(default_factory=list)
    last_activity_at: datetime = Field(default_factory=datetime.utcnow)
