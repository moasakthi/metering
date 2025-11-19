"""Redis cache service."""

from typing import Optional
from datetime import datetime, timedelta
from app.core.redis import get_redis
from app.utils.time_utils import get_time_window


class CacheService:
    """Service for Redis cache operations."""
    
    @staticmethod
    def get_counter_key(
        tenant_id: str,
        resource: str,
        feature: str,
        period: str,
        timestamp: datetime
    ) -> str:
        """Generate counter key for Redis."""
        window_start, _ = get_time_window(timestamp, period)
        window_str = window_start.strftime("%Y-%m-%d-%H")
        return f"meter:counter:{tenant_id}:{resource}:{feature}:{period}:{window_str}"
    
    @staticmethod
    def increment_counter(
        tenant_id: str,
        resource: str,
        feature: str,
        period: str,
        timestamp: datetime,
        quantity: int = 1
    ) -> int:
        """Increment counter in Redis."""
        redis = get_redis()
        key = CacheService.get_counter_key(tenant_id, resource, feature, period, timestamp)
        
        # Set TTL based on period
        ttl = CacheService._get_ttl(period)
        value = redis.incrby(key, quantity)
        redis.expire(key, ttl)
        
        return value
    
    @staticmethod
    def get_counter(
        tenant_id: str,
        resource: str,
        feature: str,
        period: str,
        timestamp: datetime
    ) -> Optional[int]:
        """Get counter value from Redis."""
        redis = get_redis()
        key = CacheService.get_counter_key(tenant_id, resource, feature, period, timestamp)
        value = redis.get(key)
        return int(value) if value else None
    
    @staticmethod
    def get_aggregate_cache_key(
        tenant_id: str,
        resource: str,
        feature: str,
        window_type: str,
        window_start: datetime
    ) -> str:
        """Generate aggregate cache key."""
        window_str = window_start.strftime("%Y-%m-%d-%H")
        return f"meter:aggregate:{tenant_id}:{resource}:{feature}:{window_type}:{window_str}"
    
    @staticmethod
    def set_aggregate(
        tenant_id: str,
        resource: str,
        feature: str,
        window_type: str,
        window_start: datetime,
        total_quantity: int,
        event_count: int,
        ttl: int = 3600
    ):
        """Cache aggregate data."""
        redis = get_redis()
        key = CacheService.get_aggregate_cache_key(
            tenant_id, resource, feature, window_type, window_start
        )
        redis.setex(
            key,
            ttl,
            f"{total_quantity}:{event_count}"
        )
    
    @staticmethod
    def get_quota_cache_key(tenant_id: str, feature: str) -> str:
        """Generate quota cache key."""
        return f"meter:quota:{tenant_id}:{feature}"
    
    @staticmethod
    def set_quota(
        tenant_id: str,
        feature: str,
        limit_value: int,
        period: str,
        alert_threshold: int,
        ttl: int = 300
    ):
        """Cache quota configuration."""
        redis = get_redis()
        key = CacheService.get_quota_cache_key(tenant_id, feature)
        data = f"{limit_value}:{period}:{alert_threshold}"
        redis.setex(key, ttl, data)
    
    @staticmethod
    def get_quota(tenant_id: str, feature: str) -> Optional[dict]:
        """Get quota from cache."""
        redis = get_redis()
        key = CacheService.get_quota_cache_key(tenant_id, feature)
        data = redis.get(key)
        if data:
            parts = data.split(":")
            return {
                "limit_value": int(parts[0]),
                "period": parts[1],
                "alert_threshold": int(parts[2])
            }
        return None
    
    @staticmethod
    def _get_ttl(period: str) -> int:
        """Get TTL in seconds for a period."""
        ttl_map = {
            "hourly": 3600 * 2,  # 2 hours
            "daily": 86400 * 2,  # 2 days
            "monthly": 86400 * 32,  # 32 days
            "yearly": 86400 * 366  # 366 days
        }
        return ttl_map.get(period, 3600)

