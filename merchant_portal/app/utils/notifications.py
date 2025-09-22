from __future__ import annotations

from typing import Iterable


def send_otp_via_sms(phone_number: str, otp: str) -> None:
    # Placeholder for SMS gateway integration
    print(f"Sending OTP {otp} to {phone_number}")


def send_email_notification(email: str, subject: str, message: str) -> None:
    # Placeholder for email service integration
    print(f"Email to {email}: {subject} - {message}")


def broadcast_nudges(recipients: Iterable[str], message: str) -> None:
    for recipient in recipients:
        print(f"Nudge to {recipient}: {message}")
