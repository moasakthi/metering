"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.v1.router import api_router
from app.core.database import Base, engine

# Create database tables (in production, use Alembic migrations)
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="Metering Service API",
    description="Dynamic API-Driven Metering Framework",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/v1")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Metering Service API",
        "version": "1.0.0",
        "docs": "/docs"
    }

