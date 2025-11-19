"""Event endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from app.core.database import get_db
from app.core.security import validate_api_key
from app.models.schemas import (
    EventCreate,
    EventBatchCreate,
    Event,
    EventFilters,
    Pagination,
    PaginatedResponse
)
from app.services.event_service import EventService

router = APIRouter()


@router.post("/events", response_model=dict, status_code=201)
async def create_event(
    event: EventCreate,
    db: Session = Depends(get_db),
    api_key: str = Depends(validate_api_key)
):
    """Create a single event."""
    service = EventService(db)
    result = await service.ingest_event(event)
    return {
        "status": "success",
        "events_processed": 1,
        "event_ids": [str(result.id)]
    }


@router.post("/events/batch", response_model=dict, status_code=201)
async def create_events_batch(
    batch: EventBatchCreate,
    db: Session = Depends(get_db),
    api_key: str = Depends(validate_api_key)
):
    """Create multiple events in batch."""
    service = EventService(db)
    results = await service.ingest_batch(batch.events)
    return {
        "status": "success",
        "events_processed": len(results),
        "event_ids": [str(r.id) for r in results]
    }


@router.get("/events", response_model=PaginatedResponse)
async def get_events(
    tenant_id: Optional[str] = Query(None),
    resource: Optional[str] = Query(None),
    feature: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=1000),
    db: Session = Depends(get_db),
    api_key: str = Depends(validate_api_key)
):
    """Get events with filtering and pagination."""
    filters = EventFilters(
        tenant_id=tenant_id,
        resource=resource,
        feature=feature,
        start_date=start_date,
        end_date=end_date
    )
    pagination = Pagination(page=page, page_size=page_size)
    
    service = EventService(db)
    result = await service.get_events(filters, pagination)
    return result

