import os
import sys
from functools import lru_cache
from typing import Literal


class Settings:
    """Application configuration."""

    APP_API_KEY: str = os.getenv("APP_API_KEY", "dev-only-key")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    HASH_SALT: str = os.getenv("HASH_SALT", "super-secret-hash-key")
    APP_API_KEY_HASH: str = os.getenv("APP_API_KEY_HASH", "")

    CORS_ORIGINS: str = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://localhost:3000"
    )

    ENVIRONMENT: Literal["development", "production"] = os.getenv(
        "ENVIRONMENT",
        "development"
    )

    API_TITLE: str = "Clinical Data Reconciliation Engine"
    API_VERSION: str = "1.0.0"

    CACHE_ENABLED: bool = os.getenv("CACHE_ENABLED", "true").lower() == "true"
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", "300"))
    CACHE_MAX_SIZE: int = int(os.getenv("CACHE_MAX_SIZE", "100"))

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins string into list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


def validate_settings(settings: Settings) -> None:
    """Validate that required environment variables are set."""
    if not settings.GEMINI_API_KEY:
        print("ERROR: GEMINI_API_KEY environment variable is required but not set", file=sys.stderr)
        print("Please set GEMINI_API_KEY in your .env file or environment", file=sys.stderr)
        sys.exit(1)


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    settings_instance = Settings()
    validate_settings(settings_instance)
    return settings_instance


settings = get_settings()
