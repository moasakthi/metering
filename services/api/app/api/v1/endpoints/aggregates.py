"""Aggregate endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from app.core.database import get_db
from app.core.security import validate_api_key
from app.models.schemas import AggregateFilters, AggregateResponse
from app.services.aggregate_service import AggregateService

router = APIRouter()


@router.get("/aggregates", response_model=AggregateResponse)
async def get_aggregates(
    window_type: str = Query(..., pattern="^(hourly|daily|monthly)$"),
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    tenant_id: Optional[str] = Query(None),
    resource: Optional[str] = Query(None),
    feature: Optional[str] = Query(None),
    group_by: str = Query("resource,feature"),
    db: Session = Depends(get_db),
    api_key: str = Depends(validate_api_key)
):
    """Get aggregated usage statistics."""
    filters = AggregateFilters(
        tenant_id=tenant_id,
        resource=resource,
        feature=feature,
        window_type=window_type,
        start_date=start_date,
        end_date=end_date,
        group_by=group_by
    )
    
    service = AggregateService(db)
    result = await service.get_aggregates(filters)
    return result

