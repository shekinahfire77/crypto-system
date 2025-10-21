"""Settings management using Pydantic."""

import os
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Keys (read from environment, never logged or printed)
    coingecko_api_key: str
    cmc_api_key: str
    cmc_dex_api_key: str

    # Rate Limits (calls per minute)
    coingecko_rate_limit: int = 15
    cmc_rate_limit: int = 15
    cmc_dex_rate_limit: int = 50

    # Database Configuration
    db_host: str = "postgres"
    db_port: int = 5432
    db_name: str = "crypto_market"
    db_user: str = "crypto_user"
    db_password: str = "crypto_pass"

    # Update Intervals (seconds)
    price_update_interval: int = 60
    metadata_update_interval: int = 3600
    sentiment_update_interval: int = 300
    dex_update_interval: int = 120
    exchange_update_interval: int = 7200

    # Logging
    log_level: str = "INFO"
    log_file: str = "/app/logs/crypto-system.log"

    # Feature Flags
    enable_coingecko: bool = True
    enable_cmc: bool = True
    enable_cmc_dex: bool = True
    enable_sentiment_analysis: bool = True

    # Batch Processing
    batch_size: int = 250

    # API Endpoints (shouldn't change, but configurable)
    coingecko_base_url: str = "https://api.coingecko.com/api/v3"
    cmc_base_url: str = "https://pro-api.coinmarketcap.com/v1"
    cmc_dex_base_url: str = "https://pro-api.coinmarketcap.com/dex/v1"

    # Metrics
    metrics_port: int = 8000

    # Retry Configuration
    max_retries: int = 3
    retry_backoff_factor: float = 2.0

    # Connection Pool
    db_pool_size: int = 10
    db_max_overflow: int = 20

    # Circuit Breaker
    circuit_breaker_failure_threshold: int = 5
    circuit_breaker_recovery_timeout: int = 60

    class Config:
        """Pydantic configuration."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    @property
    def database_url(self) -> str:
        """Get database connection URL."""
        return (
            f"postgresql://{self.db_user}:{self.db_password}@"
            f"{self.db_host}:{self.db_port}/{self.db_name}"
        )

    def get_masked_settings(self) -> dict:
        """Get settings with API keys masked for logging."""
        settings_dict = self.model_dump()
        settings_dict["coingecko_api_key"] = "***MASKED***"
        settings_dict["cmc_api_key"] = "***MASKED***"
        settings_dict["cmc_dex_api_key"] = "***MASKED***"
        settings_dict["db_password"] = "***MASKED***"
        return settings_dict


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
