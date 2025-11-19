"""API key validation and security utilities."""

import hashlib
from typing import Optional
from fastapi import HTTPException, Security, Depends
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session
from app.models.database import MeteringAPIKey
from app.core.database import get_db

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def hash_api_key(api_key: str, algorithm: str = "sha256") -> str:
    """Hash an API key."""
    if algorithm == "sha256":
        return hashlib.sha256(api_key.encode()).hexdigest()
    raise ValueError(f"Unsupported algorithm: {algorithm}")


def validate_api_key(
    api_key: Optional[str] = Security(api_key_header),
    db: Session = Depends(get_db)
) -> str:
    """Validate API key from header."""
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="API key is required"
        )
    
    # Hash the provided key
    key_hash = hash_api_key(api_key)
    
    # Check if key exists and is active
    db_key = db.query(MeteringAPIKey).filter(
        MeteringAPIKey.key_hash == key_hash,
        MeteringAPIKey.is_active == True
    ).first()
    
    if not db_key:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )
    
    # Update last used timestamp
    from datetime import datetime
    db_key.last_used_at = datetime.utcnow()
    db.commit()
    
    return api_key

