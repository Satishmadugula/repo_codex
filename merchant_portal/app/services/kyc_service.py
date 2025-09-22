from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from fastapi import HTTPException, UploadFile, status

from ..db import get_database
from ..models import KycChecklistRequest, KycDocument


db = get_database().db


ENTITY_CHECKLISTS = {
    "sole_proprietor": ["PAN", "Aadhaar", "Bank Statement"],
    "private_limited": ["PAN", "GSTIN", "MOA", "Bank Statement"],
    "partnership": ["PAN", "Partnership Deed", "GSTIN", "Bank Statement"],
}


async def get_checklist(payload: KycChecklistRequest) -> dict[str, Any]:
    checklist = ENTITY_CHECKLISTS.get(payload.entity_type.lower())
    if not checklist:
        checklist = ["PAN", "GSTIN", "Address Proof"]
    return {
        "entity_type": payload.entity_type,
        "required_documents": checklist,
        "compliance_notes": [
            "Documents must be valid as per RBI KYC Master Directions.",
            "Ensure scans are clear and readable.",
        ],
    }


async def upload_document(merchant_email: str, document_type: str, file: UploadFile) -> dict[str, Any]:
    content = await file.read()
    upload_dir = Path("uploads")
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = upload_dir / f"{merchant_email.replace('@', '_')}_{document_type}.{file.filename.split('.')[-1]}"
    with open(file_path, "wb") as f:
        f.write(content)

    doc = KycDocument(
        merchant_email=merchant_email,
        document_type=document_type,
        file_path=str(file_path),
        file_format=file.content_type or "application/octet-stream",
        status="in_review",
        last_updated_at=datetime.utcnow(),
    )
    await db.kyc_documents.update_one(
        {"merchant_email": merchant_email, "document_type": document_type},
        {"$set": doc.dict(by_alias=True)},
        upsert=True,
    )
    return {"message": "Document uploaded", "path": file_path}


async def list_documents(merchant_email: str) -> list[dict[str, Any]]:
    cursor = db.kyc_documents.find({"merchant_email": merchant_email})
    return [KycDocument(**doc).dict(by_alias=True) async for doc in cursor]


async def document_status(merchant_email: str) -> dict[str, Any]:
    docs = await list_documents(merchant_email)
    if not docs:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No documents found")
    return {"documents": docs}
