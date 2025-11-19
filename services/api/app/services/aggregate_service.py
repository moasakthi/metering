"""Service for aggregation operations."""

from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.schemas import Aggregate, AggregateFilters, AggregateResponse
from app.models.database import MeteringEvent, MeteringAggregate
from app.repositories.aggregate_repository import AggregateRepository
from app.services.cache_service import CacheService
from app.utils.time_utils import get_time_window


class AggregateService:
    """Service for aggregate business logic."""
    
    def __init__(self, db: Session):
        self.db = db
        self.aggregate_repo = AggregateRepository()
        self.cache_service = CacheService()
    
    async def compute_aggregates(
        self,
        window_type: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[Aggregate]:
        """Compute aggregates for a time window."""
        # Query raw events and group by tenant/resource/feature/window
        # This is a simplified version - in production, you'd want to batch process
        
        aggregates = []
        current_date = start_date
        
        while current_date < end_date:
            window_start, window_end = get_time_window(current_date, window_type)
            
            # Query events in this window
            query = self.db.query(
                MeteringEvent.tenant_id,
                MeteringEvent.resource,
                MeteringEvent.feature,
                func.sum(MeteringEvent.quantity).label('total_quantity'),
                func.count(MeteringEvent.id).label('event_count')
            ).filter(
                MeteringEvent.timestamp >= window_start,
                MeteringEvent.timestamp <= window_end
            ).group_by(
                MeteringEvent.tenant_id,
                MeteringEvent.resource,
                MeteringEvent.feature
            )
            
            results = query.all()
            
            for result in results:
                aggregate = self.aggregate_repo.create_or_update(
                    self.db,
                    result.tenant_id,
                    result.resource,
                    result.feature,
                    window_start,
                    window_end,
                    window_type,
                    int(result.total_quantity or 0),
                    int(result.event_count or 0)
                )
                
                # Cache the aggregate
                self.cache_service.set_aggregate(
                    result.tenant_id,
                    result.resource,
                    result.feature,
                    window_type,
                    window_start,
                    aggregate.total_quantity,
                    aggregate.event_count
                )
                
                aggregates.append(Aggregate.from_orm(aggregate))
            
            # Move to next window
            if window_type == "hourly":
                current_date = window_end + datetime.resolution
            elif window_type == "daily":
                current_date = window_end + datetime.resolution
            elif window_type == "monthly":
                if current_date.month == 12:
                    current_date = datetime(current_date.year + 1, 1, 1)
                else:
                    current_date = datetime(current_date.year, current_date.month + 1, 1)
        
        return aggregates
    
    async def get_aggregates(
        self,
        filters: AggregateFilters
    ) -> AggregateResponse:
        """Get aggregates with filters."""
        # Try to get from database first
        aggregates = self.aggregate_repo.get_aggregates(
            self.db,
            filters.tenant_id,
            filters.resource,
            filters.feature,
            filters.window_type,
            filters.start_date,
            filters.end_date
        )
        
        # If no aggregates found, compute on-the-fly
        if not aggregates:
            aggregates_list = await self.compute_aggregates(
                filters.window_type,
                filters.start_date,
                filters.end_date
            )
            # Filter the computed aggregates
            if filters.tenant_id:
                aggregates_list = [a for a in aggregates_list if a.tenant_id == filters.tenant_id]
            if filters.resource:
                aggregates_list = [a for a in aggregates_list if a.resource == filters.resource]
            if filters.feature:
                aggregates_list = [a for a in aggregates_list if a.feature == filters.feature]
            
            return AggregateResponse(
                aggregates=aggregates_list,
                summary={
                    "total_quantity": sum(a.total_quantity for a in aggregates_list),
                    "total_events": sum(a.event_count for a in aggregates_list)
                }
            )
        
        aggregate_models = [Aggregate.from_orm(agg) for agg in aggregates]
        
        return AggregateResponse(
            aggregates=aggregate_models,
            summary={
                "total_quantity": sum(agg.total_quantity for agg in aggregates),
                "total_events": sum(agg.event_count for agg in aggregates)
            }
        )

