from fastapi import APIRouter, File, UploadFile

from ..models import RejectionFeedback
from ..services import ocr_service

router = APIRouter(prefix="/ocr", tags=["OCR"])


@router.post("/process/{document_type}")
async def process(document_type: str, merchant_email: str, file: UploadFile = File(...)):
    return await ocr_service.process_document(merchant_email, document_type, file)


@router.post("/feedback")
async def feedback(payload: RejectionFeedback):
    return await ocr_service.rejection_feedback(payload)
