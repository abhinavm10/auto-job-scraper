"""
Application configuration using pydantic-settings.

Reads configuration from environment variables and .env file.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    DATABASE_URL: str = "sqlite:///./auto_applier.db"
    GEMINI_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    
    # Notification settings (placeholder)
    EMAIL_SMTP_SERVER: Optional[str] = None
    EMAIL_PORT: int = 587
    EMAIL_USERNAME: Optional[str] = None
    EMAIL_PASSWORD: Optional[str] = None

    class Config:
        env_file = ".env"


settings = Settings()
