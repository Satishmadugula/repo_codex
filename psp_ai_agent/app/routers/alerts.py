from fastapi import APIRouter

from ..services import alert_service

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.post("/merchant")
async def merchant_alert(merchant_email: str, message: str, channel: str = "email"):
    return await alert_service.notify_merchant(merchant_email, message, channel)


@router.post("/internal")
async def internal_alert(message: str, severity: str = "info"):
    return await alert_service.alert_internal_team(message, severity)


@router.post("/anomaly")
async def anomaly(merchant_email: str, transaction_amount: float):
    return await alert_service.anomaly_detection(merchant_email, transaction_amount)
