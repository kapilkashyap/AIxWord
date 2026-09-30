"""
Application configuration module.

This module provides centralized configuration management using Pydantic Settings.
All configuration values are loaded from environment variables with sensible defaults.
"""

import logging
import os
from functools import lru_cache
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Configure SSL certificates for corporate environments (Zscaler, etc.)
# This must happen BEFORE any HTTPS requests (OpenAI API calls)
if "SSL_CERT_FILE" not in os.environ:
    try:
        import certifi
        os.environ["SSL_CERT_FILE"] = certifi.where()
        logging.info(f"SSL_CERT_FILE configured: {certifi.where()}")
    except ImportError:
        logging.warning("certifi not installed - SSL certificate verification may fail in corporate environments")


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    All settings can be overridden via environment variables or .env file.
    Required settings will raise validation errors if not provided.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # OpenAI Configuration
    openai_api_key: str = Field(
        ...,
        description="OpenAI API key (required)",
        min_length=1,
    )
    openai_model: str = Field(
        default="gpt-4o-mini",
        description="OpenAI model to use for LLM calls",
    )
    openai_temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Temperature for LLM responses (0.0-2.0)",
    )

    # Grid Configuration
    grid_size: int = Field(
        default=8,
        ge=4,
        le=20,
        description="Default crossword grid size (NxN)",
    )
    max_iterations: int = Field(
        default=50,
        ge=1,
        le=200,
        description="Maximum iterations for puzzle generation",
    )
    min_fill_rate: float = Field(
        default=0.6,
        ge=0.0,
        le=1.0,
        description="Minimum fill rate for valid puzzle (0.0-1.0)",
    )

    # Application Configuration
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )
    cors_origins: str = Field(
        default="http://localhost:5173,http://localhost:3000",
        description="Comma-separated list of allowed CORS origins",
    )
    api_host: str = Field(
        default="0.0.0.0",
        description="API host address",
    )
    api_port: int = Field(
        default=8000,
        ge=1,
        le=65535,
        description="API port number",
    )
    enable_docs: bool = Field(
        default=True,
        description="Enable API documentation endpoints",
    )

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level is a valid logging level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"log_level must be one of {valid_levels}")
        return v_upper

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins string into list."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    def configure_logging(self) -> None:
        """Configure application logging based on settings."""
        logging.basicConfig(
            level=getattr(logging, self.log_level),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.

    This function uses lru_cache to ensure settings are loaded only once
    and reused throughout the application lifecycle.

    Returns:
        Settings: Singleton settings instance
    """
    return Settings()


# Export singleton instance for convenience
settings = get_settings()
