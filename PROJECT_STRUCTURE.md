# **Project Structure Definition**

This document defines the complete directory structure for the Dynamic API-Driven Metering Framework.

---

## **Root Structure**

```
metering/
├── BRD.md
├── HLD.md
├── LLD.md
├── PROJECT_STRUCTURE.md
├── README.md
├── LICENSE
├── .gitignore
├── docker-compose.yml
│
├── services/
│   ├── api/                    # Metering Service (FastAPI)
│   └── ui/                     # React Frontend
│
├── metering-annotator/         # Python Integration Library
│
└── docs/                       # Additional documentation
```

---

## **1. Metering Service (API) Structure**

```
services/api/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration management (Pydantic Settings)
│   ├── dependencies.py         # Dependency injection (API key validation, DB sessions)
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── router.py       # Main API router that combines all endpoints
│   │   │   └── endpoints/
│   │   │       ├── __init__.py
│   │   │       ├── events.py   # POST/GET /v1/meter/events
│   │   │       ├── aggregates.py  # GET /v1/meter/aggregates
│   │   │       ├── validate.py    # POST /v1/meter/validate
│   │   │       └── health.py      # GET /v1/meter/health
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── database.py         # SQLAlchemy ORM models
│   │   └── schemas.py          # Pydantic request/response schemas
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── event_service.py    # Business logic for event ingestion/retrieval
│   │   ├── aggregate_service.py # Business logic for aggregation
│   │   ├── quota_service.py    # Business logic for quota validation
│   │   └── cache_service.py    # Redis cache operations
│   │
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── event_repository.py # Database operations for events
│   │   ├── aggregate_repository.py # Database operations for aggregates
│   │   └── quota_repository.py # Database operations for quotas
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── database.py         # Database connection and session management
│   │   ├── redis.py            # Redis connection and client
│   │   ├── security.py         # API key validation and hashing
│   │   └── exceptions.py       # Custom exception classes
│   │
│   └── utils/
│       ├── __init__.py
│       └── time_utils.py       # Time window calculations (hourly/daily/monthly)
│
├── alembic/                    # Database migrations
│   ├── versions/
│   │   └── .gitkeep
│   ├── env.py
│   └── script.py.mako
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # Pytest fixtures
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_event_service.py
│   │   ├── test_aggregate_service.py
│   │   └── test_quota_service.py
│   ├── integration/
│   │   ├── __init__.py
│   │   ├── test_events_api.py
│   │   ├── test_aggregates_api.py
│   │   └── test_validate_api.py
│   └── e2e/
│       ├── __init__.py
│       └── test_full_flow.py
│
├── requirements.txt            # Python dependencies
├── requirements-dev.txt        # Development dependencies
├── Dockerfile                  # Container definition
├── .env.example                # Environment variables template
├── .dockerignore
└── README.md                   # Service-specific documentation
```

---

## **2. Metering Annotator Structure**

```
metering-annotator/
├── metering/
│   ├── __init__.py             # Package initialization, exports main classes
│   ├── decorator.py             # @meter decorator implementation
│   ├── middleware.py            # FastAPI/Flask/Starlette middleware
│   ├── client.py                # HTTP client for API calls (sync/async)
│   ├── queue.py                 # Local event queue for offline buffering
│   ├── config.py                # Configuration management
│   └── exceptions.py            # Custom exceptions
│
├── tests/
│   ├── __init__.py
│   ├── test_decorator.py
│   ├── test_middleware.py
│   ├── test_client.py
│   └── test_queue.py
│
├── examples/
│   ├── decorator_example.py     # Example: Using @meter decorator
│   ├── middleware_example.py    # Example: Using FastAPI middleware
│   ├── flask_example.py         # Example: Using Flask middleware
│   └── async_example.py         # Example: Async usage patterns
│
├── setup.py                     # Python package setup
├── pyproject.toml               # Modern Python packaging
├── requirements.txt
├── requirements-dev.txt
├── .env.example
├── README.md                    # Library documentation
└── LICENSE
```

---

## **3. Frontend UI Structure**

```
services/ui/
├── public/
│   ├── favicon.ico
│   └── index.html
│
├── src/
│   ├── main.tsx                 # React app entry point
│   ├── App.tsx                  # Root component with routing
│   ├── index.css                # Global styles, Tailwind imports
│   │
│   ├── components/
│   │   ├── ui/                  # shadcn/ui components (auto-generated)
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── table.tsx
│   │   │   ├── input.tsx
│   │   │   ├── select.tsx
│   │   │   ├── dialog.tsx
│   │   │   └── ...
│   │   │
│   │   ├── layout/
│   │   │   ├── Layout.tsx       # Main layout wrapper
│   │   │   ├── Header.tsx       # Top navigation
│   │   │   ├── Sidebar.tsx      # Side navigation (if needed)
│   │   │   └── Footer.tsx       # Footer component
│   │   │
│   │   ├── Dashboard.tsx        # Dashboard page components
│   │   ├── TenantUsage.tsx      # Tenant usage components
│   │   ├── EventsExplorer.tsx   # Events table and filters
│   │   └── ApiKeyManager.tsx    # API key management UI
│   │
│   ├── pages/
│   │   ├── DashboardPage.tsx    # Main dashboard page
│   │   ├── TenantPage.tsx       # Tenant usage page
│   │   ├── EventsPage.tsx       # Events explorer page
│   │   └── SettingsPage.tsx     # Settings/API keys page
│   │
│   ├── services/
│   │   ├── api.ts               # Axios client and API methods
│   │   └── types.ts             # TypeScript type definitions
│   │
│   ├── hooks/
│   │   ├── useMetering.ts       # Custom hook for metering data
│   │   ├── useQueries.ts        # React Query hooks
│   │   └── useApiKey.ts         # API key management hook
│   │
│   ├── types/
│   │   └── index.ts             # Shared TypeScript interfaces
│   │
│   ├── utils/
│   │   ├── formatters.ts        # Date/number formatters
│   │   └── constants.ts         # App constants
│   │
│   └── lib/
│       └── utils.ts             # Utility functions (cn, etc.)
│
├── .env.example
├── .env.local.example
├── package.json
├── package-lock.json
├── tsconfig.json                # TypeScript configuration
├── tsconfig.node.json
├── vite.config.ts               # Vite configuration
├── tailwind.config.js           # Tailwind CSS configuration
├── postcss.config.js            # PostCSS configuration
├── components.json              # shadcn/ui configuration
├── Dockerfile
├── .dockerignore
└── README.md
```

