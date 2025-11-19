"""Pydantic request/response schemas."""

from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID


# Event Schemas
class EventCreate(BaseModel):
    """Schema for creating an event."""
    tenant_id: str = Field(..., min_length=1, max_length=255)
    resource: str = Field(..., min_length=1, max_length=255)
    feature: str = Field(..., min_length=1, max_length=255)
    quantity: int = Field(default=1, gt=0)
    timestamp: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None


class EventBatchCreate(BaseModel):
    """Schema for batch event creation."""
    events: List[EventCreate] = Field(..., min_items=1, max_items=1000)


class Event(BaseModel):
    """Schema for event response."""
    id: UUID
    tenant_id: str
    resource: str
    feature: str
    quantity: int
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = Field(None, alias="event_metadata")
    created_at: datetime
    
    class Config:
        from_attributes = True
        populate_by_name = True  # Allow both alias and original name


class EventFilters(BaseModel):
    """Schema for event query filters."""
    tenant_id: Optional[str] = None
    resource: Optional[str] = None
    feature: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class Pagination(BaseModel):
    """Schema for pagination."""
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=50, ge=1, le=1000)


class PaginatedResponse(BaseModel):
    """Schema for paginated response."""
    items: List[Dict[str, Any]]  # Use Dict instead of generic for FastAPI compatibility
    page: int
    page_size: int
    total: int
    total_pages: int


# Aggregate Schemas
class AggregateFilters(BaseModel):
    """Schema for aggregate query filters."""
    tenant_id: Optional[str] = None
    resource: Optional[str] = None
    feature: Optional[str] = None
    window_type: str = Field(..., pattern="^(hourly|daily|monthly)$")
    start_date: datetime
    end_date: datetime
    group_by: Optional[str] = Field(default="resource,feature")


class Aggregate(BaseModel):
    """Schema for aggregate response."""
    tenant_id: str
    resource: str
    feature: str
    window_start: datetime
    window_end: datetime
    window_type: str
    total_quantity: int
    event_count: int
    
    class Config:
        from_attributes = True


class AggregateResponse(BaseModel):
    """Schema for aggregate query response."""
    aggregates: List[Aggregate]
    summary: Dict[str, Any]


# Quota Schemas
class QuotaValidationRequest(BaseModel):
    """Schema for quota validation request."""
    tenant_id: str
    resource: str
    feature: str
    quantity: int = Field(default=1, gt=0)
    period: str = Field(..., pattern="^(hourly|daily|monthly|yearly)$")


class QuotaValidationResult(BaseModel):
    """Schema for quota validation response."""
    allowed: bool
    remaining: int
    limit: int
    period: str
    reset_at: datetime
    current_usage: int
    message: Optional[str] = None


class QuotaCreate(BaseModel):
    """Schema for creating a quota."""
    tenant_id: str
    resource: Optional[str] = None
    feature: str
    limit_value: int = Field(..., gt=0)
    period: str = Field(..., pattern="^(hourly|daily|monthly|yearly)$")
    alert_threshold: int = Field(default=80, ge=0, le=100)


class Quota(BaseModel):
    """Schema for quota response."""
    id: UUID
    tenant_id: str
    resource: Optional[str]
    feature: str
    limit_value: int
    period: str
    alert_threshold: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Health Check Schema
class HealthResponse(BaseModel):
    """Schema for health check response."""
    status: str
    timestamp: datetime
    services: Dict[str, str]

