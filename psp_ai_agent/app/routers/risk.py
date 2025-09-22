from fastapi import APIRouter

from ..models import RiskScoreRequest
from ..services import fraud_service, risk_service

router = APIRouter(prefix="/risk", tags=["Risk"])


@router.post("/score")
async def score(payload: RiskScoreRequest):
    return await risk_service.generate_risk_score(
        payload.merchant_email,
        payload.category,
        payload.location,
        payload.credit_score,
        payload.fraud_flags,
    )


@router.get("/dashboard")
async def dashboard():
    return await risk_service.risk_dashboard()


@router.post("/fraud-check")
async def fraud_check(merchant_email: str, business_name: str, pan: str):
    return await fraud_service.fraud_checks(merchant_email, business_name, pan)
