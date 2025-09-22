from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import HTTPException, UploadFile, status

from ..db import get_database
from ..models import DocumentExtraction, RejectionFeedback
from ..utils.ollama import run_ocr


db = get_database().db


async def process_document(merchant_email: str, document_type: str, file: UploadFile) -> dict[str, Any]:
    contents = await file.read()
    upload_dir = Path("psp_uploads")
    upload_dir.mkdir(parents=True, exist_ok=True)
    storage_path = upload_dir / f"{merchant_email.replace('@', '_')}_{document_type}.{file.filename.split('.')[-1]}"
    with open(storage_path, "wb") as out:
        out.write(contents)

    try:
        ocr_result = await run_ocr(str(storage_path), document_type)
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    try:
        extracted = json.loads(ocr_result.get("extracted_text", "{}"))
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Invalid OCR response") from exc

    document = DocumentExtraction(
        merchant_email=merchant_email,
        document_type=document_type,
        extracted_data=extracted,
        score=_score_document(extracted),
        status="auto_approved" if extracted else "needs_review",
    )
    await db.document_extractions.insert_one(document.dict(by_alias=True))
    return {"extracted_data": extracted, "score": document.score, "status": document.status}


async def rejection_feedback(feedback: RejectionFeedback) -> dict[str, Any]:
    await db.document_extractions.update_one(
        {"merchant_email": feedback.merchant_email, "document_type": feedback.document_type},
        {
            "$set": {
                "status": "rejected",
                "rejection_reason": feedback.reason,
                "suggestions": feedback.suggestions,
            }
        },
        upsert=True,
    )
    return {"message": "Feedback recorded"}


def _score_document(extracted: dict[str, Any]) -> float:
    if not extracted:
        return 0.0
    coverage = len([v for v in extracted.values() if v])
    score = min(1.0, coverage / max(len(extracted), 1))
    return round(score * 100, 2)
