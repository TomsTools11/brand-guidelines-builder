"""
Application configuration using pydantic-settings.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Required
    ANTHROPIC_API_KEY: str

    # Redis configuration
    REDIS_URL: str = "redis://localhost:6379/0"

    # Application settings
    DEBUG: bool = False
    PDF_OUTPUT_DIR: str = "./generated"
    PDF_RETENTION_HOURS: int = 24

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
