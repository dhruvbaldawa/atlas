"""Configuration management for ATLAS using Pydantic Settings.

This module provides a centralized configuration management system using Pydantic's
BaseSettings class. It loads environment variables from a .env file and validates
them against the expected types.
"""

from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """Database connection settings."""

    host: str = Field(default="localhost", description="Database host")
    port: int = Field(default=5432, description="Database port")
    name: str = Field(default="atlas", description="Database name")
    user: str = Field(default="postgres", description="Database user")
    password: str = Field(default="postgres", description="Database password")

    model_config = SettingsConfigDict(env_prefix="DB_", extra="ignore")

    def get_postgres_uri(self) -> str:
        """Get PostgreSQL connection URI."""
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


class TemporalSettings(BaseSettings):
    """Temporal connection settings."""

    host: str = Field(default="localhost", description="Temporal server host")
    port: int = Field(default=7233, description="Temporal server port")
    namespace: str = Field(default="default", description="Temporal namespace")
    db_name: str = Field(default="temporal", description="Temporal database name")

    model_config = SettingsConfigDict(env_prefix="TEMPORAL_", extra="ignore")

    def get_server_url(self) -> str:
        """Get Temporal server URL."""
        return f"{self.host}:{self.port}"


class APISettings(BaseSettings):
    """API server settings."""

    host: str = Field(default="0.0.0.0", description="API host")
    port: int = Field(default=8000, description="API port")
    debug: bool = Field(default=True, description="Debug mode")

    model_config = SettingsConfigDict(env_prefix="API_", extra="ignore")


class Settings(BaseSettings):
    """Main application settings."""

    # Environment
    env: str = Field(default="development", description="Deployment environment")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Sub-settings
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    temporal: TemporalSettings = Field(default_factory=TemporalSettings)
    api: APISettings = Field(default_factory=APISettings)

    @field_validator("env")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate the environment value."""
        allowed_environments = ["development", "testing", "staging", "production"]
        if v.lower() not in allowed_environments:
            raise ValueError(f"Invalid environment: {v}. Must be one of {allowed_environments}")
        return v.lower()


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
