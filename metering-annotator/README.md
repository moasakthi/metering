# Metering Annotator

Python integration library for the Metering Service. Provides decorators and middleware for easy integration.

## Installation

```bash
pip install -r requirements.txt
```

Or install in development mode:
```bash
pip install -e .
```

## Usage

### Decorator

```python
from metering import meter

@meter(resource="billing", feature="invoice_generate")
def generate_invoice(order_id: str, tenant_id: str):
    # Your function logic
    return invoice
```

### Middleware (FastAPI)

```python
from fastapi import FastAPI
from metering.middleware import MeteringMiddleware

app = FastAPI()
app.add_middleware(MeteringMiddleware, api_url="http://localhost:8000", api_key="your_key")
```

## Configuration

Set environment variables or use `.env` file:
- `METERING_API_URL`: API endpoint URL
- `METERING_API_KEY`: API key for authentication
- `METERING_TRANSPORT_MODE`: `sync`, `async`, or `batch`

See `.env.example` for all options.

