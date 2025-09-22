from functools import lru_cache
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application configuration using environment variables."""

    app_name: str = Field("Merchant Onboarding Portal", env="MERCHANT_APP_NAME")
    mongodb_uri: str = Field(..., env="MERCHANT_MONGODB_URI")
    database_name: str = Field("merchant_portal", env="MERCHANT_DB_NAME")
    otp_expiry_seconds: int = Field(300, env="MERCHANT_OTP_EXPIRY")
    supported_languages: list[str] = Field(default_factory=lambda: ["en", "hi", "ta", "bn"])

    allowed_origins: list[str] = Field(default_factory=lambda: ["*"])


    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Return cached application settings."""

    return Settings()
