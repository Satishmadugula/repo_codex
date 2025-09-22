from __future__ import annotations

import hashlib
import os
import random
import string
from datetime import datetime, timedelta

from ..config import get_settings


def generate_otp(length: int = 6) -> str:
    return "".join(random.choices(string.digits, k=length))


def compute_device_fingerprint(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def otp_expiry_time() -> datetime:
    settings = get_settings()
    return datetime.utcnow() + timedelta(seconds=settings.otp_expiry_seconds)


def generate_mfa_token() -> str:
    return hashlib.sha256(os.urandom(32)).hexdigest()
