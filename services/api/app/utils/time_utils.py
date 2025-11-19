"""Time window calculation utilities."""

from datetime import datetime, timedelta
from typing import Tuple


def get_time_window(
    timestamp: datetime,
    window_type: str
) -> Tuple[datetime, datetime]:
    """
    Calculate time window boundaries for a given timestamp and window type.
    
    Args:
        timestamp: The timestamp to calculate window for
        window_type: 'hourly', 'daily', 'monthly', or 'yearly'
    
    Returns:
        Tuple of (window_start, window_end)
    """
    if window_type == "hourly":
        window_start = timestamp.replace(minute=0, second=0, microsecond=0)
        window_end = window_start + timedelta(hours=1) - timedelta(microseconds=1)
    
    elif window_type == "daily":
        window_start = timestamp.replace(hour=0, minute=0, second=0, microsecond=0)
        window_end = window_start + timedelta(days=1) - timedelta(microseconds=1)
    
    elif window_type == "monthly":
        window_start = timestamp.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        # Calculate next month
        if timestamp.month == 12:
            window_end = datetime(timestamp.year + 1, 1, 1) - timedelta(microseconds=1)
        else:
            window_end = datetime(timestamp.year, timestamp.month + 1, 1) - timedelta(microseconds=1)
    
    elif window_type == "yearly":
        window_start = timestamp.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        window_end = datetime(timestamp.year + 1, 1, 1) - timedelta(microseconds=1)
    
    else:
        raise ValueError(f"Unsupported window_type: {window_type}")
    
    return window_start, window_end


def get_period_start(timestamp: datetime, period: str) -> datetime:
    """Get the start of a period for a given timestamp."""
    window_start, _ = get_time_window(timestamp, period)
    return window_start


def get_period_end(timestamp: datetime, period: str) -> datetime:
    """Get the end of a period for a given timestamp."""
    _, window_end = get_time_window(timestamp, period)
    return window_end

