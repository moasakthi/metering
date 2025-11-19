# **Low-Level Design (LLD) Document**
## **Dynamic API-Driven Metering Framework**

**Version:** 1.0  
**Date:** 2025-11-20  
**Status:** Draft

---

## **1. Introduction**

This document provides detailed low-level design specifications for the Dynamic API-Driven Metering Framework. It includes database schemas, API specifications, class diagrams, sequence diagrams, and implementation details for each component.

---

## **2. Database Schema Design**

### **2.1 PostgreSQL Schema**

#### **2.1.1 Table: `metering_events`**

Raw event storage table.

```sql
CREATE TABLE metering_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id VARCHAR(255) NOT NULL,
    resource VARCHAR(255) NOT NULL,
    feature VARCHAR(255) NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    -- Indexes
    CONSTRAINT chk_quantity_positive CHECK (quantity > 0)
);

-- Indexes for query performance
CREATE INDEX idx_events_tenant_id ON metering_events(tenant_id);
CREATE INDEX idx_events_resource ON metering_events(resource);
CREATE INDEX idx_events_feature ON metering_events(feature);
CREATE INDEX idx_events_timestamp ON metering_events(timestamp DESC);
CREATE INDEX idx_events_tenant_resource_feature ON metering_events(tenant_id, resource, feature);
CREATE INDEX idx_events_timestamp_range ON metering_events(timestamp) WHERE timestamp >= NOW() - INTERVAL '90 days';

-- GIN index for JSONB metadata queries
CREATE INDEX idx_events_metadata ON metering_events USING GIN(metadata);
```

#### **2.1.2 Table: `metering_aggregates`**

Pre-computed aggregate values for faster queries.

```sql
CREATE TABLE metering_aggregates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id VARCHAR(255) NOT NULL,
    resource VARCHAR(255) NOT NULL,
    feature VARCHAR(255) NOT NULL,
    window_start TIMESTAMP WITH TIME ZONE NOT NULL,
    window_end TIMESTAMP WITH TIME ZONE NOT NULL,
    window_type VARCHAR(20) NOT NULL, -- 'hourly', 'daily', 'monthly'
    total_quantity INTEGER NOT NULL DEFAULT 0,
    event_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    -- Unique constraint to prevent duplicate aggregates
    CONSTRAINT uq_aggregate_window UNIQUE (tenant_id, resource, feature, window_start, window_end, window_type)
);

-- Indexes
CREATE INDEX idx_aggregates_tenant ON metering_aggregates(tenant_id);
CREATE INDEX idx_aggregates_resource_feature ON metering_aggregates(resource, feature);
CREATE INDEX idx_aggregates_window ON metering_aggregates(window_start, window_end);
CREATE INDEX idx_aggregates_window_type ON metering_aggregates(window_type);
```

#### **2.1.3 Table: `metering_quotas`**

Quota configuration and limits per tenant/feature.

```sql
CREATE TABLE metering_quotas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id VARCHAR(255) NOT NULL,
    resource VARCHAR(255),
    feature VARCHAR(255) NOT NULL,
    limit_value INTEGER NOT NULL,
    period VARCHAR(20) NOT NULL, -- 'hourly', 'daily', 'monthly', 'yearly'
    alert_threshold INTEGER DEFAULT 80, -- Percentage (0-100)
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    CONSTRAINT chk_limit_positive CHECK (limit_value > 0),
    CONSTRAINT chk_alert_threshold CHECK (alert_threshold >= 0 AND alert_threshold <= 100)
);

-- Indexes
CREATE INDEX idx_quotas_tenant_feature ON metering_quotas(tenant_id, feature) WHERE is_active = TRUE;
CREATE INDEX idx_quotas_resource ON metering_quotas(resource) WHERE is_active = TRUE;
```

#### **2.1.4 Table: `metering_api_keys`**

API key management for authentication.

```sql
CREATE TABLE metering_api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    key_hash VARCHAR(255) NOT NULL UNIQUE, -- SHA-256 hash of the API key
    name VARCHAR(255), -- Human-readable name
    tenant_id VARCHAR(255), -- Optional: restrict key to specific tenant
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    last_used_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE, -- Optional expiration
    metadata JSONB
);

-- Indexes
CREATE INDEX idx_api_keys_hash ON metering_api_keys(key_hash) WHERE is_active = TRUE;
CREATE INDEX idx_api_keys_tenant ON metering_api_keys(tenant_id) WHERE is_active = TRUE;
```

