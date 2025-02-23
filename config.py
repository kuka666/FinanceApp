from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator, ValidationError
from typing import Optional
import re

class Settings(BaseSettings):
    """
    Configuration settings for the Financial Advisor API.
    Loaded from environment variables or a .env file.
    """
    APP_NAME: str = "Finance App"
    DEBUG: bool = False  
    DATABASE_URL: str = "sqlite:///./sqlite.db"  
    
    # Redis configuration
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None  # Optional password
    
    # Rate limiting configuration
    RATE_LIMIT: str = "5/minute"  

    @field_validator("RATE_LIMIT")
    @classmethod
    def validate_rate_limit(cls, v: str) -> str:
        """
        Validate that RATE_LIMIT follows the format 'number/time_unit'.
        Supported units: minute, hour, day.
        """
        pattern = r"^\d+/(minute|hour|day)$"
        if not re.match(pattern, v):
            raise ValueError(
                "RATE_LIMIT must be in the format 'number/time_unit' (e.g., '5/minute', '100/hour')"
            )
        return v

    @field_validator("REDIS_PORT")
    @classmethod
    def validate_redis_port(cls, v: int) -> int:
        """
        Ensure REDIS_PORT is a valid port number (1-65535).
        """
        if not 1 <= v <= 65535:
            raise ValueError("REDIS_PORT must be between 1 and 65535")
        return v

    @field_validator("REDIS_DB")
    @classmethod
    def validate_redis_db(cls, v: int) -> int:
        """
        Ensure REDIS_DB is a valid Redis database number (0-15 by default).
        """
        if not 0 <= v <= 15:
            raise ValueError("REDIS_DB must be between 0 and 15")
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,  # Allow flexibility in env var casing (e.g., "debug" or "DEBUG")
    )

# Instantiate settings
try:
    settings = Settings()
except ValidationError as e:
    raise RuntimeError(f"Configuration error: {e}") from e