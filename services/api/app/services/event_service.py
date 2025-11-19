"""Service for event operations."""

from typing import List
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.schemas import EventCreate, Event, EventFilters, Pagination, PaginatedResponse
from app.repositories.event_repository import EventRepository
from app.services.cache_service import CacheService


class EventService:
    """Service for event business logic."""
    
    def __init__(self, db: Session):
        self.db = db
        self.event_repo = EventRepository()
        self.cache_service = CacheService()
    
    async def ingest_event(self, event: EventCreate) -> Event:
        """Ingest a single event."""
        # Set timestamp if not provided
        timestamp = event.timestamp or datetime.utcnow()
        
        # Create event in database
        event_data = {
            "tenant_id": event.tenant_id,
            "resource": event.resource,
            "feature": event.feature,
            "quantity": event.quantity,
            "timestamp": timestamp,
            "event_metadata": event.metadata
        }
        
        db_event = self.event_repo.create(self.db, event_data)
        
        # Update Redis counters for common periods
        for period in ["hourly", "daily", "monthly"]:
            self.cache_service.increment_counter(
                event.tenant_id,
                event.resource,
                event.feature,
                period,
                timestamp,
                event.quantity
            )
        
        return Event.model_validate(db_event)
    
    async def ingest_batch(self, events: List[EventCreate]) -> List[Event]:
        """Ingest multiple events in batch."""
        timestamp = datetime.utcnow()
        
        events_data = []
        for event in events:
            event_timestamp = event.timestamp or timestamp
            events_data.append({
                "tenant_id": event.tenant_id,
                "resource": event.resource,
                "feature": event.feature,
                "quantity": event.quantity,
                "timestamp": event_timestamp,
                "event_metadata": event.metadata
            })
        
        # Bulk insert
        db_events = self.event_repo.create_batch(self.db, events_data)
        
        # Update Redis counters
        for event, db_event in zip(events, db_events):
            for period in ["hourly", "daily", "monthly"]:
                self.cache_service.increment_counter(
                    event.tenant_id,
                    event.resource,
                    event.feature,
                    period,
                    db_event.timestamp,
                    event.quantity
                )
        
        return [Event.model_validate(db_event) for db_event in db_events]
    
    async def get_events(
        self,
        filters: EventFilters,
        pagination: Pagination
    ) -> PaginatedResponse:
        """Get events with filters and pagination."""
        events, total = self.event_repo.get_all(self.db, filters, pagination)
        
        total_pages = (total + pagination.page_size - 1) // pagination.page_size
        
        # Convert events to dict for PaginatedResponse
        event_dicts = [Event.model_validate(event).model_dump() for event in events]
        return PaginatedResponse(
            items=event_dicts,
            page=pagination.page,
            page_size=pagination.page_size,
            total=total,
            total_pages=total_pages
        )

