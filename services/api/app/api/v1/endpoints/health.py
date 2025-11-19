"""Health check endpoints."""

from fastapi import APIRouter, Depends
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import get_db
from app.core.redis import get_redis
from app.models.schemas import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint."""
    services = {}
    
    # Check database
    try:
        db.execute(text("SELECT 1"))
        services["database"] = "connected"
    except Exception:
        services["database"] = "disconnected"
    
    # Check Redis
    try:
        redis = get_redis()
        redis.ping()
        services["redis"] = "connected"
    except Exception:
        services["redis"] = "disconnected"
    
    status = "healthy" if all(s == "connected" for s in services.values()) else "degraded"
    
    return HealthResponse(
        status=status,
        timestamp=datetime.utcnow(),
        services=services
    )

