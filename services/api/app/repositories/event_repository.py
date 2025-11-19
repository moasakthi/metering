"""Repository for event database operations."""

from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from app.models.database import MeteringEvent
from app.models.schemas import EventFilters, Pagination


class EventRepository:
    """Repository for event operations."""
    
    @staticmethod
    def create(db: Session, event_data: dict) -> MeteringEvent:
        """Create a new event."""
        event = MeteringEvent(**event_data)
        db.add(event)
        db.commit()
        db.refresh(event)
        return event
    
    @staticmethod
    def create_batch(db: Session, events_data: List[dict]) -> List[MeteringEvent]:
        """Create multiple events in batch."""
        events = [MeteringEvent(**event_data) for event_data in events_data]
        db.bulk_save_objects(events)
        db.commit()
        return events
    
    @staticmethod
    def get_by_id(db: Session, event_id: str) -> Optional[MeteringEvent]:
        """Get event by ID."""
        return db.query(MeteringEvent).filter(MeteringEvent.id == event_id).first()
    
    @staticmethod
    def get_all(
        db: Session,
        filters: EventFilters,
        pagination: Pagination
    ) -> tuple[List[MeteringEvent], int]:
        """Get events with filters and pagination."""
        query = db.query(MeteringEvent)
        
        # Apply filters
        if filters.tenant_id:
            query = query.filter(MeteringEvent.tenant_id == filters.tenant_id)
        if filters.resource:
            query = query.filter(MeteringEvent.resource == filters.resource)
        if filters.feature:
            query = query.filter(MeteringEvent.feature == filters.feature)
        if filters.start_date:
            query = query.filter(MeteringEvent.timestamp >= filters.start_date)
        if filters.end_date:
            query = query.filter(MeteringEvent.timestamp <= filters.end_date)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (pagination.page - 1) * pagination.page_size
        events = query.order_by(MeteringEvent.timestamp.desc()).offset(offset).limit(pagination.page_size).all()
        
        return events, total
    
    @staticmethod
    def get_usage_summary(
        db: Session,
        tenant_id: str,
        resource: Optional[str],
        feature: Optional[str],
        start_date: datetime,
        end_date: datetime
    ) -> int:
        """Get total usage for a tenant/resource/feature in a time range."""
        query = db.query(func.sum(MeteringEvent.quantity)).filter(
            MeteringEvent.tenant_id == tenant_id,
            MeteringEvent.timestamp >= start_date,
            MeteringEvent.timestamp <= end_date
        )
        
        if resource:
            query = query.filter(MeteringEvent.resource == resource)
        if feature:
            query = query.filter(MeteringEvent.feature == feature)
        
        result = query.scalar()
        return result or 0

