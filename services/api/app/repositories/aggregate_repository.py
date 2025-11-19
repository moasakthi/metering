"""Repository for aggregate database operations."""

from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from app.models.database import MeteringAggregate


class AggregateRepository:
    """Repository for aggregate operations."""
    
    @staticmethod
    def create_or_update(
        db: Session,
        tenant_id: str,
        resource: str,
        feature: str,
        window_start: datetime,
        window_end: datetime,
        window_type: str,
        total_quantity: int,
        event_count: int
    ) -> MeteringAggregate:
        """Create or update an aggregate."""
        aggregate = db.query(MeteringAggregate).filter(
            MeteringAggregate.tenant_id == tenant_id,
            MeteringAggregate.resource == resource,
            MeteringAggregate.feature == feature,
            MeteringAggregate.window_start == window_start,
            MeteringAggregate.window_end == window_end,
            MeteringAggregate.window_type == window_type
        ).first()
        
        if aggregate:
            aggregate.total_quantity = total_quantity
            aggregate.event_count = event_count
        else:
            aggregate = MeteringAggregate(
                tenant_id=tenant_id,
                resource=resource,
                feature=feature,
                window_start=window_start,
                window_end=window_end,
                window_type=window_type,
                total_quantity=total_quantity,
                event_count=event_count
            )
            db.add(aggregate)
        
        db.commit()
        db.refresh(aggregate)
        return aggregate
    
    @staticmethod
    def get_aggregates(
        db: Session,
        tenant_id: Optional[str],
        resource: Optional[str],
        feature: Optional[str],
        window_type: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[MeteringAggregate]:
        """Get aggregates with filters."""
        query = db.query(MeteringAggregate).filter(
            MeteringAggregate.window_type == window_type,
            MeteringAggregate.window_start >= start_date,
            MeteringAggregate.window_end <= end_date
        )
        
        if tenant_id:
            query = query.filter(MeteringAggregate.tenant_id == tenant_id)
        if resource:
            query = query.filter(MeteringAggregate.resource == resource)
        if feature:
            query = query.filter(MeteringAggregate.feature == feature)
        
        return query.order_by(MeteringAggregate.window_start).all()

