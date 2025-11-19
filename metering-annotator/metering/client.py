"""HTTP client for Metering Service API."""

import requests
import aiohttp
import asyncio
import threading
import time
from typing import Optional, Dict, Any, List
from datetime import datetime
from tenacity import retry, stop_after_attempt, wait_exponential
from metering.config import config
from metering.queue import EventQueue
from metering.exceptions import MeteringAPIError


class MeteringClient:
    """HTTP client for Metering Service API."""
    
    def __init__(
        self,
        api_url: Optional[str] = None,
        api_key: Optional[str] = None,
        transport_mode: Optional[str] = None
    ):
        self.api_url = (api_url or config.api_url).rstrip("/")
        self.api_key = api_key or config.api_key
        self.transport_mode = transport_mode or config.transport_mode
        self.queue = EventQueue()
        self._batch_thread = None
        self._running = False
        
        if self.transport_mode == "batch":
            self._start_batch_worker()
    
    def _start_batch_worker(self):
        """Start background thread for batch processing."""
        if self._running:
            return
        
        self._running = True
        
        def worker():
            while self._running:
                try:
                    batch = self.queue.get_batch(config.batch_size)
                    if batch:
                        self._send_batch_sync(batch)
                    time.sleep(config.batch_interval_seconds)
                except Exception:
                    pass  # Log error in production
        
        self._batch_thread = threading.Thread(target=worker, daemon=True)
        self._batch_thread.start()
    
    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for API requests."""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        return headers
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def record_event_sync(
        self,
        tenant_id: str,
        resource: str,
        feature: str,
        quantity: int = 1,
        metadata: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None
    ) -> bool:
        """Record event synchronously."""
        try:
            payload = {
                "tenant_id": tenant_id,
                "resource": resource,
                "feature": feature,
                "quantity": quantity,
                "metadata": metadata
            }
            if timestamp:
                payload["timestamp"] = timestamp.isoformat()
            
            response = requests.post(
                f"{self.api_url}/v1/meter/events",
                json=payload,
                headers=self._get_headers(),
                timeout=config.timeout
            )
            response.raise_for_status()
            return True
        except Exception as e:
            # Fallback to local queue
            self.queue.add_event(tenant_id, resource, feature, quantity, metadata, timestamp)
            raise MeteringAPIError(f"Failed to record event: {str(e)}")
    
    async def record_event_async(
        self,
        tenant_id: str,
        resource: str,
        feature: str,
        quantity: int = 1,
        metadata: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None
    ) -> bool:
        """Record event asynchronously."""
        try:
            payload = {
                "tenant_id": tenant_id,
                "resource": resource,
                "feature": feature,
                "quantity": quantity,
                "metadata": metadata
            }
            if timestamp:
                payload["timestamp"] = timestamp.isoformat()
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_url}/v1/meter/events",
                    json=payload,
                    headers=self._get_headers(),
                    timeout=aiohttp.ClientTimeout(total=config.timeout)
                ) as response:
                    response.raise_for_status()
                    return True
        except Exception as e:
            # Fallback to local queue
            self.queue.add_event(tenant_id, resource, feature, quantity, metadata, timestamp)
            raise MeteringAPIError(f"Failed to record event: {str(e)}")
    
    def _send_batch_sync(self, events: List[Dict[str, Any]]):
        """Send batch of events synchronously."""
        try:
            response = requests.post(
                f"{self.api_url}/v1/meter/events/batch",
                json={"events": events},
                headers=self._get_headers(),
                timeout=config.timeout * 2
            )
            response.raise_for_status()
        except Exception:
            # Re-queue events on failure
            for event in events:
                self.queue.add_event(**event)
    
    def record_event(
        self,
        tenant_id: str,
        resource: str,
        feature: str,
        quantity: int = 1,
        metadata: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None
    ):
        """Record event based on transport mode."""
        if self.transport_mode == "sync":
            return self.record_event_sync(tenant_id, resource, feature, quantity, metadata, timestamp)
        elif self.transport_mode == "async":
            # Fire and forget
            asyncio.create_task(
                self.record_event_async(tenant_id, resource, feature, quantity, metadata, timestamp)
            )
            return True
        elif self.transport_mode == "batch":
            self.queue.add_event(tenant_id, resource, feature, quantity, metadata, timestamp)
            return True
        else:
            raise MeteringAPIError(f"Unknown transport mode: {self.transport_mode}")
    
    def close(self):
        """Close client and cleanup."""
        self._running = False
        if self._batch_thread:
            self._batch_thread.join(timeout=5)

