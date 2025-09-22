from fastapi import APIRouter

from ..models import BankVerification, BusinessVerification
from ..services import banking_service

router = APIRouter(prefix="/banking", tags=["Banking"])


@router.post("/verify-bank")
async def verify_bank(payload: BankVerification):
    return await banking_service.initiate_bank_verification(payload)


@router.post("/business-verification")
async def verify_business(payload: BusinessVerification):
    return await banking_service.business_verification(payload)


@router.post("/update-bank-status")
async def update_status(reference: str, matched: bool, account_name: str | None = None):
    return await banking_service.update_bank_verification(reference, matched, account_name)
