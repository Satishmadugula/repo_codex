from __future__ import annotations

import base64
from pathlib import Path
from typing import Any

import httpx

from ..config import get_settings


async def run_ocr(image_path: str, document_type: str) -> dict[str, Any]:
    settings = get_settings()
    url = f"{settings.ollama_base_url}/api/generate"
    encoded = base64.b64encode(Path(image_path).read_bytes()).decode("utf-8")
    prompt = (
        "You are an OCR assistant for merchant KYC. Extract key fields from the provided "
        f"{document_type} image encoded in base64. Respond in JSON with keys and values.\n"
        "BASE64_IMAGE::" + encoded
    )
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                url,
                json={"model": settings.ocr_model, "prompt": prompt, "stream": False},
            )
            response.raise_for_status()
            data = response.json()
    except httpx.RequestError as exc:  # pragma: no cover - network heavy
        raise RuntimeError(f"Failed to reach Ollama service: {exc}") from exc
    text = data.get("response", "{}")
    return {"raw_response": data, "extracted_text": text}