### **2.2 Redis Data Structures**

#### **2.2.1 Counter Keys**

Format: `meter:counter:{tenant_id}:{resource}:{feature}:{period}:{window}`

Example: `meter:counter:org_001:billing:invoice_generate:daily:2025-11-20`

- **Type:** String (integer value)
- **TTL:** Based on period (daily = 24h, monthly = 31 days)

#### **2.2.2 Aggregate Cache Keys**

Format: `meter:aggregate:{tenant_id}:{resource}:{feature}:{window_type}:{window_start}`

Example: `meter:aggregate:org_001:billing:invoice_generate:daily:2025-11-20`

- **Type:** Hash
- **Fields:** `total_quantity`, `event_count`, `window_start`, `window_end`
- **TTL:** 1 hour

#### **2.2.3 Quota Cache Keys**

Format: `meter:quota:{tenant_id}:{feature}`

- **Type:** Hash
- **Fields:** `limit_value`, `period`, `alert_threshold`
- **TTL:** 5 minutes

---

## **3. API Specification**

### **3.1 Base URL & Authentication**

```
Base URL: http://localhost:8000/v1/meter
Authentication: X-API-Key header
```

### **3.2 Endpoint: POST /v1/meter/events**

**Purpose:** Ingest single or batch events

**Request Headers:**
```
X-API-Key: <api_key>
Content-Type: application/json
```

**Request Body (Single Event):**
```json
{
  "tenant_id": "org_001",
  "resource": "billing",
  "feature": "invoice_generate",
  "quantity": 1,
  "timestamp": "2025-11-20T10:31:00Z",
  "metadata": {
    "user": "u_123",
    "order": "ord_456"
  }
}
```

**Request Body (Batch Events):**
```json
{
  "events": [
    {
      "tenant_id": "org_001",
      "resource": "billing",
      "feature": "invoice_generate",
      "quantity": 1,
      "timestamp": "2025-11-20T10:31:00Z",
      "metadata": {}
    },
    {
      "tenant_id": "org_001",
      "resource": "billing",
      "feature": "pdf_export",
      "quantity": 1,
      "timestamp": "2025-11-20T10:32:00Z",
      "metadata": {}
    }
  ]
}
```

**Response (201 Created):**
```json
{
  "status": "success",
  "events_processed": 1,
  "event_ids": ["550e8400-e29b-41d4-a716-446655440000"]
}
```

**Response (Batch - 201 Created):**
```json
{
  "status": "success",
  "events_processed": 2,
  "event_ids": [
    "550e8400-e29b-41d4-a716-446655440000",
    "550e8400-e29b-41d4-a716-446655440001"
  ]
}
```

**Error Responses:**
- `400 Bad Request`: Invalid payload
- `401 Unauthorized`: Invalid/missing API key
- `422 Unprocessable Entity`: Validation errors

### **3.3 Endpoint: GET /v1/meter/events**

**Purpose:** Retrieve events with filtering and pagination

**Query Parameters:**
- `tenant_id` (optional): Filter by tenant
- `resource` (optional): Filter by resource
- `feature` (optional): Filter by feature
- `start_date` (optional): ISO 8601 timestamp
- `end_date` (optional): ISO 8601 timestamp
- `page` (optional, default: 1): Page number
- `page_size` (optional, default: 50, max: 1000): Items per page

**Example Request:**
```
GET /v1/meter/events?tenant_id=org_001&resource=billing&page=1&page_size=50
```

**Response (200 OK):**
```json
{
  "events": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "tenant_id": "org_001",
      "resource": "billing",
      "feature": "invoice_generate",
      "quantity": 1,
      "timestamp": "2025-11-20T10:31:00Z",
      "metadata": {
        "user": "u_123"
      },
      "created_at": "2025-11-20T10:31:01Z"
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 50,
    "total": 150,
    "total_pages": 3
  }
}
```

### **3.4 Endpoint: GET /v1/meter/aggregates**

**Purpose:** Get aggregated usage statistics

