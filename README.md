# Dynamic API-Driven Metering Framework

A comprehensive metering solution for tracking, measuring, and monitoring usage of modules, features, and APIs in real-time.

## Project Structure

```
metering/
├── services/
│   ├── api/          # FastAPI backend service
│   └── ui/           # React frontend dashboard
├── metering-annotator/  # Python integration library
├── BRD.md            # Business Requirements Document
├── HLD.md            # High-Level Design
├── LLD.md            # Low-Level Design
└── docker-compose.yml # Docker Compose configuration
```

## Quick Start

### Prerequisites

- **For Docker**: Docker and Docker Compose
- **For Local**: Python 3.11+, Node.js 18+, PostgreSQL 14+, Redis 6+

### Option 1: Local Development (Recommended for Development)

See **[LOCAL_SETUP.md](LOCAL_SETUP.md)** for detailed local setup instructions.

**Quick Start:**
1. Install PostgreSQL and Redis
2. Set up database: `createdb metering`
3. Start API: `cd services/api && uvicorn app.main:app --reload`
4. Start UI: `cd services/ui && npm run dev`
5. Create API key: `python3 services/api/create_api_key.py`

### Option 2: Docker Compose

1. Clone the repository:
```bash
git clone <repository-url>
cd metering
```

2. Start all services:
```bash
docker-compose up -d
```

3. Access the services:
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- UI: http://localhost:3000

## Components

### 1. Metering Service (API)

FastAPI-based REST API for:
- Event ingestion (single and batch)
- Event querying with filters
- Usage aggregation
- Quota validation

**Documentation:** See `services/api/README.md`

### 2. Metering Annotator

Python library for easy integration:
- `@meter` decorator for function instrumentation
- Middleware for FastAPI/Flask
- Automatic event tracking

**Documentation:** See `metering-annotator/README.md`

### 3. Frontend UI

React dashboard for:
- Usage visualization
- Tenant analytics
- Events explorer
- Settings management

**Documentation:** See `services/ui/README.md`

## API Endpoints

- `POST /v1/meter/events` - Ingest events
- `GET /v1/meter/events` - Query events
- `GET /v1/meter/aggregates` - Get usage aggregates
- `POST /v1/meter/validate` - Validate quota
- `GET /v1/meter/health` - Health check

See API documentation at http://localhost:8000/docs

## Usage Examples

### Using the Decorator

```python
from metering import meter

@meter(resource="billing", feature="invoice_generate")
def generate_invoice(order_id: str, tenant_id: str):
    # Your function logic
    return invoice
```

### Using Middleware

```python
from fastapi import FastAPI
from metering.middleware import MeteringMiddleware

app = FastAPI()
app.add_middleware(MeteringMiddleware, api_url="http://localhost:8000", api_key="your_key")
```

## Configuration

See `.env.example` files in each service directory for configuration options.

## Documentation

- **LOCAL_SETUP.md** - Detailed local development setup guide
- **BRD.md** - Business Requirements Document
- **HLD.md** - High-Level Design
- **LLD.md** - Low-Level Design
- **PROJECT_STRUCTURE.md** - Project structure definition

## License

See LICENSE file for details.

## Contributing

1. Review the BRD, HLD, and LLD documents
2. Follow the project structure
3. Write tests for new features
4. Update documentation as needed

