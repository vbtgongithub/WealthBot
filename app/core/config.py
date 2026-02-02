"""
WealthBot Configuration Module
==============================
Centralized configuration management using Pydantic Settings.
"""

from functools import lru_cache
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    Follows 12-factor app methodology for configuration management.
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    # -------------------------------------------------------------------------
    # Application Settings
    # -------------------------------------------------------------------------
    app_env: str = Field(default="development", description="Application environment")
    debug: bool = Field(default=False, description="Debug mode flag")
    log_level: str = Field(default="INFO", description="Logging level")
    
    # -------------------------------------------------------------------------
    # Database Configuration
    # -------------------------------------------------------------------------
    database_url: str = Field(
        default="postgresql+asyncpg://wealthbot_user:wealthbot_secret@localhost:5432/wealthbot_db",
        description="Async PostgreSQL connection string",
    )
    db_pool_size: int = Field(default=5, description="Database connection pool size")
    db_max_overflow: int = Field(default=10, description="Max overflow connections")
    db_pool_timeout: int = Field(default=30, description="Pool connection timeout")
    
    # -------------------------------------------------------------------------
    # Security Settings
    # -------------------------------------------------------------------------
    secret_key: str = Field(
        default="dev-secret-key-change-in-production",
        description="Secret key for JWT encoding",
    )
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(
        default=30,
        description="Access token expiration time in minutes",
    )
    
    # -------------------------------------------------------------------------
    # CORS Configuration
    # -------------------------------------------------------------------------
    allowed_origins: str = Field(
        default="http://localhost:3000,http://localhost:8000",
        description="Comma-separated list of allowed CORS origins",
    )
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """Parse allowed origins string into a list."""
        return [origin.strip() for origin in self.allowed_origins.split(",")]
    
    # -------------------------------------------------------------------------
    # ML Model Configuration
    # -------------------------------------------------------------------------
    model_path: str = Field(
        default="./ml/models/xgboost_spending_model.pkl",
        description="Path to the XGBoost model artifact",
    )
    transformer_model_name: str = Field(
        default="distilbert-base-uncased",
        description="Hugging Face transformer model name",
    )
    
    # -------------------------------------------------------------------------
    # PII Protection (GDPR/SOC 2 Compliance)
    # -------------------------------------------------------------------------
    enable_pii_masking: bool = Field(
        default=True,
        description="Enable PII masking in logs and responses",
    )
    data_retention_days: int = Field(
        default=365,
        description="Data retention period in days",
    )
    encryption_key: str = Field(
        default="",
        description="Encryption key for sensitive data",
    )
    
    # -------------------------------------------------------------------------
    # Validators
    # -------------------------------------------------------------------------
    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Ensure log level is valid."""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        upper_v = v.upper()
        if upper_v not in valid_levels:
            raise ValueError(f"Invalid log level: {v}. Must be one of {valid_levels}")
        return upper_v
    
    @field_validator("app_env")
    @classmethod
    def validate_app_env(cls, v: str) -> str:
        """Ensure app environment is valid."""
        valid_envs = {"development", "staging", "production", "testing"}
        lower_v = v.lower()
        if lower_v not in valid_envs:
            raise ValueError(f"Invalid environment: {v}. Must be one of {valid_envs}")
        return lower_v


@lru_cache
def get_settings() -> Settings:
    """
    Create cached settings instance.
    
    Uses LRU cache to ensure settings are only loaded once.
    """
    return Settings()


# Global settings instance
settings = get_settings()
