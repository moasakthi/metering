"""Service for quota validation operations."""

from datetime import datetime
from sqlalchemy.orm import Session
from app.models.schemas import QuotaValidationRequest, QuotaValidationResult
from app.repositories.quota_repository import QuotaRepository
from app.repositories.event_repository import EventRepository
from app.services.cache_service import CacheService
from app.utils.time_utils import get_time_window, get_period_end


class QuotaService:
    """Service for quota validation business logic."""
    
    def __init__(self, db: Session):
        self.db = db
        self.quota_repo = QuotaRepository()
        self.event_repo = EventRepository()
        self.cache_service = CacheService()
    
    async def validate_quota(
        self,
        request: QuotaValidationRequest
    ) -> QuotaValidationResult:
        """Validate if action is allowed within quota."""
        # Get quota configuration
        quota = self.quota_repo.get_by_tenant_feature(
            self.db,
            request.tenant_id,
            request.feature,
            request.resource
        )
        
        if not quota:
            # No quota configured - allow by default
            return QuotaValidationResult(
                allowed=True,
                remaining=999999,  # Unlimited
                limit=999999,
                period=request.period,
                reset_at=get_period_end(datetime.utcnow(), request.period),
                current_usage=0,
                message="No quota configured"
            )
        
        # Get current usage
        current_usage = await self.get_usage(
            request.tenant_id,
            request.resource,
            request.feature,
            quota.period
        )
        
        # Calculate remaining
        remaining = max(0, quota.limit_value - current_usage)
        allowed = remaining >= request.quantity
        
        # Calculate reset time
        reset_at = get_period_end(datetime.utcnow(), quota.period)
        
        message = None
        if not allowed:
            message = f"Quota exceeded for feature '{request.feature}'. Current usage: {current_usage}/{quota.limit_value}"
        
        return QuotaValidationResult(
            allowed=allowed,
            remaining=remaining,
            limit=quota.limit_value,
            period=quota.period,
            reset_at=reset_at,
            current_usage=current_usage,
            message=message
        )
    
    async def get_usage(
        self,
        tenant_id: str,
        resource: str,
        feature: str,
        period: str
    ) -> int:
        """Get current usage for a tenant/feature/period."""
        timestamp = datetime.utcnow()
        
        # Try Redis cache first
        usage = self.cache_service.get_counter(
            tenant_id,
            resource,
            feature,
            period,
            timestamp
        )
        
        if usage is not None:
            return usage
        
        # Fallback to database
        window_start, window_end = get_time_window(timestamp, period)
        usage = self.event_repo.get_usage_summary(
            self.db,
            tenant_id,
            resource,
            feature,
            window_start,
            window_end
        )
        
        # Cache the result for future queries
        if usage > 0:
            from app.core.redis import get_redis
            redis = get_redis()
            key = self.cache_service.get_counter_key(
                tenant_id, resource, feature, period, timestamp
            )
            ttl = self.cache_service._get_ttl(period)
            redis.setex(key, ttl, usage)
        
        return usage

