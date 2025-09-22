from fastapi import APIRouter, File, UploadFile

from ..models import KycChecklistRequest
from ..services import kyc_service

router = APIRouter(prefix="/kyc", tags=["KYC"])


@router.post("/checklist")
async def checklist(payload: KycChecklistRequest):
    return await kyc_service.get_checklist(payload)


@router.post("/upload/{document_type}")
async def upload(document_type: str, merchant_email: str, file: UploadFile = File(...)):
    return await kyc_service.upload_document(merchant_email, document_type, file)


@router.get("/status")
async def status(merchant_email: str):
    return await kyc_service.document_status(merchant_email)
