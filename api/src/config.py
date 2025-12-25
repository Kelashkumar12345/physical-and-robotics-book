"""Application configuration using pydantic-settings."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # OpenAI Configuration
    openai_api_key: str

    # Qdrant Configuration
    qdrant_url: str
    qdrant_api_key: str
    qdrant_collection: str = "book_content"

    # CORS Configuration
    cors_origins: str = "http://localhost:3000"

    # Session Configuration
    session_secret: str = "dev-secret-change-in-production"
    rate_limit_per_session: int = 50

    # Debug mode
    debug: bool = False

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",")]


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
