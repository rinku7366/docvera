from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """
    Single source of truth for all configuration.
    Why: Rule 6 — no hardcoded values scattered across feature files.
    All values can be overridden via a .env file or environment variables.
    """

    # Security
    SECRET_KEY: str = "change-this-in-production-use-a-long-random-string"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Database
    # SQLite is chosen for portability — no server setup needed for development/viva demo.
    DATABASE_URL: str = "sqlite:///./docvera.db"

    # File uploads
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE_MB: int = 10

    # Only these MIME types are accepted before even opening a file.
    # Why: reject obviously wrong uploads at the HTTP layer before parsing.
    ALLOWED_MIME_TYPES: List[str] = [
        "application/pdf",
        "text/csv",
        "text/plain",
    ]

    # Translation
    # deep-translator uses Google Translate API.
    # Default source language is auto-detect.
    DEFAULT_SOURCE_LANG: str = "auto"
    SUPPORTED_TARGET_LANGS: List[str] = ["en", "hi", "te", "ta"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Module-level singleton — import this everywhere instead of constructing Settings() repeatedly.
settings = Settings()
