"""
Application configuration using pydantic-settings.

Reads configuration from environment variables and .env file.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    DATABASE_URL: str = "postgresql://jobapplier:jobapplier123@localhost:5432/auto_applier"
    
    # OpenRouter API Configuration
    OPENROUTER_API_KEY: Optional[str] = None
    OPENROUTER_MODEL: str = "google/gemini-2.0-flash-exp:free"  # Default free model
    
    # Notification settings (placeholder)
    EMAIL_SMTP_SERVER: Optional[str] = None
    EMAIL_PORT: int = 587
    EMAIL_USERNAME: Optional[str] = None
    EMAIL_PASSWORD: Optional[str] = None

    class Config:
        env_file = ".env"


settings = Settings()
