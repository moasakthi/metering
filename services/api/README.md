# Metering Service API

FastAPI-based backend service for the Dynamic API-Driven Metering Framework.

## Features

- Event ingestion (single and batch)
- Event querying with filters and pagination
- Usage aggregation (hourly, daily, monthly)
- Quota validation
- Redis caching for performance
- PostgreSQL for persistent storage

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Run database migrations (when Alembic is set up):
```bash
alembic upgrade head
```

4. Start the service:
```bash
uvicorn app.main:app --reload
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Environment Variables

See `.env.example` for all available configuration options.

