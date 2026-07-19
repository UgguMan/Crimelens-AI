"""
CrimeLens AI — Application Configuration
==========================================
Centralized settings management using Pydantic BaseSettings.
All configuration is loaded from environment variables with sensible defaults.
"""

from pathlib import Path
from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    Provides validation, type coercion, and default values for all config.
    """

    # --- Application ---
    app_name: str = Field(default="CrimeLens AI", description="Application display name")
    app_version: str = Field(default="1.0.0", description="Semantic version")
    debug: bool = Field(default=False, description="Enable debug mode")

    # --- MongoDB ---
    mongodb_uri: str = Field(
        default="mongodb://localhost:27017",
        description="MongoDB connection URI",
    )
    db_name: str = Field(default="crimelens", description="MongoDB database name")

    # --- JWT Authentication ---
    jwt_secret: str = Field(
        default="CHANGE_ME_TO_A_RANDOM_64_CHAR_SECRET_KEY",
        description="Secret key for JWT signing — MUST be changed in production",
    )
    jwt_algorithm: str = Field(default="HS256", description="JWT signing algorithm")
    jwt_expiry_hours: int = Field(default=24, description="JWT token expiry in hours")

    # --- Google Gemini API ---
    gemini_api_key: str = Field(default="", description="Google Gemini API key")

    # --- Google Authentication (OAuth) ---
    google_client_id: str = Field(default="", description="Google OAuth2 Client ID")

    # --- File Upload ---
    upload_dir: str = Field(default="uploads", description="Directory for uploaded evidence files")
    export_dir: str = Field(default="exports", description="Directory for generated PDF reports")
    max_upload_size_mb: int = Field(default=50, description="Maximum upload file size in MB")

    # --- CORS ---
    cors_origins: str = Field(
        default="http://localhost:3000,https://*.vercel.app",
        description="Comma-separated list of allowed CORS origins",
    )

    # --- Rate Limiting ---
    rate_limit_per_minute: int = Field(default=60, description="Max API requests per minute per IP")

    # ---- Derived Properties ----

    @property
    def max_upload_size_bytes(self) -> int:
        """Convert MB limit to bytes for file validation."""
        return self.max_upload_size_mb * 1024 * 1024

    @property
    def cors_origin_list(self) -> list[str]:
        """Parse comma-separated CORS origins into a list."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def upload_path(self) -> Path:
        """Resolved upload directory path."""
        path = Path(self.upload_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def export_path(self) -> Path:
        """Resolved export directory path."""
        path = Path(self.export_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore",
    }


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Singleton factory for application settings.
    Cached after first call to avoid re-reading .env on every request.
    """
    return Settings()
