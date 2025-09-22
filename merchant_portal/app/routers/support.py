from fastapi import APIRouter

from ..models import ChatMessage, SupportTicket
from ..services import support_service

router = APIRouter(prefix="/support", tags=["Support"])


@router.get("/faqs")
async def faqs():
    return await support_service.fetch_faqs()


@router.post("/ticket")
async def create_ticket(ticket: SupportTicket):
    return await support_service.create_ticket(ticket)


@router.post("/chat/start")
async def start_chat(merchant_email: str, language: str):
    return await support_service.start_chat_session(merchant_email, language)


@router.post("/chat/{session_id}")
async def send_chat(session_id: str, message: ChatMessage):
    return await support_service.post_chat_message(session_id, message)
