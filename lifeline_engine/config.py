"""Configuration management for LifeLine Engine."""
from __future__ import annotations

import functools
import os
from dataclasses import dataclass
from typing import Optional

from pydantic import AnyHttpUrl, BaseSettings, Field, validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    Defaults reflect the MVP deployment targets described in the architecture
    blueprint. The class can be extended to support secrets managers or
    configuration services.
    """

    temporal_address: str = Field(
        "temporal:7233", description="Temporal service address accessible to workers."
    )
    database_url: str = Field(
        ..., description="SQLAlchemy-compatible URL for the metadata database."
    )
    object_storage_bucket: str = Field(
        ..., description="S3 bucket used for design deliverables."
    )
    object_storage_region: str = Field("ap-northeast-2", description="AWS region")
    kafka_bootstrap_servers: str = Field(
        ..., description="Kafka cluster used for event ingestion and notifications."
    )
    observability_endpoint: Optional[AnyHttpUrl] = Field(
        None, description="OTLP collector endpoint for metrics and traces."
    )
    feature_store_table: str = Field(
        "lifeline_engine.features", description="Feature store table identifier."
    )
    model_registry_uri: AnyHttpUrl = Field(
        ..., description="MLflow tracking URI for model versioning."
    )
    cache_ttl_seconds: int = Field(3600, description="TTL for cached API responses")
    environment: str = Field(
        "development", description="Deployment environment (dev/staging/prod)."
    )

    class Config:
        env_prefix = "LIFELINE_"
        case_sensitive = False

    @validator("database_url", pre=True)
    def _validate_database_url(cls, value: str) -> str:
        if value.startswith("sqlite:///"):
            raise ValueError("SQLite is not supported for production workflows")
        return value


@functools.lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached settings instance."""

    return Settings()


@dataclass
class TemporalRetryPolicy:
    """Standard retry policy applied to Temporal activities."""

    initial_interval_seconds: float = 5.0
    backoff_coefficient: float = 2.0
    maximum_interval_seconds: float = 60.0
    maximum_attempts: int = 5


DEFAULT_RETRY_POLICY = TemporalRetryPolicy()
