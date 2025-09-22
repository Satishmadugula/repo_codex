from __future__ import annotations

from difflib import SequenceMatcher
from typing import Any

from ..db import get_database


db = get_database().db

BLOCKLIST = {"fraud@example.com", "bad-merchant"}
SANCTIONED_ENTITIES = {"Sanctioned Corp"}


async def fraud_checks(merchant_email: str, business_name: str, pan: str) -> dict[str, Any]:
    results: dict[str, Any] = {"blocklisted": merchant_email in BLOCKLIST or business_name in BLOCKLIST}
    results["sanction_hit"] = business_name in SANCTIONED_ENTITIES
    duplicates = await _find_duplicates(business_name)
    results["potential_duplicates"] = duplicates
    results["fraud_score"] = 100 if results["blocklisted"] or results["sanction_hit"] else max(0, 50 - len(duplicates) * 10)
    return results


async def _find_duplicates(business_name: str) -> list[str]:
    cursor = db.risk_scores.find({}, {"merchant_email": 1, "recommended_actions": 1})
    duplicates = []
    async for record in cursor:
        match_ratio = SequenceMatcher(a=record.get("merchant_email", ""), b=business_name).ratio()
        if match_ratio > 0.8:
            duplicates.append(record.get("merchant_email"))
    return duplicates
