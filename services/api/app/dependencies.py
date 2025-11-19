"""FastAPI dependencies."""

from fastapi import Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import validate_api_key


def get_database() -> Session:
    """Dependency for database session."""
    return Depends(get_db)


def get_api_key() -> str:
    """Dependency for API key validation."""
    return Depends(validate_api_key)

