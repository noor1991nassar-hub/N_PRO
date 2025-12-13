from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date

class InvoiceItemExtract(BaseModel):
    description: str = Field(..., description="Description of the line item")
    quantity: float = Field(..., description="Quantity of the item")
    unit_price: float = Field(..., description="Price per unit")
    total_price: float = Field(..., description="Total line price")
    category: Optional[str] = Field(None, description="Category of the item (e.g., Software, Hardware, Services)")

class InvoiceExtract(BaseModel):
    invoice_number: str = Field(..., description="The invoice number")
    invoice_date: Optional[str] = Field(None, description="Date of the invoice in YYYY-MM-DD format")
    vendor_name: str = Field(..., description="Name of the vendor/supplier")
    vendor_tax_id: Optional[str] = Field(None, description="Tax ID or VAT number of the vendor")
    total_amount: float = Field(..., description="Total amount of the invoice")
    currency: str = Field("SAR", description="Currency code (e.g., SAR, USD)")
    items: List[InvoiceItemExtract] = Field(default_factory=list, description="List of line items")
