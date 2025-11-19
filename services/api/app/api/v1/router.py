"""API v1 router."""

from fastapi import APIRouter
from app.api.v1.endpoints import events, aggregates, validate, health

api_router = APIRouter()

api_router.include_router(events.router, prefix="/meter", tags=["events"])
api_router.include_router(aggregates.router, prefix="/meter", tags=["aggregates"])
api_router.include_router(validate.router, prefix="/meter", tags=["validate"])
api_router.include_router(health.router, prefix="/meter", tags=["health"])

