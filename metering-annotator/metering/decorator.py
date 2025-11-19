"""Metering decorator for function instrumentation."""

import functools
import inspect
from typing import Callable, Optional, Dict, Any
from metering.client import MeteringClient
from metering.config import config


class Meter:
    """Metering decorator for function instrumentation."""
    
    def __init__(
        self,
        resource: str,
        feature: str,
        quantity: int = 1,
        tenant_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        transport: Optional[str] = None
    ):
        self.resource = resource
        self.feature = feature
        self.quantity = quantity
        self.tenant_id = tenant_id
        self.metadata = metadata or {}
        self.transport = transport or config.transport_mode
        self.client = MeteringClient(transport_mode=self.transport)
    
    def _extract_tenant_id(self, args, kwargs, func) -> Optional[str]:
        """Extract tenant_id from function arguments."""
        if self.tenant_id:
            return self.tenant_id
        
        # Try to find tenant_id in function signature
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())
        
        # Check kwargs first
        if "tenant_id" in kwargs:
            return str(kwargs["tenant_id"])
        
        # Check args by position
        if "tenant_id" in params:
            idx = params.index("tenant_id")
            if idx < len(args):
                return str(args[idx])
        
        # Try common patterns
        for key in ["tenant", "org_id", "organization_id"]:
            if key in kwargs:
                return str(kwargs[key])
            if key in params:
                idx = params.index(key)
                if idx < len(args):
                    return str(args[idx])
        
        return None
    
    def _record_event(self, result, args, kwargs, func):
        """Record event synchronously."""
        tenant_id = self._extract_tenant_id(args, kwargs, func) or "unknown"
        
        try:
            self.client.record_event(
                tenant_id=tenant_id,
                resource=self.resource,
                feature=self.feature,
                quantity=self.quantity,
                metadata=self.metadata
            )
        except Exception:
            pass  # Don't fail the function if metering fails
    
    async def _record_event_async(self, result, args, kwargs, func):
        """Record event asynchronously."""
        tenant_id = self._extract_tenant_id(args, kwargs, func) or "unknown"
        
        try:
            await self.client.record_event_async(
                tenant_id=tenant_id,
                resource=self.resource,
                feature=self.feature,
                quantity=self.quantity,
                metadata=self.metadata
            )
        except Exception:
            pass  # Don't fail the function if metering fails
    
    def __call__(self, func: Callable) -> Callable:
        """Apply decorator to function."""
        if inspect.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                result = await func(*args, **kwargs)
                await self._record_event_async(result, args, kwargs, func)
                return result
            return async_wrapper
        else:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                result = func(*args, **kwargs)
                self._record_event(result, args, kwargs, func)
                return result
            return wrapper


def meter(
    resource: str,
    feature: str,
    quantity: int = 1,
    tenant_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    transport: Optional[str] = None
):
    """
    Decorator for metering function calls.
    
    Usage:
        @meter(resource="billing", feature="invoice_generate")
        def generate_invoice(order_id):
            ...
    """
    return Meter(resource, feature, quantity, tenant_id, metadata, transport)

