from __future__ import annotations

from datetime import datetime
from typing import Any

from bson import ObjectId
from fastapi import HTTPException, status

from ..db import get_database
from ..models import ChatMessage, ChatSession, SupportTicket
from ..utils.notifications import send_email_notification


db = get_database().db


DEFAULT_FAQS = [
    {"question": "What documents are required?", "answer": "Refer to the entity-specific checklist in the KYC section."},
    {"question": "How long does verification take?", "answer": "Bank and KYC verification usually completes within 24 hours."},
]


async def create_ticket(ticket: SupportTicket) -> dict[str, Any]:
    ticket.updated_at = datetime.utcnow()
    result = await db.support_tickets.insert_one(ticket.dict(by_alias=True))
    send_email_notification(ticket.merchant_email, "Support ticket created", "Our team will respond shortly.")
    return {"ticket_id": str(result.inserted_id)}


async def update_ticket(ticket_id: str, resolution_note: str) -> dict[str, Any]:
    ticket = await db.support_tickets.find_one_and_update(
        {"_id": ObjectId(ticket_id)},
        {
            "$set": {"status": "resolved", "updated_at": datetime.utcnow()},
            "$push": {"resolution_notes": resolution_note},
        },
    )
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    return {"message": "Ticket resolved"}


async def fetch_faqs() -> dict[str, Any]:
    return {"faqs": DEFAULT_FAQS}


async def start_chat_session(merchant_email: str, language: str) -> dict[str, Any]:
    session = ChatSession(merchant_email=merchant_email, language=language)
    result = await db.support_chats.insert_one(session.dict(by_alias=True))
    return {"session_id": str(result.inserted_id)}


async def post_chat_message(session_id: str, message: ChatMessage) -> dict[str, Any]:
    update_result = await db.support_chats.update_one(
        {"_id": ObjectId(session_id)},
        {
            "$push": {"messages": message.dict()},
            "$set": {"last_activity_at": datetime.utcnow()},
        },
    )
    if update_result.modified_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat session not found")
    response = {
        "reply": "Our AI assistant will reach out with more details shortly.",
        "language": message.role,
    }
    return response
