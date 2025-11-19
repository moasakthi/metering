"""Configuration management for Metering Annotator."""

import os
from typing import Optional


class Config:
    """Configuration for metering annotator."""
    
    def __init__(self):
        self.api_url = os.getenv("METERING_API_URL", "http://localhost:8000")
        self.api_key = os.getenv("METERING_API_KEY", "")
        self.transport_mode = os.getenv("METERING_TRANSPORT_MODE", "async")
        self.batch_size = int(os.getenv("METERING_BATCH_SIZE", "100"))
        self.batch_interval_seconds = int(os.getenv("METERING_BATCH_INTERVAL_SECONDS", "5"))
        self.retry_max_attempts = int(os.getenv("METERING_RETRY_MAX_ATTEMPTS", "3"))
        self.timeout = int(os.getenv("METERING_TIMEOUT", "5"))


config = Config()

