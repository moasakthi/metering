"""Local event queue for offline buffering."""

import threading
import time
from typing import List, Dict, Any
from datetime import datetime
from collections import deque
from metering.exceptions import MeteringError


class EventQueue:
    """Thread-safe in-memory event queue."""
    
    def __init__(self, max_size: int = 10000):
        self.queue = deque(maxlen=max_size)
        self.lock = threading.Lock()
        self.max_size = max_size
    
    def add_event(
        self,
        tenant_id: str,
        resource: str,
        feature: str,
        quantity: int = 1,
        metadata: Dict[str, Any] = None,
        timestamp: datetime = None
    ):
        """Add event to queue."""
        with self.lock:
            if len(self.queue) >= self.max_size:
                raise MeteringError("Event queue is full")
            
            event = {
                "tenant_id": tenant_id,
                "resource": resource,
                "feature": feature,
                "quantity": quantity,
                "metadata": metadata or {},
                "timestamp": timestamp.isoformat() if timestamp else datetime.utcnow().isoformat()
            }
            self.queue.append(event)
    
    def get_batch(self, size: int) -> List[Dict[str, Any]]:
        """Get a batch of events from queue."""
        with self.lock:
            batch = []
            for _ in range(min(size, len(self.queue))):
                if self.queue:
                    batch.append(self.queue.popleft())
            return batch
    
    def size(self) -> int:
        """Get current queue size."""
        with self.lock:
            return len(self.queue)
    
    def clear(self):
        """Clear the queue."""
        with self.lock:
            self.queue.clear()