**Query Parameters:**
- `tenant_id` (optional): Filter by tenant
- `resource` (optional): Filter by resource
- `feature` (optional): Filter by feature
- `window_type` (required): `hourly`, `daily`, `monthly`
- `start_date` (required): ISO 8601 timestamp
- `end_date` (required): ISO 8601 timestamp
- `group_by` (optional, default: `resource,feature`): Comma-separated list (`tenant_id`, `resource`, `feature`)

**Example Request:**
```
GET /v1/meter/aggregates?window_type=daily&start_date=2025-11-01T00:00:00Z&end_date=2025-11-20T23:59:59Z&group_by=tenant_id,resource
```

**Response (200 OK):**
```json
{
  "aggregates": [
    {
      "tenant_id": "org_001",
      "resource": "billing",
      "feature": "invoice_generate",
      "window_start": "2025-11-20T00:00:00Z",
      "window_end": "2025-11-20T23:59:59Z",
      "window_type": "daily",
      "total_quantity": 150,
      "event_count": 150
    }
  ],
  "summary": {
    "total_quantity": 150,
    "total_events": 150
  }
}
```

### **3.5 Endpoint: POST /v1/meter/validate**

**Purpose:** Validate quota before performing an action

**Request Body:**
```json
{
  "tenant_id": "org_001",
  "resource": "billing",
  "feature": "invoice_generate",
  "quantity": 1,
  "period": "monthly"
}
```

**Response (200 OK):**
```json
{
  "allowed": true,
  "remaining": 22,
  "limit": 100,
  "period": "monthly",
  "reset_at": "2025-12-01T00:00:00Z",
  "current_usage": 78
}
```

**Response (Quota Exceeded - 200 OK):**
```json
{
  "allowed": false,
  "remaining": 0,
  "limit": 100,
  "period": "monthly",
  "reset_at": "2025-12-01T00:00:00Z",
  "current_usage": 100,
  "message": "Quota exceeded for feature 'invoice_generate'"
}
```

### **3.6 Endpoint: GET /v1/meter/health**

**Purpose:** Health check endpoint

**Response (200 OK):**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-20T10:31:00Z",
  "services": {
    "database": "connected",
    "redis": "connected"
  }
}
```

---

## **4. Metering Service Implementation**

### **4.1 Project Structure**

```
metering-service/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app entry point
│   ├── config.py               # Configuration management
│   ├── dependencies.py         # Dependency injection
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── router.py       # API router
│   │   │   └── endpoints/
│   │   │       ├── events.py
│   │   │       ├── aggregates.py
│   │   │       ├── validate.py
│   │   │       └── health.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── database.py         # SQLAlchemy models
│   │   └── schemas.py          # Pydantic schemas
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── event_service.py
│   │   ├── aggregate_service.py
│   │   ├── quota_service.py
│   │   └── cache_service.py
│   │
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── event_repository.py
│   │   ├── aggregate_repository.py
│   │   └── quota_repository.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── database.py         # DB connection
│   │   ├── redis.py            # Redis connection
│   │   ├── security.py         # API key validation
│   │   └── exceptions.py       # Custom exceptions
│   │
│   └── utils/
│       ├── __init__.py
│       └── time_utils.py       # Time window calculations
│
├── alembic/                    # Database migrations
│   ├── versions/
│   └── env.py
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
├── requirements.txt
├── Dockerfile
└── .env.example
```

### **4.2 Core Classes**

#### **4.2.1 EventService**

```python
class EventService:
    """Service for event ingestion and retrieval."""
    
    def __init__(
        self,
        event_repo: EventRepository,
        cache_service: CacheService,
        aggregate_service: AggregateService
    ):
        self.event_repo = event_repo
        self.cache_service = cache_service
        self.aggregate_service = aggregate_service
    
    async def ingest_event(self, event: EventCreate) -> Event:
        """Ingest a single event."""
        # 1. Validate event
        # 2. Save to PostgreSQL
        # 3. Update Redis counter
        # 4. Trigger async aggregation (if needed)
        # 5. Return event
    
    async def ingest_batch(self, events: List[EventCreate]) -> List[Event]:
        """Ingest multiple events in batch."""
        # Similar to ingest_event but with batch optimization
    
    async def get_events(
        self,
        filters: EventFilters,
        pagination: Pagination
    ) -> PaginatedResponse[Event]:
        """Retrieve events with filters and pagination."""
        # Query database with filters
        # Apply pagination
        # Return paginated response
