from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from ..db import get_database
from ..models import ComplianceTask, RekycSchedule


db = get_database().db


async def schedule_cpv(merchant_email: str, address: str) -> dict[str, Any]:
    task = ComplianceTask(
        merchant_email=merchant_email,
        task_type="cpv",
        metadata={"address": address},
        due_date=datetime.utcnow() + timedelta(days=2),
    )
    await db.compliance_tasks.insert_one(task.dict(by_alias=True))
    return {"task": task.dict()}


async def verify_ovd(merchant_email: str, document_type: str, reference_number: str) -> dict[str, Any]:
    result = await db.compliance_tasks.update_one(
        {
            "merchant_email": merchant_email,
            "task_type": "ovd_verification",
            "metadata.document_type": document_type,
        },
        {
            "$set": {
                "status": "completed",
                "metadata.reference_number": reference_number,
                "updated_at": datetime.utcnow(),
            }
        },
        upsert=True,
    )
    return {"updated": result.modified_count > 0}


async def manage_rekyc_cycle(merchant_email: str, completed_at: datetime) -> dict[str, Any]:
    schedule = RekycSchedule(
        merchant_email=merchant_email,
        next_due_date=completed_at + timedelta(days=365),
        last_completed_at=completed_at,
        regulatory_reference="RBI Master Direction - KYC",
    )
    await db.rekyc_schedules.update_one(
        {"merchant_email": merchant_email},
        {"$set": schedule.dict()},
        upsert=True,
    )
    return schedule.dict()


async def compliance_updates() -> dict[str, Any]:
    cursor = db.rekyc_schedules.find({})
    updates = [schedule async for schedule in cursor]
    return {"rekyc_schedules": updates}
