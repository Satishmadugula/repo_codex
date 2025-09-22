from functools import lru_cache
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    app_name: str = Field("AI PSP Agent", env="PSP_APP_NAME")
    mongodb_uri: str = Field(..., env="PSP_MONGODB_URI")
    database_name: str = Field("psp_agent", env="PSP_DB_NAME")
    ollama_base_url: str = Field("http://localhost:11434", env="OLLAMA_BASE_URL")
    ocr_model: str = Field("llava", env="OLLAMA_OCR_MODEL")
    allowed_origins: list[str] = Field(default_factory=lambda: ["*"])
      
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