```

#### **4.2.2 AggregateService**

```python
class AggregateService:
    """Service for computing and retrieving aggregates."""
    
    async def compute_aggregates(
        self,
        window_type: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[Aggregate]:
        """Compute aggregates for a time window."""
        # 1. Query raw events
        # 2. Group by tenant/resource/feature
        # 3. Compute totals
        # 4. Store in aggregates table
        # 5. Update Redis cache
    
    async def get_aggregates(
        self,
        filters: AggregateFilters,
        group_by: List[str]
    ) -> List[Aggregate]:
        """Retrieve pre-computed aggregates."""
        # 1. Check Redis cache
        # 2. If miss, query database
        # 3. If not found, compute on-the-fly
        # 4. Cache result
        # 5. Return aggregates
```

#### **4.2.3 QuotaService**

```python
class QuotaService:
    """Service for quota validation."""
    
    async def validate_quota(
        self,
        tenant_id: str,
        resource: str,
        feature: str,
        quantity: int,
        period: str
    ) -> QuotaValidationResult:
        """Validate if action is allowed within quota."""
        # 1. Load quota configuration
        # 2. Get current usage (from Redis or DB)
        # 3. Calculate remaining
        # 4. Check if allowed
        # 5. Return validation result
    
    async def get_usage(
        self,
        tenant_id: str,
        feature: str,
        period: str
    ) -> int:
        """Get current usage for a tenant/feature/period."""
        # 1. Check Redis counter
        # 2. If miss, query aggregates
        # 3. Return usage count
```

### **4.3 Pydantic Schemas**

```python
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, Dict, Any, List

class EventCreate(BaseModel):
    tenant_id: str = Field(..., min_length=1, max_length=255)
    resource: str = Field(..., min_length=1, max_length=255)
    feature: str = Field(..., min_length=1, max_length=255)
    quantity: int = Field(default=1, gt=0)
    timestamp: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

class EventBatchCreate(BaseModel):
    events: List[EventCreate] = Field(..., min_items=1, max_items=1000)

class Event(BaseModel):
    id: str
    tenant_id: str
    resource: str
    feature: str
    quantity: int
    timestamp: datetime
    metadata: Optional[Dict[str, Any]]
    created_at: datetime

class EventFilters(BaseModel):
    tenant_id: Optional[str] = None
    resource: Optional[str] = None
    feature: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class Pagination(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=50, ge=1, le=1000)

class QuotaValidationRequest(BaseModel):
    tenant_id: str
    resource: str
    feature: str
    quantity: int = Field(default=1, gt=0)
    period: str = Field(..., pattern="^(hourly|daily|monthly|yearly)$")

class QuotaValidationResult(BaseModel):
    allowed: bool
    remaining: int
    limit: int
    period: str
    reset_at: datetime
    current_usage: int
    message: Optional[str] = None
```

---

## **5. Metering Annotator Implementation**

### **5.1 Project Structure**

```
metering-annotator/
├── metering/
│   ├── __init__.py
│   ├── decorator.py           # @meter decorator
│   ├── middleware.py          # FastAPI/Flask middleware
│   ├── client.py              # HTTP client for API calls
│   ├── queue.py               # Local event queue
│   └── config.py              # Configuration
│
├── tests/
├── examples/
│   ├── decorator_example.py
│   └── middleware_example.py
│
├── setup.py
└── README.md
```

### **5.2 Decorator Implementation**

```python
from functools import wraps
from typing import Callable, Optional, Dict, Any
from metering.client import MeteringClient
from metering.queue import EventQueue

class Meter:
    """Metering decorator for function instrumentation."""
    
    def __init__(
        self,
        resource: str,
        feature: str,
        quantity: int = 1,
        tenant_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        transport: str = "async"  # "sync", "async", "batch"
    ):
        self.resource = resource
        self.feature = feature
        self.quantity = quantity
        self.tenant_id = tenant_id
        self.metadata = metadata or {}
        self.transport = transport
        self.client = MeteringClient()
        self.queue = EventQueue()
    
    def __call__(self, func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Execute function
            result = func(*args, **kwargs)
            
            # Record event
            self._record_event(result, args, kwargs)
            
            return result
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Execute async function
            result = await func(*args, **kwargs)
            
            # Record event
            await self._record_event_async(result, args, kwargs)
            
            return result
        
        # Return appropriate wrapper based on function type
        import inspect
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        return wrapper
    
    def _record_event(self, result, args, kwargs):
        """Record event synchronously."""
        if self.transport == "sync":
            self.client.record_event_sync(...)
        elif self.transport == "async":
            self.client.record_event_async(...)
        elif self.transport == "batch":
            self.queue.add_event(...)
    
    async def _record_event_async(self, result, args, kwargs):
        """Record event asynchronously."""
        # Similar implementation for async
```

### **5.3 Middleware Implementation (FastAPI)**

```python
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from metering.client import MeteringClient

class MeteringMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware for automatic API metering."""
    
    def __init__(self, app, api_url: str, api_key: str):
        super().__init__(app)
        self.client = MeteringClient(api_url=api_url, api_key=api_key)
    
    async def dispatch(self, request: Request, call_next):
        # Extract tenant_id from request (header, path, etc.)
        tenant_id = self._extract_tenant_id(request)
        
        # Extract resource/feature from route
        resource, feature = self._extract_resource_feature(request)
        
        # Process request
        response = await call_next(request)
        
        # Record event if successful
        if response.status_code < 400:
            await self.client.record_event_async(
                tenant_id=tenant_id,
                resource=resource,
                feature=feature,
                quantity=1
            )
        
        return response
```

### **5.4 Client Implementation**

```python
import aiohttp
import requests
from typing import Optional, Dict, Any, List
from tenacity import retry, stop_after_attempt, wait_exponential

class MeteringClient:
    """HTTP client for Metering Service API."""
    
    def __init__(
        self,
        api_url: str = "http://localhost:8000",
        api_key: Optional[str] = None,
        timeout: int = 5
    ):
        self.api_url = api_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.queue = EventQueue()
    
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
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Record event synchronously."""
        try:
            response = requests.post(
                f"{self.api_url}/v1/meter/events",
                json={
                    "tenant_id": tenant_id,
                    "resource": resource,
                    "feature": feature,
                    "quantity": quantity,
                    "metadata": metadata
                },
                headers={"X-API-Key": self.api_key},
                timeout=self.timeout
            )
            response.raise_for_status()
            return True
        except Exception as e:
            # Fallback to local queue
            self.queue.add_event(...)
            return False
    
    async def record_event_async(self, ...):
        """Record event asynchronously."""
        # Similar implementation with aiohttp
```

---

## **6. Frontend UI Implementation**

### **6.1 Project Structure**

```
metering-ui/
├── src/
│   ├── App.tsx
│   ├── main.tsx
│   │
│   ├── components/
│   │   ├── ui/              # shadcn components
│   │   ├── Dashboard.tsx
│   │   ├── TenantUsage.tsx
│   │   ├── EventsExplorer.tsx
│   │   └── ApiKeyManager.tsx
│   │
│   ├── pages/
│   │   ├── DashboardPage.tsx
│   │   ├── TenantPage.tsx
│   │   ├── EventsPage.tsx
│   │   └── SettingsPage.tsx
│   │
│   ├── services/
│   │   └── api.ts            # API client
│   │
│   ├── hooks/
│   │   ├── useMetering.ts
│   │   └── useQueries.ts
│   │
│   └── types/
│       └── index.ts
│
├── public/
├── package.json
└── vite.config.ts
```

### **6.2 API Client**

```typescript
// src/services/api.ts
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_KEY = import.meta.env.VITE_API_KEY || '';

const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/v1/meter`,
  headers: {
    'X-API-Key': API_KEY,
    'Content-Type': 'application/json',
  },
});

export const meteringApi = {
  getEvents: (params: EventFilters) =>
    apiClient.get('/events', { params }),
  
  getAggregates: (params: AggregateFilters) =>
    apiClient.get('/aggregates', { params }),
  
  validateQuota: (data: QuotaValidationRequest) =>
    apiClient.post('/validate', data),
};
```

---

## **7. Sequence Diagrams**

### **7.1 Event Ingestion Sequence**

```mermaid
sequenceDiagram
    participant Client
    participant Annotator
    participant API
    participant Postgres
    participant Redis
    participant Aggregator

    Client->>Annotator: Function call with @meter
    Annotator->>Annotator: Execute function
    Annotator->>API: POST /v1/meter/events
    API->>API: Validate API key
    API->>API: Validate payload
    API->>Postgres: INSERT event
    Postgres-->>API: Event saved
    API->>Redis: INCR counter
    Redis-->>API: Counter updated
    API-->>Annotator: 201 Created
    Annotator-->>Client: Function result
    API->>Aggregator: Trigger async aggregation (if needed)
```

### **7.2 Quota Validation Sequence**

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant Redis
    participant Postgres

    Client->>API: POST /v1/meter/validate
    API->>API: Validate API key
    API->>Redis: GET quota config
    alt Cache Hit
        Redis-->>API: Quota config
    else Cache Miss
        API->>Postgres: SELECT quota
        Postgres-->>API: Quota config
        API->>Redis: SET quota config (cache)
    end
    API->>Redis: GET current usage
    alt Counter Exists
        Redis-->>API: Usage count
    else Counter Missing
        API->>Postgres: SELECT aggregate
        Postgres-->>API: Usage count
        API->>Redis: SET counter (cache)
    end
    API->>API: Calculate remaining
    API->>API: Check if allowed
    API-->>Client: Validation result
```

---

## **8. Error Handling**

### **8.1 Error Codes**

| HTTP Code | Meaning | Example |
|-----------|---------|---------|
| 400 | Bad Request | Invalid JSON, missing required fields |
| 401 | Unauthorized | Invalid/missing API key |
| 422 | Unprocessable Entity | Validation errors (Pydantic) |
| 500 | Internal Server Error | Database connection failure |
| 503 | Service Unavailable | Redis unavailable, degraded mode |

### **8.2 Error Response Format**

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid tenant_id format",
    "details": {
      "field": "tenant_id",
      "reason": "Must be non-empty string"
    }
  }
}
```

---

## **9. Configuration Management**

### **9.1 Environment Variables**

**Metering Service:**
```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/metering
REDIS_URL=redis://localhost:6379/0

# API
API_HOST=0.0.0.0
API_PORT=8000
API_KEY_HASH_ALGORITHM=sha256

# Performance
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10
REDIS_POOL_SIZE=10

# Aggregation
AGGREGATION_BATCH_SIZE=1000
AGGREGATION_INTERVAL_SECONDS=300
```

**Metering Annotator:**
```python
# .env or config
METERING_API_URL=http://localhost:8000
METERING_API_KEY=your_api_key
METERING_TRANSPORT_MODE=async  # sync, async, batch
METERING_BATCH_SIZE=100
METERING_BATCH_INTERVAL_SECONDS=5
```

---

## **10. Testing Specifications**

### **10.1 Unit Tests**

**EventService Tests:**
- Test event ingestion (single)
- Test event ingestion (batch)
- Test event retrieval with filters
- Test pagination

**QuotaService Tests:**
- Test quota validation (allowed)
- Test quota validation (exceeded)
- Test usage calculation
- Test period boundaries

### **10.2 Integration Tests**

- Full API endpoint tests
- Database transaction tests
- Redis cache tests
- Error handling scenarios

### **10.3 Performance Tests**

- Load test: 1,000 events/sec
- Latency test: <200ms P95
- Cache hit rate: >80%

---

## **11. Deployment Configuration**

### **11.1 Docker Compose**

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:14
    environment:
      POSTGRES_DB: metering
      POSTGRES_USER: metering
      POSTGRES_PASSWORD: metering
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
  
  metering-api:
    build: ./services/api
    environment:
      DATABASE_URL: postgresql://metering:metering@postgres:5432/metering
      REDIS_URL: redis://redis:6379/0
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
  
  metering-ui:
    build: ./services/ui
    ports:
      - "3000:3000"
    environment:
      VITE_API_URL: http://localhost:8000
    depends_on:
      - metering-api

volumes:
  postgres_data:
  redis_data:
```

---

**Document Status:** Ready for Implementation  
**Next Steps:** Begin development of Metering Service API

