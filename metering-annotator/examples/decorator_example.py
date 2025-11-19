"""Example: Using @meter decorator."""

from metering import meter


@meter(resource="billing", feature="invoice_generate")
def generate_invoice(order_id: str, tenant_id: str):
    """Generate an invoice."""
    print(f"Generating invoice for order {order_id}")
    return {"invoice_id": "inv_123", "order_id": order_id}


@meter(resource="billing", feature="pdf_export", quantity=1)
def export_to_pdf(invoice_id: str):
    """Export invoice to PDF."""
    print(f"Exporting invoice {invoice_id} to PDF")
    return {"pdf_url": "https://example.com/invoice.pdf"}


if __name__ == "__main__":
    # Usage
    invoice = generate_invoice("order_123", "tenant_001")
    pdf = export_to_pdf(invoice["invoice_id"])

