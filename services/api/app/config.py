"""Configuration management for Metering Service."""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    database_url: str = "postgresql://postgres:admin@localhost:5432/postgres"
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    redis_pool_size: int = 10
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_key_hash_algorithm: str = "sha256"
    
    # Database Connection Pool
    db_pool_size: int = 20
    db_max_overflow: int = 10
    
    # Aggregation
    aggregation_batch_size: int = 1000
    aggregation_interval_seconds: int = 300
    
    # Logging
    log_level: str = "INFO"
    
    # CORS
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

