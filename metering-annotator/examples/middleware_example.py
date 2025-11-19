"""Example: Using FastAPI middleware."""

from fastapi import FastAPI
from metering.middleware import MeteringMiddleware

app = FastAPI()

# Add metering middleware
app.add_middleware(
    MeteringMiddleware,
    api_url="http://localhost:8000",
    api_key="your_api_key_here"
)


@app.get("/api/invoices/{invoice_id}")
async def get_invoice(invoice_id: str):
    """Get invoice by ID."""
    return {"invoice_id": invoice_id, "status": "paid"}


@app.post("/api/invoices")
async def create_invoice(data: dict):
    """Create a new invoice."""
    return {"invoice_id": "inv_123", "status": "created"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

