"""Application configuration using Pydantic Settings."""

from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # App
    APP_NAME: str = "AI-Powered Forum API"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    # Firebase
    FIREBASE_CREDENTIALS_PATH: str = "serviceAccountKey.json"

    # OpenAI (for LangChain)
    OPENAI_API_KEY: str = ""

    # Database (future)
    DATABASE_URL: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
