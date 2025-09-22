from fastapi import APIRouter

from ..models import AssistedOnboardingRequest
from ..services import onboarding_service

router = APIRouter(prefix="/onboarding", tags=["Onboarding"])


@router.get("/progress")
async def progress(merchant_email: str):
    return await onboarding_service.track_progress(merchant_email)


@router.post("/update-checklist")
async def update_checklist(merchant_email: str, item: str, completed: bool):
    return await onboarding_service.update_checklist(merchant_email, item, completed)


@router.post("/assistance")
async def request_assistance(payload: AssistedOnboardingRequest):
    return await onboarding_service.request_assistance(payload)


@router.post("/nudges")
async def generate_nudges():
    return await onboarding_service.generate_nudges()
