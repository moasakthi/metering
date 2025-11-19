"""Middleware for FastAPI/Flask/Starlette."""

from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from metering.client import MeteringClient
from metering.config import config


class MeteringMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware for automatic API metering."""
    
    def __init__(self, app, api_url: str = None, api_key: str = None):
        super().__init__(app)
        self.client = MeteringClient(api_url=api_url, api_key=api_key)
    
    def _extract_tenant_id(self, request: Request) -> str:
        """Extract tenant_id from request."""
        # Try header first
        tenant_id = request.headers.get("X-Tenant-ID") or request.headers.get("X-Tenant-Id")
        if tenant_id:
            return tenant_id
        
        # Try path parameter
        if "tenant_id" in request.path_params:
            return str(request.path_params["tenant_id"])
        
        # Try query parameter
        if "tenant_id" in request.query_params:
            return request.query_params["tenant_id"]
        
        return "unknown"
    
    def _extract_resource_feature(self, request: Request) -> tuple[str, str]:
        """Extract resource and feature from route."""
        # Use route path as resource
        resource = request.url.path.strip("/").replace("/", ".")
        if not resource:
            resource = "api"
        
        # Use HTTP method as feature
        feature = request.method.lower()
        
        return resource, feature
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and record event."""
        # Skip health checks and docs
        if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)
        
        # Process request
        response = await call_next(request)
        
        # Record event if successful
        if response.status_code < 400:
            tenant_id = self._extract_tenant_id(request)
            resource, feature = self._extract_resource_feature(request)
            
            try:
                await self.client.record_event_async(
                    tenant_id=tenant_id,
                    resource=resource,
                    feature=feature,
                    quantity=1
                )
            except Exception:
                pass  # Don't fail request if metering fails
        
        return response