---

## **4. Root Configuration Files**

```
metering/
├── docker-compose.yml           # Multi-service Docker Compose
├── .gitignore                   # Git ignore rules
├── .env.example                 # Root environment template
└── README.md                    # Main project README
```

---

## **5. Documentation Structure**

```
docs/
├── api/                         # API documentation
│   ├── openapi.yaml             # OpenAPI/Swagger specification
│   └── examples.md              # API usage examples
│
├── integration/                 # Integration guides
│   ├── python-decorator.md      # Decorator usage guide
│   ├── python-middleware.md     # Middleware usage guide
│   └── http-api.md              # Direct HTTP API usage
│
├── deployment/                  # Deployment guides
│   ├── docker.md                # Docker deployment
│   ├── development.md           # Local development setup
│   └── production.md            # Production deployment (future)
│
└── architecture/                # Architecture diagrams
    └── diagrams.md              # Additional diagrams
```

---

## **6. File Descriptions**

### **API Service Key Files**

| File | Purpose |
|------|---------|
| `app/main.py` | FastAPI app initialization, middleware setup, route registration |
| `app/config.py` | Environment variable loading, settings validation |
| `app/dependencies.py` | FastAPI dependencies (DB session, API key validation) |
| `app/models/database.py` | SQLAlchemy ORM models (Event, Aggregate, Quota, APIKey) |
| `app/models/schemas.py` | Pydantic models for request/response validation |
| `app/services/event_service.py` | Business logic for event operations |
| `app/services/quota_service.py` | Quota validation and usage calculation |
| `app/core/database.py` | Database connection, session factory |
| `app/core/redis.py` | Redis client initialization and connection pooling |

### **Annotator Key Files**

| File | Purpose |
|------|---------|
| `metering/decorator.py` | `@meter` decorator class implementation |
| `metering/middleware.py` | FastAPI/Flask middleware classes |
| `metering/client.py` | HTTP client with sync/async support, retry logic |
| `metering/queue.py` | In-memory event queue for offline buffering |
| `metering/config.py` | Configuration loading from env vars |

### **UI Key Files**

| File | Purpose |
|------|---------|
| `src/App.tsx` | React Router setup, route definitions |
| `src/services/api.ts` | Axios client, API method wrappers |
| `src/pages/DashboardPage.tsx` | Main dashboard with charts and summary cards |
| `src/components/Dashboard.tsx` | Dashboard-specific components (charts, cards) |
| `src/hooks/useMetering.ts` | Custom React hooks for data fetching |

---

## **7. Technology Versions**

### **Backend (API Service)**
- Python: 3.11+
- FastAPI: 0.104+
- SQLAlchemy: 2.0+
- PostgreSQL: 14+
- Redis: 6+
- Alembic: 1.12+

### **Annotator**
- Python: 3.8+
- requests: 2.31+
- aiohttp: 3.9+ (optional, for async)
- tenacity: 8.2+ (retry logic)

### **Frontend (UI)**
- Node.js: 18+
- React: 18.2+
- TypeScript: 5.0+
- Vite: 5.0+
- TailwindCSS: 3.3+
- shadcn/ui: Latest
- Recharts: 2.8+
- React Query (TanStack Query): 5.0+
- Axios: 1.6+

---

## **8. Environment Variables**

### **API Service (.env)**
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

# Logging
LOG_LEVEL=INFO
```

### **Annotator (.env)**
```bash
METERING_API_URL=http://localhost:8000
METERING_API_KEY=your_api_key_here
METERING_TRANSPORT_MODE=async
METERING_BATCH_SIZE=100
METERING_BATCH_INTERVAL_SECONDS=5
METERING_RETRY_MAX_ATTEMPTS=3
```

### **UI (.env)**
```bash
VITE_API_URL=http://localhost:8000
VITE_API_KEY=your_api_key_here
```

---

## **9. Docker Services**

### **docker-compose.yml Services**
1. **postgres** - PostgreSQL database
2. **redis** - Redis cache
3. **metering-api** - FastAPI service
4. **metering-ui** - React frontend (dev server or built)

---

## **10. Initial Setup Checklist**

- [ ] Create directory structure
- [ ] Initialize Python projects (API, Annotator)
- [ ] Initialize React project (UI)
- [ ] Set up Docker Compose
- [ ] Create database migrations
- [ ] Implement core API endpoints
- [ ] Implement decorator and middleware
- [ ] Build UI components
- [ ] Write initial tests
- [ ] Create documentation

---

**Status:** Structure Definition Complete  
**Next Step:** Begin scaffolding files based on this structure

