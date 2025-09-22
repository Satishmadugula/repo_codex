from fastapi import APIRouter

from ..models import RekycCompletion
from ..services import compliance_service

router = APIRouter(prefix="/compliance", tags=["Compliance"])


@router.post("/cpv")
async def schedule_cpv(merchant_email: str, address: str):
    return await compliance_service.schedule_cpv(merchant_email, address)


@router.post("/ovd")
async def ovd(merchant_email: str, document_type: str, reference_number: str):
    return await compliance_service.verify_ovd(merchant_email, document_type, reference_number)


@router.post("/rekyc")
async def rekyc(payload: RekycCompletion):
    return await compliance_service.manage_rekyc_cycle(payload.merchant_email, payload.completed_at)


@router.get("/updates")
async def updates():
    return await compliance_service.compliance_updates()
