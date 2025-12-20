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

    # Google AI (Nano Banana Pro)
    GOOGLE_API_KEY: str = ""
    GOOGLE_IMAGE_MODEL: str = "gemini-1.5-pro"  # Default model alias or ID

    # Google Veo 3.1 Video Generation
    GOOGLE_VIDEO_MODEL: str = "veo-3.1-generate-preview"

    # Google Lyria Music Generation
    GOOGLE_MUSIC_MODEL: str = "models/lyria-realtime-exp"

    # AI Rate Limiting
    AI_DAILY_RATE_LIMIT: int = 50

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
