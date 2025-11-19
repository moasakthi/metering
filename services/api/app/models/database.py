"""SQLAlchemy database models."""

from sqlalchemy import Column, String, Integer, DateTime, Boolean, JSON, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid
from app.core.database import Base


class MeteringEvent(Base):
    """Raw event storage model."""
    __tablename__ = "metering_events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(String(255), nullable=False, index=True)
    resource = Column(String(255), nullable=False, index=True)
    feature = Column(String(255), nullable=False, index=True)
    quantity = Column(Integer, nullable=False, default=1)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=func.now(), index=True)
    event_metadata = Column("metadata", JSONB, nullable=True)  # Column name is "metadata" in DB
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    
    __table_args__ = (
        CheckConstraint('quantity > 0', name='chk_quantity_positive'),
        {'extend_existing': True}
    )


class MeteringAggregate(Base):
    """Pre-computed aggregate model."""
    __tablename__ = "metering_aggregates"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(String(255), nullable=False, index=True)
    resource = Column(String(255), nullable=False, index=True)
    feature = Column(String(255), nullable=False, index=True)
    window_start = Column(DateTime(timezone=True), nullable=False, index=True)
    window_end = Column(DateTime(timezone=True), nullable=False, index=True)
    window_type = Column(String(20), nullable=False, index=True)  # hourly, daily, monthly
    total_quantity = Column(Integer, nullable=False, default=0)
    event_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        {'extend_existing': True}
    )


class MeteringQuota(Base):
    """Quota configuration model."""
    __tablename__ = "metering_quotas"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(String(255), nullable=False, index=True)
    resource = Column(String(255), nullable=True, index=True)
    feature = Column(String(255), nullable=False, index=True)
    limit_value = Column(Integer, nullable=False)
    period = Column(String(20), nullable=False)  # hourly, daily, monthly, yearly
    alert_threshold = Column(Integer, nullable=False, default=80)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        CheckConstraint('limit_value > 0', name='chk_limit_positive'),
        CheckConstraint('alert_threshold >= 0 AND alert_threshold <= 100', name='chk_alert_threshold'),
        {'extend_existing': True}
    )


class MeteringAPIKey(Base):
    """API key management model."""
    __tablename__ = "metering_api_keys"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key_hash = Column(String(255), nullable=False, unique=True, index=True)
    name = Column(String(255), nullable=True)
    tenant_id = Column(String(255), nullable=True, index=True)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    key_metadata = Column("metadata", JSONB, nullable=True)  # Column name is "metadata" in DB
    
    __table_args__ = (
        {'extend_existing': True}
    )

