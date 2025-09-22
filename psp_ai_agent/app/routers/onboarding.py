from fastapi import APIRouter

from ..models import CaseSummaryRequest
from ..services import onboarding_service

router = APIRouter(prefix="/onboarding", tags=["Onboarding"])


@router.post("/assign-field")
async def assign(merchant_email: str, location: str):
    return await onboarding_service.assign_field_verification(merchant_email, location)


@router.get("/orchestrate")
async def orchestrate(merchant_email: str):
    return await onboarding_service.orchestrate_onboarding(merchant_email)


@router.post("/summary")
async def summary(payload: CaseSummaryRequest):
    return await onboarding_service.summarize_case(
        payload.merchant_email,
        payload.risk_level,
        payload.highlights,
    )
